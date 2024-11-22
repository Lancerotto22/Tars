from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection

import requests

from requests.auth import HTTPBasicAuth

from registry.models import (
    Person,
    PersonRole,
    Place,
    PlaceRole,
    RoleType,
    Membership,
    MembershipType,
    Billing,
    Plan,
    PersonAlias,
    Portfolio,
    PortfolioAlias
)

TABLES = [
    "registry_personalias",
    "registry_billing",
    "registry_membership",
    "registry_membershiptype",
    "registry_person",
    "registry_personrole",
    "registry_place",
    "registry_placerole",
    "registry_plan",
    "registry_roletype",
    "registry_portfolio",
    "registry_portfolioalias"
]

class Command(BaseCommand):
    help = "Import data from CouchDb"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username", "-u", help="CouchDb username", default="admin"
        )
        parser.add_argument("--password", "-p", help="CouchDb password", required=True)
        parser.add_argument(
            "--endpoint",
            "-e",
            help="CouchDb endpoint",
            default="https://couchdb.tinga.io/",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        auth = HTTPBasicAuth(options["username"], options["password"])
        base_url = options["endpoint"]

        with connection.cursor() as cursor:
            for table in TABLES:
                cursor.execute(f"DELETE FROM {table}")

        crm_url = base_url + "crm-gqyzi5uqadltgest/_all_docs?include_docs=true"
        with requests.get(crm_url, auth=auth) as response:
            crm = list(map(lambda x: x["doc"], response.json()["rows"]))

            people = filter(lambda doc: doc.get("type") == "person", crm)
            new_people = {}
            for person in people:
                new_person = Person.objects.create(
                    name=person["name"],
                    vat=person.get("vat"),
                    phone=person["phone"],
                    email=person["email"],
                )
                if person["name"] == "LEAD_NAME":
                    lead = new_person
                new_people[person["_id"]] = new_person
                for alias in person["aliases"]:
                    try:
                        other_alias = PersonAlias.objects.get(name=alias)
                        print(
                            f"warning: alias {alias} for {new_person} already exists in {other_alias.person}"
                        )
                    except PersonAlias.DoesNotExist:
                        print(f"{alias} -> {new_person}")
                        PersonAlias.objects.create(name=alias, person=new_person)

            places = filter(lambda doc: doc.get("type") == "place", crm)
            new_places = {}
            for place in places:
                new_place = Place.objects.create(
                    address=place["address"],
                    zip_code=place["zipCode"],
                    city=place["city"],
                    province=place["province"],
                    country_code=place["countryCode"],
                    notes=place.get("notes"),
                )
                new_places[place["_id"]] = new_place

            roles = filter(lambda doc: doc.get("type") == "role", crm)
            for role in roles:
                role_type, _ = RoleType.objects.get_or_create(name=role["role"])
                if role["of"] in new_places:
                    PlaceRole.objects.create(
                        place=new_places[role["of"]],
                        role=role_type,
                        in_person=new_people[role["in"]],
                    )
                else:
                    PersonRole.objects.create(
                        person=new_people[role["of"]],
                        role=role_type,
                        in_person=new_people[role["in"]],
                    )

        sales_url = base_url + "sales-tgayvtjqpfkf1h/_all_docs?include_docs=true"
        with requests.get(sales_url, auth=auth) as response:
            sales = list(map(lambda x: x["doc"], response.json()["rows"]))

            portfolio_by_alias = {}
            portfolios = filter(lambda doc: doc.get("type") == "portfolio", sales)
            for p in portfolios:
                portfolio = Portfolio.objects.create(name=p["name"], brand=p["brand"])
                for alias in p["aliases"]:
                    portfolio_by_alias[alias] = PortfolioAlias.objects.create(portfolio=portfolio, name=alias)
                     
            billings = filter(lambda doc: doc.get("type") == "billing", sales)
            for billing in billings:
                Billing.objects.create(
                    alias=billing["alias"], description=billing["description"]
                )

            plans = filter(lambda doc: doc.get("type") == "plan", sales)
            new_plans = {}
            for plan in plans:
                new_plan = Plan.objects.create(
                    name=plan["name"],
                    category=plan["category"],
                    discounts=plan["discounts"],
                    unit=plan["unit"],
                    creation=plan["creation"]
                )
                new_plans[plan["_id"]] = new_plan

            memberships = filter(lambda doc: doc.get("type") == "membership", sales)
            for membership in memberships:
                membership_type, _ = MembershipType.objects.get_or_create(
                    name=membership["membership"]
                )

                try:
                    alias = PersonAlias.objects.get(name=membership["of"])
                except PersonAlias.DoesNotExist:
                    print(f"alias {alias} not found! Creating to LEAD")
                    alias = PersonAlias.objects.create(name=membership["of"], person=lead)

                Membership.objects.create(
                    of=alias,
                    portfolio=portfolio_by_alias[membership["portfolio"]],
                    plan=new_plans[membership["in"]],
                    membership=membership_type,
                    billing=Billing.objects.get(alias=membership["billing"]),
                )

