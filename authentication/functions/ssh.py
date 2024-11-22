from dataclasses import dataclass
from datetime import datetime

from django.contrib.auth.models import User
from django.db import transaction
from sshkey_tools.cert import CertificateFields, SSHCertificate
from sshkey_tools.keys import Ed25519PrivateKey, Ed25519PublicKey

from authentication.models import CertificateRequest, SSHRootCA
from registry.models import Project


@dataclass
class SSHKey:
    private_key: str
    public_key: str


@dataclass
class SSHCredentials(SSHKey):
    certificate: str


def generate_ssh_key(comment: str = "") -> SSHKey:
    ed25519_priv = Ed25519PrivateKey.generate()
    ed25519_pub = ed25519_priv.public_key

    if comment is not None:
        ed25519_pub.comment = comment.replace(' ', '_')

    return SSHKey(
        private_key=ed25519_priv.to_string(),
        public_key=ed25519_pub.to_string()
    )


def generate_ssh_credentials(root_ca: SSHRootCA, user: User, project: Project) -> SSHCredentials:
    with transaction.atomic():
        root_ca.refresh_from_db()
        serial = root_ca.last_serial + 1

        # 1. generate key pair
        user_ssh_keys: SSHKey = generate_ssh_key(user.email)
        user_pubkey = Ed25519PublicKey.from_string(user_ssh_keys.public_key)
        
        ca_privkey = Ed25519PrivateKey.from_string(root_ca.private_key)

        # 2. generate certificate
        cert_fields = CertificateFields(
            serial=serial,
            cert_type=1,
            key_id=user.email,
            principals=[root_ca.principal],
            valid_after=datetime.now(),
            valid_before=datetime.now() + root_ca.validity,
            extensions=[
                "permit-X11-forwarding",
                "permit-agent-forwarding",
                "permit-port-forwarding",
                "permit-pty",
                "permit-user-rc",
            ],
        )

        certificate = SSHCertificate.create(
            subject_pubkey=user_pubkey,
            ca_privkey=ca_privkey,
            fields=cert_fields,
        )

        certificate.sign()
        certificate_str = certificate.to_string()

        # 3. update last serial
        root_ca.last_serial = serial
        root_ca.save()

        # 4. insert certificate request event
        cert_request = CertificateRequest(user=user, project=project, certificate=certificate_str)
        cert_request.save()

        return SSHCredentials(
            private_key=user_ssh_keys.private_key,
            public_key=user_ssh_keys.public_key,
            certificate=certificate_str
        )

