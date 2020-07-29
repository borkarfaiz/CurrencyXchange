from django.urls import include, path

urlpatterns = [
    path("user/", include("users.api.urls")),
    path("currency_converter/", include("currency_converter.api.urls")),
    path("wallet/", include("wallet.api.urls"))
]

