# Generated manually for ProductHistory model
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0005_remove_productimage_archived_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(help_text='Quantity purchased')),
                ('purchase_type', models.CharField(choices=[('on_premises', 'On-Premises Purchase'), ('restock', 'Restock')], default='on_premises', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, help_text='Additional notes about the purchase', null=True)),
                ('performed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product_purchases', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_history', to='products.product')),
            ],
            options={
                'verbose_name': 'Product Purchase History',
                'verbose_name_plural': 'Product Purchase Histories',
                'db_table': 'product_history',
                'ordering': ['-created_at'],
            },
        ),
    ]

