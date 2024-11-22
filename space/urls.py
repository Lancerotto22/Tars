from django.urls import path, include

from rest_framework import routers
from space import views


router = routers.DefaultRouter()


urlpatterns = [
    path("", include(router.urls)),
    path('api/v1/auth/user/', views.auth_user),
    path('api/v1/auth/login/', views.auth_login),
    path('api/v1/auth/logout/', views.auth_logout),
    path('api/v1/customers/', views.get_customers),
    path('api/v1/customers/<str:customer>/', views.get_customer_by_name),
    path('api/v1/customers/<str:customer_name>/projects/<str:project_name>/', views.get_project_details),
    path('api/v1/customers/<str:customer_name>/projects/<str:project_name>/deliverables/<str:deliverable_name>/', views.get_deliverable_details),
    path('api/v1/deliverables/', views.get_all_deliverables),
    path('api/v1/customers/<str:customer>/projects/<str:project>/deliverables/<str:deliverable>/configurations/<str:stage>/', views.stage_status),
    

    ## TESTING ##
    path('api/v1/customers/<str:customer>/projects/<str:project>/deliverables/<str:deliverable>/events/', views.get_deliverable_events),
    path('api/v1/customers/<str:customer>/projects/<str:project>/deliverables/<str:deliverable>/publish/', views.publish_deliverable),
    
]

