from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from authentication.functions.ssh import generate_ssh_credentials
from registry.models import Project, ProjectMembership


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generate_certificate(request: Request):
    user: User = request.user
    project_id = request.query_params.get("project")
    if project_id is None or user is None or user.email is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    project_name, customer_name = project_id.strip().split('@')
    
    project = Project.objects.get(name=project_name, customer__name=customer_name)
    if project is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    root_ca = project.ca_certificate
    if root_ca is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    membership = ProjectMembership.objects.get(user=user, project=project)

    # check if customer has correct permission
    if (membership.role != ProjectMembership.ProjectMembershipRole.ADMIN and 
        membership.role != ProjectMembership.ProjectMembershipRole.CUSTOMER):
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    credentials = generate_ssh_credentials(root_ca, user, project)

    return Response({
        'private_key': credentials.private_key,
        'public_key': credentials.public_key,
        'certificate': credentials.certificate
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_token(request: Request):
    token, _ = Token.objects.get_or_create(user=request.user)

    return Response({
        "token": token.key,
    })
