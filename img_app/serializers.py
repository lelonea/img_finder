from rest_framework import serializers
from img_app.models import ImageModel


class S3RequestSerializer(serializers.Serializer):
    bucket_name = serializers.CharField()
    prefix = serializers.CharField(required=False, allow_blank=True)
    region_name = serializers.CharField(required=False, allow_blank=True)


class ImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = [
            "object_key",
            "object_url",
        ]


class ImageKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ['keywords']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        keywords_query = instance.keywords.all()
        representation['keywords'] = [keyword.keyword for keyword in keywords_query]
        return representation
