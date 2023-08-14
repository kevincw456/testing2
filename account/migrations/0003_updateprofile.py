# Generated by Django 4.2.2 on 2023-08-08 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_remove_request_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='UpdateProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('email', models.EmailField(blank=True, max_length=100)),
                ('phone_number', models.IntegerField(null=True)),
                ('address', models.CharField(blank=True, max_length=100)),
                ('postal_code', models.IntegerField(null=True)),
                ('twitter_handle', models.CharField(blank=True, max_length=20)),
            ],
        ),
    ]
