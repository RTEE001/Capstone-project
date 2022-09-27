# Generated by Django 4.0.4 on 2022-09-26 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('researchapp', '0004_group_created_university_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('message', models.CharField(max_length=250)),
                ('date_posted', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]