# Generated by Django 4.0.4 on 2022-09-23 11:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('researchapp', '0003_remove_paper_category_paper_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='group',
            field=models.ForeignKey(blank=True, default=None, null=b'I01\n', on_delete=django.db.models.deletion.CASCADE, to='researchapp.groups'),
            preserve_default=b'I01\n',
        ),
    ]
