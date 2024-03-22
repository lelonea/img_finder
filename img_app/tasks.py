import logging

from celery import group, chord

from img_app.helpers.api_helper import find_new_images_in_bucket
from img_finder.celery import app
from img_app.helpers import openai_helper
from img_app.models import ImageModel, Keyword, LookupBucket
from img_app.helpers.aws_util import list_s3_objects


@app.task
def generate_image_search_keywords(image_url):
    keywords = openai_helper.generate_image_search_keywords(image_url)
    return image_url, keywords


@app.task
def on_all_keywords_generated(results):
    """
    Callback task to process keywords once they're generated.
    results: List of tuples, each containing (image_url, keywords list).
    """
    logging.info("All tasks completed. Processing results...")

    for image_url, keywords in results:
        try:
            image_instance = ImageModel.objects.get(object_url=image_url)
            for keyword_str in keywords:
                for kw in keyword_str.replace('-', '').split(','):
                    kw = kw.strip().lower()
                    if kw:
                        keyword, created = Keyword.objects.get_or_create(keyword=kw.lower())
                        image_instance.keywords.add(keyword)
                        logging.info(f'Keyword "{kw}" processed and linked to image "{image_url}".')
        except ImageModel.DoesNotExist:
            logging.exception(f"ImageModel instance for URL '{image_url}' not found.")

    logging.info("Results processed.")


@app.task(bind=True)
def process_images(self, image_urls):
    """
    Process multiple images in parallel and handle their keywords.
    image_urls: a list of image URLs to process.
    """
    task_group = group(generate_image_search_keywords.s(image_url) for image_url in image_urls)
    callback_task = on_all_keywords_generated.s()
    chord(task_group)(callback_task)


@app.task
def periodic_image_search():
    logging.info("Looking for new images and generating keywords...")
    lookup_buckets = LookupBucket.objects.all()
    for lookup_bucket in lookup_buckets:
        bucket_name = lookup_bucket.bucket_name
        new_created_instances = find_new_images_in_bucket(bucket_name, lookup_bucket.prefix, lookup_bucket.region_name)
        logging.info(f"Found {len(new_created_instances)} new images in lookup bucket {bucket_name}")
        if new_created_instances:
            images_urls = [instance.object_url for instance in new_created_instances]
            process_images.delay(images_urls)
