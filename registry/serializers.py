from rest_framework import serializers

from registry.models import (
    Person,
    Place,
    Billing,
    Plan,
    Membership,
    Portfolio,
    Context,
    Customer,
    Project,
    Company,
)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = "__all__"


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = "__all__"


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = "__all__"


class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = "__all__"


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"


class MembershipSerializer(serializers.ModelSerializer):
    membership = serializers.SlugRelatedField(slug_field="name", read_only=True)
    plan = PlanSerializer(read_only=True)
    billing = BillingSerializer(read_only=True)
    portfolio = PortfolioSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    hq_place = PlaceSerializer(read_only=True)
    bu_place = PlaceSerializer(read_only=True)
    team_leader = PersonSerializer(read_only=True)    
    purchase_manager = PersonSerializer(read_only=True)
    engineering_director = PersonSerializer(read_only=True)
    marketing_director = PersonSerializer(read_only=True)
    membership = MembershipSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Project
        fields = "__all__"


class ContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Context
        fields = "__all__"
