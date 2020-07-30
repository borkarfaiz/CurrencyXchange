from django.urls import include, path

urlpatterns = [
    path("user/", include("users.api.urls")),
    path("currency-converter/", include("currency_converter.api.urls")),
    path("wallet/", include("wallet.api.urls")),
    path("analytics/", include("analytics.api.urls"))
]