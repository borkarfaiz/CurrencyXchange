from django.urls import include, path


urlpatterns = [
    path("v1/", include('analytics.api.v1.urls')),
]