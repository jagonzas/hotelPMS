# Generated by Django 4.2.1 on 2023-09-11 12:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hotel_pms', '0017_rename_staff_id_staffregistrationrequest_employee_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employees',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='employee_profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
