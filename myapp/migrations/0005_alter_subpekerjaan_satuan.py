# Generated by Django 5.0.3 on 2024-05-29 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_referensi_subpekerjaan_referensi_harga_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subpekerjaan',
            name='satuan',
            field=models.CharField(choices=[('KMS', 'KMS'), ('Bay', 'Bay'), ('Lot', 'Lot'), ('Set', 'Set'), ('Unit', 'Unit'), ('LS', 'LS'), ('m2', 'm2'), ('KMR', 'KMR'), ('DIA', 'DIA'), ('Bank', 'Bank'), ('CB', 'CB')], max_length=50),
        ),
    ]
