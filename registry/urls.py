from django.urls import path, include

from rest_framework import routers

from registry import views

router = routers.DefaultRouter()
router.register("places", views.PlaceViewSet)
router.register("people", views.PersonViewSet)
router.register("billings", views.BillingViewSet)
router.register("plans", views.PlanViewSet)
router.register("membership", views.MembershipViewSet)
router.register("context", views.ContextViewSet)
router.register("customers", views.CustomerViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
