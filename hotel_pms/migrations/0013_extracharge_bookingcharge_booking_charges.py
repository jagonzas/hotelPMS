# Generated by Django 4.0.6 on 2023-08-09 12:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_pms', '0012_booking_accompanies'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtraCharge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('charge_type', models.CharField(choices=[('bed', 'Extra Bed'), ('smoking', 'Smoking Fee'), ('coffee', 'Coffe Price'), ('water', 'Water Price'), ('maintenance', 'Maintenance Price'), ('late', 'Late Fees'), ('early', 'Early Check Fee'), ('miscellaneous', 'Extra Fees')], max_length=50)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=7)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='BookingCharge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotel_pms.booking')),
                ('charge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotel_pms.extracharge')),
            ],
            options={
                'unique_together': {('booking', 'charge')},
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='charges',
            field=models.ManyToManyField(through='hotel_pms.BookingCharge', to='hotel_pms.extracharge'),
        ),
    ]