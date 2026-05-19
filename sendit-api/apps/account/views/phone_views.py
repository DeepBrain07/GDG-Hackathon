from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from ..utils import OTPService
from ..services.termii_service import TermiiService
from ..serializers import PhoneSerializer, PhoneOTPSerializer
from ..models import Profile


class RequestPhoneOTPView(GenericAPIView):
    """
    Endpoint to request an OTP for phone number verification.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PhoneSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        
        # Generate and store OTP
        otp = OTPService.generate_and_store_otp(phone_number, 'phone')
        
        # Send via Termii
        message = f"Your verification code is {otp}. It expires in 10 minutes."
        termii_response = TermiiService.send_dnd(phone_number, message)
        
        if termii_response:
            return Response({
                "status": "success",
                "message": "OTP sent to your phone number."
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "Failed to send OTP. Please try again later."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyPhoneOTPView(GenericAPIView):
    """
    Endpoint to verify the OTP sent to the user's phone number.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PhoneOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']

        is_valid = False

        if not settings.PHONE_NUMBER_VERIFICATION:
            is_valid = True
        else:
            is_valid = OTPService.verify_and_delete_otp(phone_number, otp, 'phone')

        if is_valid:
            # Use update() for a cleaner database hit if you don't need the object instance
            Profile.objects.filter(user=request.user).update(
                phone_number=phone_number,
                phone_verified=True
            )
            
            return Response({
                "status": "success",
                "message": "Phone number verified successfully."
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "Invalid or expired OTP."
            }, status=status.HTTP_400_BAD_REQUEST)
