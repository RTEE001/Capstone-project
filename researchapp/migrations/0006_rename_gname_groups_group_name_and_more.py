# Generated by Django 4.0.4 on 2022-09-16 17:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('researchapp', '0005_paper_created'),
    ]

    operations = [
        migrations.RenameField(
            model_name='groups',
            old_name='Gname',
            new_name='group_name',
        ),
        migrations.RenameField(
            model_name='groups',
            old_name='uni',
            new_name='university',
        ),
        migrations.RenameField(
            model_name='university',
            old_name='Uniname',
            new_name='University',
        ),
    ]
