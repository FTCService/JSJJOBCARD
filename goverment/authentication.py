from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import requests

class SSOGovernmentTokenAuthentication(BaseAuthentication):
    """
    Authenticates a Government user using a token validated through SSO service.
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Token "):
            return None

        token = auth_header.split("Token ")[1]

        try:
            response = requests.post(
                settings.AUTH_SERVER_URL + "/api/goverment/verify-token/",
                json={"token": token},
                timeout=5
            )

            if response.status_code != 200:
                raise AuthenticationFailed("Invalid or expired token.")

            data = response.json()
            user = AuthenticatedGovernmentUser(
                id=data["user_id"],
                full_name=data["full_name"],
                email=data["email"],
                mobile_number=data["mobile_number"],
                department=data["department"],
                designation=data["designation"]
            )
            return (user, None)

        except requests.RequestException:
            raise AuthenticationFailed("Government auth service unreachable.")

class AuthenticatedGovernmentUser:
    def __init__(self, id, full_name, email, mobile_number, department, designation):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.mobile_number = mobile_number
        self.department = department
        self.designation = designation
        self.is_authenticated = True  # Required by DRF

    def __str__(self):
        return f"GovernmentUser {self.full_name}"
