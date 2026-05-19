from django.contrib import admin
from .models import Media,Location,Notification
# Register your models here.


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['id', 'tag', ]

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', "city", 'latitude', 'longitude', 'created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message', 'created_at']
    search_fields = ['user__username', 'message']
    list_filter = ['user', 'created_at']