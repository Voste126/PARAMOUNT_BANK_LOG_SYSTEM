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

class StaffRegisterView(APIView):
    @swagger_auto_schema(request_body=StaffRegisterSerializer, responses={201: StaffSerializer})
    def post(self, request):
        serializer = StaffRegisterSerializer(data=request.data)
        if serializer.is_valid():
            staff = serializer.save()
            otp = f"{random.randint(100000, 999999)}"
            staff.otp = otp
            staff.otp_created_at = timezone.now()
            staff.save()
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [staff.email],
                fail_silently=False,
            )
            return Response({'message': 'Staff registered. OTP sent to email.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPVerifyView(APIView):
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
        send_mail(
            'Your Login OTP',
            f'Your login OTP is {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [staff.email],
            fail_silently=False,
        )
        return Response({'message': 'OTP sent to email.'}, status=status.HTTP_200_OK)

class OTPLoginVerifyView(APIView):
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
            return Response(StaffSerializer(staff).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# For SSO, Django's authentication system can be integrated with a custom backend if needed.
# This implementation focuses on OTP-based authentication as requested.
