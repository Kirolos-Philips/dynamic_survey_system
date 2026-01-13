from django.contrib import admin

from .models import Invitation, InvitationBatch


@admin.register(InvitationBatch)
class InvitationBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "survey", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("survey__title",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "batch", "status", "sent_at")
    list_filter = ("status", "sent_at")
    search_fields = ("email", "batch__survey__title")
    readonly_fields = ("token", "sent_at")
