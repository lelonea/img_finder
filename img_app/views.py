import os
import logging
from fuzzywuzzy import process
from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from img_app.models import ImageModel, Keyword, LookupBucket
from django.http import JsonResponse
from img_app.serializers import S3RequestSerializer, ImageModelSerializer, ImageKeywordSerializer
from img_app.tasks import process_images
from img_app.helpers.api_helper import find_new_images_in_bucket


class InitialParseView(generics.CreateAPIView):
    serializer_class = S3RequestSerializer
    response_serializer_class = ImageModelSerializer
    permission_classes = [AllowAny]
    queryset = ImageModel.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        bucket_name = validated_data.get('bucket_name')
        prefix = validated_data.get('prefix', '')
        region_name = validated_data.get('region_name', os.environ.get('AWS_DEFAULT_REGION'))
        created_instances = find_new_images_in_bucket(bucket_name, prefix, region_name)
        lookup_buckets = LookupBucket.objects.all()
        if not lookup_buckets.filter(bucket_name=bucket_name, prefix=prefix).exists():
            try:
                LookupBucket.objects.create(bucket_name=bucket_name, prefix=prefix, region_name=region_name)
            except Exception as e:
                logging.exception(f"Could not create LookupBucket: {e}")
        images_urls = [instance.object_url for instance in created_instances]
        process_images.delay(images_urls)
        response_serializer = self.response_serializer_class(created_instances, many=True)
        return JsonResponse(response_serializer.data, safe=False)


class GetKeywordsByImageView(ListAPIView):
    serializer_class = ImageKeywordSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        try:
            image_instance = ImageModel.objects.get(object_url=self.image_url)
            return image_instance
        except ImageModel.DoesNotExist:
            return ImageModel.objects.none()

    def list(self, request, *args, **kwargs):
        self.image_url = self.request.query_params.get('url')
        if not self.image_url:
            return JsonResponse({'error': 'No image URL provided'}, status=400)
        queryset = self.get_queryset()
        if not queryset:
            return JsonResponse({'error': 'Image not found'}, status=404)
        serializer = self.get_serializer(queryset)
        return JsonResponse({'keywords': serializer.data}, status=200)


class SearchImagesView(ListAPIView):
    serializer_class = ImageModelSerializer

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if not keyword:
            return []
        keywords = Keyword.objects.all()
        # Finds all matches above a certain match score threshold
        matched_keywords = process.extractBests(keyword.lower(), [kw.keyword for kw in keywords], score_cutoff=60)
        matched_keyword_names = [match[0] for match in matched_keywords]
        matched_keyword_objects = Keyword.objects.filter(keyword__in=matched_keyword_names)
        images = set()
        for keyword in matched_keyword_objects:
            images.update(keyword.images.all())
        return list(images)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return JsonResponse({'error': 'Keyword matching images not found'}, status=404)
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse({'images': serializer.data}, status=200)
