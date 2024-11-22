import logging

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from registry.serializers import (
    BillingSerializer,
    ContextSerializer,
    CustomerSerializer,
    MembershipSerializer,
    PlaceSerializer,
    PlanSerializer,
    PersonSerializer,
)
from registry.models import (
    Context,
    Customer,
    Place,
    Person,
    Billing,
    Plan,
    Membership,
)

log = logging.getLogger(__name__)

class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer


class BillingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer


class MembershipViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer


class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "name"
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    

class ContextViewSet(viewsets.ModelViewSet):
    queryset = Context.objects.all()
    serializer_class = ContextSerializer
    pagination_class = PageNumberPagination
