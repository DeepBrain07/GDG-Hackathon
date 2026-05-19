from rest_framework.permissions import BasePermission


class IsOfferOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.offer.sender == request.user 


class IsCarrier(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.offer.sender == request.user 

class IsOfferOwnerOrIsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        offer = obj.offer
        return offer.sender == request.user or request.user.is_superuser    
