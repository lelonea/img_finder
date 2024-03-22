from django.contrib import admin
from img_app.models import ImageModel, Keyword, LookupBucket


class ImageAdmin(admin.ModelAdmin):
    list_display = ['object_key', 'object_url']


class KeywordAdmin(admin.ModelAdmin):
    list_display = ['keyword']


class LookupBucketAdmin(admin.ModelAdmin):
    list_display = ['bucket_name', 'region_name']


admin.site.register(LookupBucket, LookupBucketAdmin)
admin.site.register(ImageModel, ImageAdmin)
admin.site.register(Keyword, KeywordAdmin)
