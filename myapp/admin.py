from django.contrib import admin
from django.utils.html import format_html
from .models import Land, Lead, LandImage, SavedProperty, Inquiry


# 🔥 Inline images
class LandImageInline(admin.TabularInline):
    model = LandImage
    extra = 1

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "No Image"

    readonly_fields = ['image_preview']


# 🔥 Land Admin (main upgrade)
@admin.register(Land)
class LandAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'property_type', 'price', 'created_at']
    list_filter = ['property_type', 'location']
    search_fields = ['title', 'location']
    inlines = [LandImageInline]


# 🔥 Other models (simple register)
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'created_at']


@admin.register(LandImage)
class LandImageAdmin(admin.ModelAdmin):
    list_display = ['land', 'created_at']


@admin.register(SavedProperty)
class SavedPropertyAdmin(admin.ModelAdmin):
    list_display = ['user', 'land', 'created_at']

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'land', 'created_at']