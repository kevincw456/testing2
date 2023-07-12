# Generated by Django 4.2.2 on 2023-06-22 06:00

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=128)),
                ('password_confirmation', models.CharField(max_length=128)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.IntegerField(null=True)),
                ('address', models.CharField(max_length=100)),
                ('postal_code', models.IntegerField(null=True)),
                ('twitter_handle', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('Approved', 'Approved'), ('Pending', 'Pending')], default='Pending', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='tweets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twitterUser', models.CharField(max_length=255)),
                ('tweet', models.CharField(max_length=255)),
                ('tweetURL', models.CharField(max_length=255)),
                ('category', models.CharField(choices=[('NM', 'Neutral'), ('OL', 'Offensive Language'), ('HM', 'Hateful Message')], default='Not yet analysed', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='twitterUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twitterUser', models.CharField(max_length=255)),
                ('bio', models.CharField(max_length=255)),
                ('category', models.CharField(choices=[('Neutral', 'Neutral'), ('Offensive Language', 'Offensive Language'), ('Hateful Message', 'Hateful Message')], default='Not yet analysed', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='UpdateCustomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=100)),
                ('password1', models.CharField(blank=True, max_length=20)),
                ('password2', models.CharField(blank=True, max_length=20)),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('email', models.EmailField(blank=True, max_length=100)),
                ('phone_number', models.IntegerField(null=True)),
                ('address', models.CharField(blank=True, max_length=100)),
                ('postal_code', models.IntegerField(null=True)),
                ('twitter_handle', models.CharField(blank=True, max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone_number', models.IntegerField(null=True)),
                ('address', models.CharField(blank=True, max_length=100)),
                ('postal_code', models.IntegerField(null=True)),
                ('twitter_handle', models.CharField(blank=True, max_length=20)),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Suspended', 'Suspended')], default='Suspended', max_length=20)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]