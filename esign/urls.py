from django.urls import path

from esign import views

urlpatterns = [
    path("upload", views.upload_pdf),
]
