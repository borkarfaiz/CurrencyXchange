# Generated by Django 3.0.8 on 2020-07-29 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='transaction_status',
            field=models.CharField(choices=[('FAILED', 'Failed'), ('COMPLETED', 'Completed'), ('INITIATED', 'Initiated')], default='INITIATED', max_length=20),
        ),
    ]
