# Generated by Django 5.1.6 on 2025-02-20 10:48

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupplierBranch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, null=True)),
                ('legal_name', models.CharField(max_length=256, null=True)),
                ('address', models.CharField(max_length=256, null=True)),
                ('country_code', models.CharField(max_length=3, null=True)),
                ('email', models.CharField(max_length=128, null=True)),
                ('mobile_number', models.CharField(max_length=32, null=True)),
                ('landline_number', models.CharField(max_length=32, null=True)),
                ('bank_name', models.CharField(max_length=256, null=True)),
                ('account_number', models.CharField(max_length=256, null=True)),
                ('swift_code', models.CharField(blank=True, max_length=32, null=True)),
                ('iban_code', models.CharField(blank=True, max_length=32, null=True)),
                ('sepa_code', models.CharField(blank=True, max_length=32, null=True)),
                ('other_code', models.CharField(blank=True, max_length=32, null=True)),
                ('correspondent_bank_name', models.CharField(max_length=256, null=True)),
                ('correspondent_account_number', models.CharField(max_length=256, null=True)),
                ('correspondent_swift_code', models.CharField(blank=True, max_length=32, null=True)),
                ('correspondent_iban_code', models.CharField(blank=True, max_length=32, null=True)),
                ('correspondent_sepa_code', models.CharField(blank=True, max_length=32, null=True)),
                ('correspondent_other_code', models.CharField(blank=True, max_length=32, null=True)),
                ('contact_name', models.CharField(max_length=64, null=True)),
                ('contact_position', models.CharField(max_length=64, null=True)),
                ('contact_mobile_number', models.CharField(max_length=32, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('contact_landline_number', models.CharField(max_length=32, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('contact_email', models.CharField(max_length=128, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SupplierCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('legal_name', models.CharField(max_length=256, null=True)),
                ('state_id', models.PositiveIntegerField(default=0)),
                ('tax_id', models.PositiveIntegerField(default=0)),
                ('brand_name', models.CharField(max_length=256, null=True)),
                ('ceo_first_name', models.CharField(max_length=128, null=True)),
                ('ceo_last_name', models.CharField(max_length=128, null=True)),
                ('foundation_date', models.DateField(blank=True, null=True)),
                ('logo', models.ImageField(upload_to='')),
                ('head_address', models.CharField(max_length=256, null=True)),
                ('country_code', models.CharField(max_length=3, null=True)),
                ('website', models.URLField(max_length=256, null=True)),
                ('name', models.CharField(max_length=64, null=True)),
                ('position', models.CharField(max_length=64, null=True)),
                ('mobile_number', models.CharField(max_length=32, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('landline_number', models.CharField(max_length=32, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('email', models.CharField(max_length=128, null=True)),
                ('bank_name', models.CharField(max_length=256, null=True)),
                ('account_number', models.CharField(max_length=256, null=True)),
                ('swift_code', models.CharField(blank=True, max_length=32, null=True)),
                ('iban_code', models.CharField(blank=True, max_length=32, null=True)),
                ('sepa_code', models.CharField(blank=True, max_length=32, null=True)),
                ('other_code', models.CharField(blank=True, max_length=32, null=True)),
                ('solar_power_system', models.BooleanField(default=True)),
                ('roof_mount', models.BooleanField(default=True)),
                ('ground_mount', models.BooleanField(default=True)),
                ('carport', models.BooleanField(default=True)),
                ('shed', models.BooleanField(default=True)),
                ('tracking_system', models.BooleanField(default=True)),
                ('solar_battery', models.BooleanField(default=True)),
                ('heatpump', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExtendedUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=512, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(max_length=64, null=True)),
                ('last_name', models.CharField(max_length=64, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('property_type', models.IntegerField(null=True)),
                ('zip_code', models.IntegerField(default='10000', null=True)),
                ('address', models.CharField(blank=True, max_length=256, null=True)),
                ('city', models.CharField(blank=True, max_length=256, null=True)),
                ('region', models.CharField(blank=True, max_length=256, null=True)),
                ('country', models.CharField(blank=True, max_length=256, null=True)),
                ('currency', models.CharField(blank=True, max_length=256, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=32, null=True)),
                ('energy_bill', models.IntegerField(null=True)),
                ('is_owner', models.BooleanField(default=True)),
                ('is_renting', models.BooleanField(default=True)),
                ('rent_type', models.IntegerField(default=1, null=True)),
                ('role', models.PositiveIntegerField(default=1)),
                ('if_profile_full', models.PositiveIntegerField(default=0)),
                ('is_company_verified', models.BooleanField(default=False)),
                ('reset_token', models.CharField(blank=True, max_length=64, null=True)),
                ('reset_token_created_at', models.DateTimeField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('branch', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.supplierbranch')),
                ('company', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.suppliercompany')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClientRequestEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('property_type', models.IntegerField(null=True)),
                ('zip_code', models.IntegerField(null=True)),
                ('address', models.CharField(blank=True, max_length=256, null=True)),
                ('city', models.CharField(blank=True, max_length=256, null=True)),
                ('region', models.CharField(blank=True, max_length=256, null=True)),
                ('country', models.CharField(blank=True, max_length=256, null=True)),
                ('currency', models.CharField(blank=True, max_length=256, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=32, null=True)),
                ('energy_bill', models.IntegerField(null=True)),
                ('is_owner', models.BooleanField(default=True)),
                ('is_renting', models.BooleanField(default=True)),
                ('rent_type', models.IntegerField(null=True)),
                ('client_manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_manager', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rquest_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='supplierbranch',
            name='owner_company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='branch_owner_company', to='user.suppliercompany'),
        ),
        migrations.CreateModel(
            name='SupplierQuoteEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offer_price', models.PositiveIntegerField(default=0)),
                ('needs_met', models.FloatField(default=0)),
                ('installation_warranty', models.IntegerField(default=0)),
                ('quote_preparation_date', models.DateField(blank=True, null=True)),
                ('quote_expiration_date', models.DateField(blank=True, null=True)),
                ('sollar_installation_date', models.DateField(blank=True, null=True)),
                ('system_size', models.FloatField(default=0)),
                ('estimate_1st_year', models.FloatField(default=0)),
                ('number_of_panels', models.IntegerField(default=0)),
                ('power_per_panel', models.FloatField(default=0)),
                ('number_of_inverters', models.IntegerField(default=0)),
                ('panel_location', models.IntegerField(default=0)),
                ('panel_manufacturer', models.CharField(max_length=256, null=True)),
                ('panel_manufacturer_url', models.CharField(max_length=512, null=True)),
                ('panel_warranty', models.IntegerField(default=0)),
                ('inverter_manufacturer', models.CharField(max_length=256, null=True)),
                ('inverter_manufacturer_url', models.CharField(max_length=512, null=True)),
                ('inverter_model', models.CharField(max_length=256, null=True)),
                ('inverter_model_url', models.CharField(max_length=512, null=True)),
                ('inverter_type', models.IntegerField(default=0)),
                ('inverter_warranty', models.IntegerField(default=0)),
                ('number_of_battery_units', models.IntegerField(default=0)),
                ('usable_capacity_per_unit', models.FloatField(default=0)),
                ('total_usable_capacity', models.FloatField(default=0)),
                ('continues_power_per_unit', models.FloatField(default=0)),
                ('battery_manufacturer', models.CharField(max_length=256, null=True)),
                ('battery_manufacturer_url', models.CharField(max_length=512, null=True)),
                ('battery_model', models.CharField(max_length=256, null=True)),
                ('battery_model_url', models.CharField(max_length=512, null=True)),
                ('battery_warranty', models.IntegerField(default=0)),
                ('battery_warranty_cycles', models.IntegerField(default=0)),
                ('branch', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.supplierbranch')),
                ('company', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.suppliercompany')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supply_quotes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
