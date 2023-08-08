# Generated by Django 4.0.6 on 2023-08-03 17:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_pms', '0009_remove_room_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='room_images/')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='hotel_pms.room')),
            ],
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='user',
        ),
        migrations.RemoveField(
            model_name='report',
            name='generated_by',
        ),
        migrations.DeleteModel(
            name='Blacklist',
        ),
        migrations.DeleteModel(
            name='Feedback',
        ),
        migrations.DeleteModel(
            name='Report',
        ),
    ]