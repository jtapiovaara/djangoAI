# Generated by Django 4.1.6 on 2023-03-16 14:59

import animals.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Completestory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('content', models.TextField()),
                ('rolls', models.CharField(max_length=128)),
                ('image', models.ImageField(blank=True, upload_to=animals.models.image_path)),
            ],
        ),
        migrations.CreateModel(
            name='Personality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('character', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('styles', models.CharField(max_length=64)),
                ('temp', models.DecimalField(decimal_places=1, max_digits=2)),
            ],
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('dialoque', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('personality', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='animals.personality')),
            ],
        ),
    ]
