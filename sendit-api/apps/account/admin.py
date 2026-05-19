from cryptography.fernet import Fernet
from django.conf import settings
from .models import Verification
from django.contrib import admin
from .models import CustomUser, VerifyOTP,Profile
# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name')
    search_fields = ('first_name', 'last_name', 'email',)

    class Meta:
        model = CustomUser
        fields = '__all__'


@admin.register(VerifyOTP)
class VerifyOTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'otp', 'purpose', 'created_at')
    search_fields = ('email',)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'otp', 'created_at')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', "type", 'full_name', 'gender','age')
    search_fields = ('first_name','last_name')

    def age(self, instance):
        return instance.get_age()

    class Meta:
        model = Profile
        fields = ('user', 'first_name', 'email', 'middle_name',
                  'last_name', 'gender', 'age', 'bio')


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'profile', 'verification_type', 'is_verified', 'decrypted_id_number_display']
    list_editable = ('is_verified',)
    readonly_fields = ('decrypted_id_number_display',)

    def decrypted_id_number_display(self, obj):
        if not obj.id_number:
            return "-"
        try:
            f = Fernet(settings.ENCRYPTION_KEY)
            return f.decrypt(obj.id_number.encode()).decode()
        except Exception:
            return "Unable to decrypt (wrong key or plain)"
    
    decrypted_id_number_display.short_description = "ID Number (Decrypted)"

    def save_model(self, request, obj, form, change):
        # If verification is approved
        if obj.is_verified:
            obj.profile.is_verified = True
            obj.profile.save()

        super().save_model(request, obj, form, change)
