from img_app.helpers.aws_util import list_s3_objects
from img_app.models import ImageModel


def find_new_images_in_bucket(bucket_name, prefix, region_name):
    objects = list_s3_objects(bucket_name, prefix, region_name)
    new_image_instances = []
    existing_object_keys = ImageModel.objects.values_list('object_key', flat=True)
    for obj in objects:
        if obj['key'] not in existing_object_keys:
            new_image_instances.append(ImageModel(
                object_key=obj['key'],
                object_url=obj['url']
            ))
    created_instances = ImageModel.objects.bulk_create(new_image_instances)
    return created_instances
