from rest_framework import serializers
from .models import WaitlistEntry, NewsletterSubscriber

class WaitlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitlistEntry
        fields = ['first_name', 'last_name', 'email']

    def validate_email(self, value):
        return value.lower()

class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']

    def validate_email(self, value):
        return value.lower()