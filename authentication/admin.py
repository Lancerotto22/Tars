from django.contrib import admin

from authentication.models import CertificateRequest, SSHRootCA

@admin.register(CertificateRequest)
class CertificateRequestAdmin(admin.ModelAdmin):
    list_display = ["user", "project", "created_at"]
    list_filter = ["project"]
    search_fields = ["user", "project"]


@admin.register(SSHRootCA)
class SSHRootCAAdmin(admin.ModelAdmin):
    readonly_fields = ["id", "last_serial", "public_key"]
    list_display = ["name", "principal", "validity", "last_serial"]
    exclude = ["private_key"]
