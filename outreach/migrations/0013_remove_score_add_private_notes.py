# Generated by Django 2.2.3 on 2019-07-04 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outreach', '0012_add_secondary_contact'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outreachevent',
            name='score',
        ),
        migrations.AddField(
            model_name='outreachevent',
            name='private_notes',
            field=models.CharField(blank=True, help_text='Private notes only for yourself.  These will not show to registrants or anywhere else public-facing.', max_length=400, null=True),
        ),
    ]
