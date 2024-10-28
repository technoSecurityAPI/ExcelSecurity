from django.urls import path
from .views import check_user_access

urlpatterns = [
    path('check_access/', check_user_access),
]
