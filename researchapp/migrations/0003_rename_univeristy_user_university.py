# Generated by Django 4.0.4 on 2022-09-24 20:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('researchapp', '0002_rename_role_type_role_roletype'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='univeristy',
            new_name='university',
        ),
    ]