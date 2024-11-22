from uuid import uuid4
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User

from registry.models import Project

class CertificateRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    certificate = models.TextField()


class SSHRootCA(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=30, unique=True)
    public_key = models.TextField()
    private_key = models.TextField()
    last_serial = models.PositiveIntegerField(default=0, editable=False)
    validity = models.DurationField(default=timedelta(hours=4))
    principal = models.CharField(max_length=30, default="iotinga")

    def save(self):
        # keep import here to avoid circular import problems
        from authentication.functions.ssh import generate_ssh_key

        if not self.public_key and not self.private_key:
            ssh_keys = generate_ssh_key(self.name)
            self.public_key = ssh_keys.public_key
            self.private_key = ssh_keys.private_key

        super().save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "SSH Root CA"


Project.add_to_class("ca_certificate", models.ForeignKey(SSHRootCA, null=True, blank=True, on_delete=models.SET_NULL))
