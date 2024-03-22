from django.urls import path
from img_app.views import InitialParseView, GetKeywordsByImageView, SearchImagesView

urlpatterns = [
    path('parse/', InitialParseView.as_view(), name='initial_parse'),
    path('get-keywords/', GetKeywordsByImageView.as_view(), name='get_keywords_by_image_url'),
    path('get-images/', SearchImagesView.as_view(), name='get_images_by_keyword'),
]
