from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Staff
from .serializer import StaffRegisterSerializer, OTPVerifySerializer, OTPLoginSerializer, StaffSerializer
import random
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.template.loader import render_to_string
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied

login_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', example='user@gmail.com'),
    },
    required=['email']
)

login_verify_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', example='user@gmail.com'),
        'otp': openapi.Schema(type=openapi.TYPE_STRING, example='123456'),
    },
    required=['email', 'otp']
)

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Admin'

class StaffRegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Register a new staff member.",
        request_body=StaffRegisterSerializer,
        responses={
            201: openapi.Response(
                description="Staff registered successfully.",
                schema=StaffSerializer()
            ),
            400: openapi.Response(
                description="Validation errors.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, example='Invalid data.')
                    }
                )
            )
        },
        tags=["Staff"]
    )
    def post(self, request):
        serializer = StaffRegisterSerializer(data=request.data)
        if serializer.is_valid():
            staff = serializer.save()
            otp = f"{random.randint(100000, 999999)}"
            staff.otp = otp
            staff.otp_created_at = timezone.now()
            staff.save()
            html_message = render_to_string('emails/otp_register.html', {
                'staff': staff,
                'otp': otp,
                'year': timezone.now().year
            })
            send_mail(
                'Your OTP Code',
                '',
                settings.DEFAULT_FROM_EMAIL,
                [staff.email],
                fail_silently=False,
                html_message=html_message
            )
            response_data = StaffSerializer(staff).data
            response_data['message'] = 'An OTP has been sent to your email.'
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPVerifyView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    @swagger_auto_schema(request_body=OTPVerifySerializer, responses={200: 'Verified'})
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            try:
                staff = Staff.objects.get(email=serializer.validated_data['email'])
            except Staff.DoesNotExist:
                return Response({'error': 'Staff not found.'}, status=status.HTTP_404_NOT_FOUND)
            if staff.otp != serializer.validated_data['otp']:
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
            # OTP expiry check (5 min)
            if (timezone.now() - staff.otp_created_at).total_seconds() > 300:
                return Response({'error': 'OTP expired.'}, status=status.HTTP_400_BAD_REQUEST)
            staff.is_verified = True
            staff.otp = None
            staff.save()
            return Response({'message': 'Email verified.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPLoginRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    @swagger_auto_schema(
        request_body=login_request_schema,
        responses={200: openapi.Response('OTP sent', schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}))}
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            staff = Staff.objects.get(email=email)
        except Staff.DoesNotExist:
            return Response({'error': 'Staff not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not staff.is_verified:
            return Response({'error': 'Email not verified.'}, status=status.HTTP_403_FORBIDDEN)
        otp = f"{random.randint(100000, 999999)}"
        staff.otp = otp
        staff.otp_created_at = timezone.now()
        staff.save()
        html_message = render_to_string('emails/otp_login.html', {
            'staff': staff,
            'otp': otp,
            'year': timezone.now().year
        })
        send_mail(
            'Your Login OTP',
            '',
            settings.DEFAULT_FROM_EMAIL,
            [staff.email],
            fail_silently=False,
            html_message=html_message
        )
        return Response({'message': 'OTP sent to email.'}, status=status.HTTP_200_OK)

class OTPLoginVerifyView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        request_body=login_verify_schema,
        responses={200: StaffSerializer}
    )
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            try:
                staff = Staff.objects.get(email=serializer.validated_data['email'])
            except Staff.DoesNotExist:
                return Response({'error': 'Staff not found.'}, status=status.HTTP_404_NOT_FOUND)
            if staff.otp != serializer.validated_data['otp']:
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
            if (timezone.now() - staff.otp_created_at).total_seconds() > 300:
                return Response({'error': 'OTP expired.'}, status=status.HTTP_400_BAD_REQUEST)
            staff.otp = None
            staff.save()

            # Generate JWT token for the staff
            refresh = RefreshToken.for_user(staff)
            access_token = refresh.access_token

            # Add the user's role to the access token
            access_token['role'] = staff.role

            return Response({
                'staff': StaffSerializer(staff).data,
                'refresh': str(refresh),
                'access': str(access_token)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StaffListView(APIView):
    permission_classes = [IsAdminRole, IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all staff members.",
        responses={200: StaffSerializer(many=True)},
        tags=["Staff"]
    )
    def get(self, request):
        """List all staff in the system."""
        staff = Staff.objects.all()
        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data)

class UpdateUserCredentialsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update user credentials such as name, email, branch, and role. If the email is updated, an OTP will be sent to verify the new email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, example='John'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, example='Doe'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', example='john.doe@example.com'),
                'branch': openapi.Schema(type=openapi.TYPE_STRING, example='Westlands'),
                'role': openapi.Schema(type=openapi.TYPE_STRING, example='User'),
            },
            required=['first_name', 'last_name', 'email']
        ),
        responses={200: openapi.Response('User details updated successfully.')},
        tags=["Staff"]
    )
    def put(self, request):
        user = request.user
        data = request.data
        new_email = data.get('email', user.email)
        if new_email != user.email:
            otp = f"{random.randint(100000, 999999)}"
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.is_verified = False  # Mark as unverified until OTP is confirmed
            html_message = render_to_string('emails/otp_register.html', {
                'staff': user,
                'otp': otp,
                'year': timezone.now().year
            })
            send_mail(
                'Verify Your New Email',
                '',
                settings.DEFAULT_FROM_EMAIL,
                [new_email],
                fail_silently=False,
                html_message=html_message
            )
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = new_email
        user.branch = data.get('branch', user.branch)
        user.role = data.get('role', user.role)
        user.save()
        return Response({'message': 'User details updated successfully. If you updated your email, please verify it using the OTP sent to your new email.'}, status=status.HTTP_200_OK)

class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Resend a fresh OTP to the user's email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', example='user@gmail.com'),
            },
            required=['email']
        ),
        responses={200: 'OTP resent successfully', 404: 'Staff not found'}
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            staff = Staff.objects.get(email=email)
        except Staff.DoesNotExist:
            return Response({'error': 'Staff not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a new OTP
        otp = f"{random.randint(100000, 999999)}"
        staff.otp = otp
        staff.otp_created_at = timezone.now()
        staff.save()

        # Send the new OTP via email
        html_message = render_to_string('emails/otp_register.html', {
            'staff': staff,
            'otp': otp,
            'year': timezone.now().year
        })
        send_mail(
            'Your New OTP Code',
            '',
            settings.DEFAULT_FROM_EMAIL,
            [staff.email],
            fail_silently=False,
            html_message=html_message
        )

        return Response({'message': 'A new OTP has been sent to your email.'}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout the user by revoking their JWT tokens.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The refresh token to be revoked.",
                    example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                )
            },
            required=['refresh_token']
        ),
        responses={
            200: openapi.Response(
                description="Logout successful.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Logout successful."
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Refresh token is required."
                        )
                    }
                )
            )
        },
        tags=["Authentication"]
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Revoke the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GetUserCredentialsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Fetch user credentials based on user_id and JWT.",
        responses={
            200: openapi.Response(
                description="User credentials fetched successfully.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, example='user-1'),
                        'first_name': openapi.Schema(type=openapi.TYPE_STRING, example='John'),
                        'last_name': openapi.Schema(type=openapi.TYPE_STRING, example='Doe'),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', example='john.doe@example.com'),
                        'branch': openapi.Schema(type=openapi.TYPE_STRING, example='Westlands'),
                        'role': openapi.Schema(type=openapi.TYPE_STRING, example='User'),
                    }
                )
            ),
            403: openapi.Response(
                description="Permission denied.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, example='Permission denied.')
                    }
                )
            ),
            404: openapi.Response(
                description="User not found.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, example='User not found.')
                    }
                )
            )
        },
        tags=["Staff"]
    )
    def get(self, request, user_id):
        # Decode the JWT to verify the user
        jwt_authenticator = JWTAuthentication()
        try:
            validated_token = jwt_authenticator.get_validated_token(request.headers.get('Authorization').split()[1])
            jwt_user_id = validated_token.get('user_id')

            if str(jwt_user_id) != user_id:
                return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

            try:
                staff = Staff.objects.get(id=user_id)
                return Response({
                    'id': staff.id,
                    'first_name': staff.first_name,
                    'last_name': staff.last_name,
                    'email': staff.email,
                    'branch': staff.branch,
                    'role': staff.role,
                }, status=status.HTTP_200_OK)
            except Staff.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

class AdminUpdateUserCredentialsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    @swagger_auto_schema(
        operation_description="Update user credentials such as name, email, branch, and role by an Admin.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_STRING, example='1'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, example='John'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, example='Doe'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', example='john.doe@example.com'),
                'branch': openapi.Schema(type=openapi.TYPE_STRING, example='Westlands'),
                'role': openapi.Schema(type=openapi.TYPE_STRING, example='User'),
            },
            required=['user_id', 'first_name', 'last_name', 'email']
        ),
        responses={
            200: openapi.Response('User details updated successfully.'),
            404: openapi.Response('User not found.'),
            403: openapi.Response('Permission denied.')
        },
        tags=["Admin"]
    )
    def put(self, request):
        data = request.data
        user_id = data.get('user_id')

        try:
            staff = Staff.objects.get(id=user_id)
            staff.first_name = data.get('first_name', staff.first_name)
            staff.last_name = data.get('last_name', staff.last_name)
            staff.email = data.get('email', staff.email)
            staff.branch = data.get('branch', staff.branch)
            staff.role = data.get('role', staff.role)
            staff.save()

            return Response({'message': 'User details updated successfully.'}, status=status.HTTP_200_OK)
        except Staff.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AdminGetUserCredentialsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    @swagger_auto_schema(
        operation_description="Fetch user credentials by an Admin based on user_id.",
        responses={
            200: openapi.Response(
                description="User credentials fetched successfully.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, example='1'),
                        'first_name': openapi.Schema(type=openapi.TYPE_STRING, example='John'),
                        'last_name': openapi.Schema(type=openapi.TYPE_STRING, example='Doe'),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', example='john.doe@example.com'),
                        'branch': openapi.Schema(type=openapi.TYPE_STRING, example='Westlands'),
                        'role': openapi.Schema(type=openapi.TYPE_STRING, example='User'),
                    }
                )
            ),
            404: openapi.Response('User not found.'),
            403: openapi.Response('Permission denied.')
        },
        tags=["Admin"]
    )
    def get(self, request, user_id):
        try:
            staff = Staff.objects.get(id=user_id)
            return Response({
                'id': staff.id,
                'first_name': staff.first_name,
                'last_name': staff.last_name,
                'email': staff.email,
                'branch': staff.branch,
                'role': staff.role,
            }, status=status.HTTP_200_OK)
        except Staff.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
