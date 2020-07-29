from django.urls import include, path


urlpatterns = [
    path("v1/", include('wallet.api.v1.urls')),
]