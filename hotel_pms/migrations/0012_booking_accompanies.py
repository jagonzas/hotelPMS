# Generated by Django 4.0.6 on 2023-08-09 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_pms', '0011_remove_booking_approval_alter_roomimage_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='accompanies',
            field=models.PositiveIntegerField(default=0, help_text='Number of people accompanying the customer.'),
        ),
    ]
