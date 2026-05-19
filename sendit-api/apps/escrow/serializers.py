from rest_framework import serializers
from .models import Escrow
from apps.account.serializers import UserSerializer

class EscrowSerializer(serializers.ModelSerializer):
    offer_id = serializers.ReadOnlyField(source='offer.id')
    released_by = UserSerializer(read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Escrow
        fields = [
            'id', 'offer_id', 'amount',  'status',
            'is_released', 'released_at', 'released_amount_to_carrier', 
            'released_by', "note",'created_at'
        ]
        read_only_fields = ['status', 'is_released', 'released_at', 'released_by']
