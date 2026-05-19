from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import WaitlistEntry, NewsletterSubscriber
from .serializers import WaitlistSerializer, SubscribeSerializer

class WaitlistCreateView(APIView):
    """
    Endpoint for early access signups.
    Requires: first_name, last_name, and email.
    """
    permission_classes = [AllowAny]
    serializer_class = WaitlistSerializer

    @extend_schema(
        summary="Join the Waitlist",
        description="Allows users to join the early access waitlist by providing their full name and email.",
        request=WaitlistSerializer,
        responses={
            201: OpenApiResponse(description="Successfully joined the waitlist."),
            200: OpenApiResponse(description="User already exists on the waitlist."),
            400: OpenApiResponse(description="Validation error (e.g., invalid email).")
        },
        tags=["Landing"]
    )
    def post(self, request):
        email = request.data.get('email', '').lower()
        
        # Graceful handling for existing entries
        if WaitlistEntry.objects.filter(email=email).exists():
            return Response(
                {"message": "You're already on the waitlist! Stay tuned for updates."}, 
                status=status.HTTP_200_OK
            )

        serializer = WaitlistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Welcome to the inner circle! You're on the waitlist."}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscribeCreateView(APIView):
    """
    Endpoint for general newsletter subscriptions.
    Requires: email.
    """
    permission_classes = [AllowAny]
    serializer_class = SubscribeSerializer

    @extend_schema(
        summary="Subscribe to Newsletter",
        description="Adds a user's email to the marketing newsletter mailing list.",
        request=SubscribeSerializer,
        responses={
            201: OpenApiResponse(description="Successfully subscribed."),
            200: OpenApiResponse(description="User is already a subscriber."),
            400: OpenApiResponse(description="Validation error.")
        },
        tags=["Landing"]
    )
    def post(self, request):
        email = request.data.get('email', '').lower()

        # Graceful handling for existing subscribers
        if NewsletterSubscriber.objects.filter(email=email).exists():
            return Response(
                {"message": "You're already subscribed to our newsletter!"}, 
                status=status.HTTP_200_OK
            )

        serializer = SubscribeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Thanks for subscribing to our newsletter!"}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)