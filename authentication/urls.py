from django.urls import path, include
from rest_framework import routers
from authentication import views

router = routers.DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("certificate/", views.generate_certificate),
    path('token/', views.get_token)
]
