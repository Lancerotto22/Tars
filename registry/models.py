from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "people"


class Place(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    address = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=20)
    country_code = models.CharField(max_length=2)
    notes = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.address}, {self.city} ({self.zip_code}), {self.province} ({self.country_code})"

    class Meta:
        verbose_name_plural = "places"


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50)
    vat = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=30, unique=True)
    lang = models.CharField(max_length=30, default="italian", help_text="mother tongue of the customer")
    company = models.ForeignKey(Company, on_delete=models.RESTRICT, related_name="+")
    hq_place = models.ForeignKey(Place, on_delete=models.RESTRICT, related_name="+", null=True, blank=True, help_text="* head office")
    bu_place = models.ForeignKey(Place, on_delete=models.RESTRICT, related_name="+", null=True, blank=True, help_text="operative office")
    team_leader = models.ForeignKey(Person, on_delete=models.RESTRICT, related_name="+", null=True, blank=True, help_text="* person who has to sign technical offer")
    purchase_manager = models.ForeignKey(Person, on_delete=models.RESTRICT, related_name="+", null=True, blank=True, help_text="* person who has to sign commercial offer")
    engineering_director = models.ForeignKey(Person, on_delete=models.RESTRICT, related_name="+", null=True, blank=True, help_text="")
    marketing_director = models.ForeignKey(Person, on_delete=models.RESTRICT, related_name="+", null=True, blank=True, help_text="")

    def __str__(self):
        return self.name


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT)
    name = models.CharField(max_length=30)
    number_of_deliverables = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.name}@{self.customer.name}"

    class Meta:
        unique_together = ("customer", "name")


class ProjectMembership(models.Model):
    class ProjectMembershipRole(models.TextChoices):
        ADMIN = "ADMIN"
        DEVELOPER = "DEVELOPER"
        CUSTOMER = "CUSTOMER"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=30, choices=ProjectMembershipRole)

    def __str__(self):
        return f"{self.user.email} {self.role} in {self.project}"

    class Meta:
        unique_together = ("project", "user")
        

# Inizio aggiunte classi per funzioni con deliverables-----

class Deliverable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=30)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="deliverables") 
    repository = models.URLField(max_length=100)

    # Campi aggiunti
    production_version = models.CharField(max_length=255, null=True, blank=True)
    production_last_published_at = models.DateTimeField(null=True, blank=True)
    production_download_uri = models.URLField(null=True, blank=True)
    
    staging_version = models.CharField(max_length=255, null=True, blank=True)
    staging_last_published_at = models.DateTimeField(null=True, blank=True)
    staging_download_uri = models.URLField(null=True, blank=True)
    
    delivery_version = models.CharField(max_length=255, null=True, blank=True)
    delivery_last_published_at = models.DateTimeField(null=True, blank=True)
    delivery_download_uri = models.URLField(null=True, blank=True)

    last_build_event_id = models.CharField(max_length=255, null=True, blank=True)
    last_build_outcome = models.CharField(max_length=100, null=True, blank=True)
    last_build_timestamp = models.DateTimeField(null=True, blank=True)
    last_build_stage = models.CharField(max_length=100, null=True, blank=True)
    last_build_version = models.CharField(max_length=100, null=True, blank=True)

    source_code_uri = models.URLField(null=True, blank=True)
    external_ref = models.CharField(max_length=255, null=True, blank=True)
    external_ref_uri = models.URLField(null=True, blank=True)

    # AGGIUNTA PER TESTING
    stage_status = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.name} in {self.project}"

    class Meta:
        unique_together = ("name", "project")

## TESTING ##
class Event(models.Model):
    # Relazioni
    deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE, related_name="events")
    
    # Attributi dell'evento
    id = models.CharField(max_length=255, primary_key=True)  # Assumiamo che l'ID sia un identificatore unico
    outcome = models.CharField(max_length=50)  # Successo, errore, ecc.
    timestamp = models.DateTimeField(default=timezone.now)  # Tempo dell'evento
    type = models.CharField(max_length=50)  # Tipo di evento (ad esempio, build, deploy, ecc.)
    stage = models.CharField(max_length=50)  # Fase in cui è avvenuto l'evento (es. delivery, testing)
    version = models.CharField(max_length=50)  # Versione del deliverable
    source_code_uri = models.URLField(max_length=200)  # URL del codice sorgente relativo all'evento
    external_ref = models.CharField(max_length=255, blank=True, null=True)  # Riferimento esterno opzionale
    external_ref_uri = models.URLField(max_length=200, blank=True, null=True)  # URL del riferimento esterno

    def __str__(self):
        return f"{self.type} event for {self.deliverable.name} ({self.timestamp})" 
# Fine aggiunte -----


class Billing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    alias = models.CharField(max_length=30)
    description = models.JSONField()

    def __str__(self):
        return f"{self.alias}"


class Plan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    unit = models.PositiveIntegerField()
    creation = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=20)
    category = models.JSONField()
    discounts = models.JSONField()

    def __str__(self):
        return f"{self.name}"


class MembershipType(models.Model):
    name = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return self.name


class Portfolio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=20)
    brand = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Membership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    of = models.OneToOneField(Customer, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.RESTRICT)
    plan = models.ForeignKey(Plan, on_delete=models.RESTRICT, related_name="members")
    membership = models.ForeignKey(MembershipType, on_delete=models.RESTRICT)
    billing = models.ForeignKey(Billing, on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.of} membership"


class Context(models.Model):
    key = models.CharField(max_length=100, primary_key=True)
    value = models.JSONField()

    def __str__(self):
        return self.key


