from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for Product model"""
    list_display = ('product_name', 'price', 'stock', 'image_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product_name', 'description')
    ordering = ('product_name',)
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    fields = ('product_name', 'description', 'price', 'stock', 'product_image', 'image_preview', 'created_at', 'updated_at')
    
    def image_preview(self, obj):
        """Display image preview in admin list"""
        if obj.product_image:
            return f'<img src="{obj.product_image.url}" style="max-height: 50px; max-width: 50px;" />'
        return "No image"
    image_preview.allow_tags = True
    image_preview.short_description = 'Image Preview'