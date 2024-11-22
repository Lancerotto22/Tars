from django.contrib import admin
from registry.models import (
    Person,
    Place,
    Billing,
    Plan,
    Membership,
    MembershipType,
    Portfolio,
    Customer,
    Project,
    Deliverable,
    ProjectMembership,
    Company,
)
from rest_framework.authtoken.models import TokenProxy

# avoid showing tokens for all users
admin.site.unregister(TokenProxy)

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    search_fields = ["address", "city", "zip_code", "province", "country_code"]
    list_display = ["address", "city", "zip_code", "province", "country_code"]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ["name", "email", "phone"]
    list_display = ["name", "email", "phone"]
    readonly_fields = ["id"]


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = ["name", "vat", "email", "phone"]
    list_display = ["name", "vat", "email"]
    readonly_fields = ["id"]


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ["alias"]


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(MembershipType)
class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ["name"]


class MembershipAdmin(admin.StackedInline):
    model = Membership


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ["brand", "name"]
    readonly_fields = ["id"]
    

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    inlines = [MembershipAdmin]
    list_display = ["name", "lang", "company", "team_leader", "purchase_manager"]
    search_fields = ["name", "lang", "company", "team_leader", "purchase_manager"]


class InlineProjectMembership(admin.TabularInline):
    model = ProjectMembership
    extra = 0
    readonly_fields = ["id"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [InlineProjectMembership]
    list_display = ["name", "customer"]
    search_fields = ["name", "customer"]
    list_filter = ["customer"]


@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "repository"]
    search_fields = ["name", "project"]
    list_filter = ["project"]
