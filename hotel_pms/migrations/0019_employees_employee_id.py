# Generated by Django 4.2.1 on 2023-09-20 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_pms', '0018_alter_employees_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='employees',
            name='employee_id',
            field=models.TextField(blank=True, max_length=5, null=True, unique=True),
        ),
    ]