from django.urls import include, path

urlpatterns = [
    # API base url
    path("user/", include("users.api.urls")),
    # DRF auth token
]

