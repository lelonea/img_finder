from django.db import models


class Keyword(models.Model):
    keyword = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.keyword


class ImageModel(models.Model):
    object_key = models.CharField(max_length=500, unique=True)
    object_url = models.URLField(unique=True)
    keywords = models.ManyToManyField(Keyword, related_name="images")

    def __str__(self):
        return self.object_key


class LookupBucket(models.Model):
    bucket_name = models.CharField(max_length=100, unique=True)
    region_name = models.CharField(max_length=100, blank=True)
    prefix = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('bucket_name', 'prefix')

    def __str__(self):
        return f"{self.bucket_name} ({self.region_name})"
