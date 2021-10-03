from django.urls import path

from . import views

app_name = "backend"

urlpatterns = [
    path('', views.Register.as_view(), name="register"),
    path('accounts/login', views.login_view, name="login"),
    path('accounts/register', views.Register.as_view(), name="register"),
    path('stocks/list', views.StockList.as_view(), name="StockList"),
    path('stocks/buy', views.BuyStock.as_view(), name="buy"),
    path('stocks/sell', views.SellStock.as_view(), name="sell")
]
