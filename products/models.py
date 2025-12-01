from django.db import models


class Product(models.Model):
    """Model for beauty clinic products"""
    product_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    product_image = models.ImageField(upload_to='products/', blank=True, null=True)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

    class Meta:
        db_table = 'products'
        ordering = ['product_name']


class ProductHistory(models.Model):
    """Model to track product purchase history"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_history')
    quantity = models.IntegerField(help_text="Quantity purchased")
    purchase_type = models.CharField(max_length=20, choices=[
        ('on_premises', 'On-Premises Purchase'),
        ('restock', 'Restock'),
    ], default='on_premises')
    performed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='product_purchases')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the purchase")
    
    class Meta:
        db_table = 'product_history'
        ordering = ['-created_at']
        verbose_name = 'Product Purchase History'
        verbose_name_plural = 'Product Purchase Histories'
    
    def __str__(self):
        return f"{self.product.product_name} - {self.quantity} units - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ProductImage(models.Model):
    """Model for additional product images"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.product_name} - Image {self.id}"

    class Meta:
        db_table = 'product_images'
        ordering = ['-is_primary', '-created_at']