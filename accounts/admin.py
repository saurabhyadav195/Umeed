from django.contrib import admin
from .models import User, VerificationDocument

class VerificationDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'approved', 'rejected')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.approved:
            user = obj.user
            user.is_verified = True
            user.save()

admin.site.register(User)
admin.site.register(VerificationDocument, VerificationDocumentAdmin)