from django.db import models
from django.conf import settings
#from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
#from django.contrib.auth.models import User
# from storage_manager.models import UploadedFile
from django.core.validators import RegexValidator

# register_user app models
USER_CLIENT = 1
USER_COMPANY = 2
USER_MANAGER = 4
USER_GENERAL_MANAGER = 8

PropertyTypeDict = {
  1 : "Home",
  2 : "Business",
  3 : "Non-profit",
  4 : "Farmer"
}

PropertyOwnerTypeDict = {
  0 : "Rent",
  1 : "Owner"
}

# Reverse lookup: find key by value
def findKeyByValue(d, targetValue):
    for key, value in d.items():
        if value == targetValue:
            return key
    return None


class ExtendedUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        #"""Create and save a regular User with the given email and password."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = email.lower() #self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        #"""Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class ExtendedUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True, max_length=512)
    #user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey('user.SupplierCompany', on_delete=models.CASCADE, default=None, blank=True, null=True)
    branch = models.ForeignKey('user.SupplierBranch', on_delete=models.CASCADE, default=None, blank=True, null=True)
    first_name = models.CharField(max_length=64, null=True)
    last_name = models.CharField(max_length=64, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)    
    property_type = models.IntegerField(null=True)
    zip_code = models.IntegerField(null=True, default="10000")
    address = models.CharField(max_length=256, blank=True, null=True)
    city = models.CharField(max_length=256, blank=True, null=True)
    region = models.CharField(max_length=256, blank=True, null=True)
    country = models.CharField(max_length=256, blank=True, null=True)
    currency = models.CharField(max_length=256, blank=True, null=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    energy_bill = models.IntegerField(null=True)
    is_owner = models.BooleanField(default=True)
    is_renting = models.BooleanField(default=True)
    rent_type = models.IntegerField(null=True, default=1)

    role = models.PositiveIntegerField(null=False, default=USER_CLIENT)

    #is_company = models.BooleanField(default=False)
    #is_client_manager = models.BooleanField(default=False)

    if_profile_full = models.PositiveIntegerField(default=0, null=False)
    is_company_verified = models.BooleanField(default=False)

    # Password reset token and expiration time
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    reset_token_created_at = models.DateTimeField(blank=True, null=True)

    objects = ExtendedUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return self.first_name + " " + self.last_name


 


# Supplier app models

PanelLocationDict = {
  0 : "Roof",
  1 : "Ground"
} 

InverterTypeDict = {
  0: "S",    
  1: "M",    
  2: "O",    
  3: "Hybrid"    
}

################ Supplier company models based on complex diagram from Lucid #######################
class SupplierCompany(models.Model):
    # 1. Corporate details
    name = models.CharField(max_length=256, null=True)
    legal_name = models.CharField(max_length=256, null=True)
    state_id = models.PositiveIntegerField(default=0)
    tax_id = models.PositiveIntegerField(default=0)
    brand_name = models.CharField(max_length=256, null=True)
    ceo_first_name = models.CharField(max_length=128, null=True)
    ceo_last_name = models.CharField(max_length=128, null=True)
    foundation_date = models.DateField(null=True, blank=True)
    logo = models.ImageField()

    # 2. Contact information
    head_address = models.CharField(max_length=256, null=True)
    country_code = models.CharField(max_length=3, null=True)
    email = models.CharField(max_length=128, null=True)
    mobile_number = models.CharField(max_length=32, null=True,
            validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',  # Example pattern for international phone numbers
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            ),
        ])
    landline_number = models.CharField(max_length=32, null=True,
            validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',  # Example pattern for international phone numbers
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            ),
        ])
    website = models.URLField(max_length=256, null=True)

    # 3. Contact person
    name = models.CharField(max_length=64, null=True)
    position = models.CharField(max_length=64, null=True)
    mobile_number = models.CharField(max_length=32, null=True,
            validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',  # Example pattern for international phone numbers
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            ),
        ]
    )
    landline_number = models.CharField(max_length=32, null=True,
            validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',  # Example pattern for international phone numbers
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            ),
        ]
    )
    email = models.CharField(max_length=128, null=True)

    # 3. Financial details
    bank_name = models.CharField(max_length=256, null=True)
    account_number = models.CharField(max_length=256, null=True)
    swift_code = models.CharField(max_length=32, blank=True, null=True)
    iban_code = models.CharField(max_length=32, blank=True, null=True)
    sepa_code = models.CharField(max_length=32, blank=True, null=True)
    other_code = models.CharField(max_length=32, blank=True, null=True)
    
    # 4. Professional details and company services   
    solar_power_system = models.BooleanField(default=True)
    roof_mount = models.BooleanField(default=True)
    ground_mount = models.BooleanField(default=True)
    carport = models.BooleanField(default=True)
    shed = models.BooleanField(default=True)
    tracking_system = models.BooleanField(default=True)

    solar_battery = models.BooleanField(default=True)
    heatpump = models.BooleanField(default=True)


# class ProfessionalCertificate(models.Model):
#     # Ownership
#     owner_company = models.ForeignKey(SupplierCompany, on_delete=models.CASCADE, blank=True, null=True, related_name='certificate_owner_company')

#     # certificate data
#     title = models.CharField(max_length=256, null=True)
#     file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='certificate_file')

class SupplierBranch(models.Model):
    # Ownership
    owner_company = models.ForeignKey(SupplierCompany, on_delete=models.CASCADE, blank=True, null=True, related_name='branch_owner_company')

    # 5. Branch info
    name = models.CharField(max_length=256, null=True)
    legal_name = models.CharField(max_length=256, null=True)
    address = models.CharField(max_length=256, null=True)
    country_code = models.CharField(max_length=3, null=True)
    email = models.CharField(max_length=128, null=True)
    mobile_number = models.CharField(max_length=32, null=True)
    landline_number = models.CharField(max_length=32, null=True)

    # 6. Branch financial details
    bank_name = models.CharField(max_length=256, null=True)
    account_number = models.CharField(max_length=256, null=True)
    swift_code = models.CharField(max_length=32, blank=True, null=True)
    iban_code = models.CharField(max_length=32, blank=True, null=True)
    sepa_code = models.CharField(max_length=32, blank=True, null=True)
    other_code = models.CharField(max_length=32, blank=True, null=True)

    correspondent_bank_name = models.CharField(max_length=256, null=True)
    correspondent_account_number = models.CharField(max_length=256, null=True)
    correspondent_swift_code = models.CharField(max_length=32, blank=True, null=True)
    correspondent_iban_code = models.CharField(max_length=32, blank=True, null=True)
    correspondent_sepa_code = models.CharField(max_length=32, blank=True, null=True)
    correspondent_other_code = models.CharField(max_length=32, blank=True, null=True)

    # 7. Contact person
    contact_name = models.CharField(max_length=64, null=True)
    contact_position = models.CharField(max_length=64, null=True)
    contact_mobile_number = models.CharField(max_length=32, null=True,
            validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',  # Example pattern for international phone numbers
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            ),
        ]
    )
    contact_landline_number = models.CharField(max_length=32, null=True,
            validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',  # Example pattern for international phone numbers
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            ),
        ]
    )
    
    contact_email = models.CharField(max_length=128, null=True)

################ END of Supplier company models based on complex diagram from Lucid #######################


class SupplierQuoteEntry(models.Model):
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='supply_quotes')
    company = models.ForeignKey(SupplierCompany, on_delete=models.CASCADE, default=None, blank=True, null=True)
    branch = models.ForeignKey(SupplierBranch, on_delete=models.CASCADE, default=None, blank=True, null=True)
    #company_id = models.IntegerField()
    #company_name = models.CharField(max_length=256, null=True)
    #copmany_desciprition = models.TextField(null=True)
    offer_price = models.PositiveIntegerField(default=0)
    needs_met = models.FloatField(default=0)
    installation_warranty = models.IntegerField(default=0)
    quote_preparation_date = models.DateField(null=True, blank=True)
    quote_expiration_date = models.DateField(null=True, blank=True)
    sollar_installation_date = models.DateField(null=True, blank=True)

    # system general paramaters
    system_size = models.FloatField(default=0) 
    estimate_1st_year = models.FloatField(default=0)  
    number_of_panels = models.IntegerField(default=0)
    power_per_panel = models.FloatField(default=0)
    number_of_inverters = models.IntegerField(default=0)
    panel_location = models.IntegerField(default=0)

    # solar panels
    panel_manufacturer = models.CharField(max_length=256, null=True)
    panel_manufacturer_url = models.CharField(max_length=512, null=True)
    panel_warranty = models.IntegerField(default=0)

    # solar inverters
    inverter_manufacturer = models.CharField(max_length=256, null=True)
    inverter_manufacturer_url = models.CharField(max_length=512, null=True)
    inverter_model = models.CharField(max_length=256, null=True)
    inverter_model_url = models.CharField(max_length=512, null=True)
    inverter_type = models.IntegerField(default=0)
    inverter_warranty = models.IntegerField(default=0)

    # battery system design
    number_of_battery_units = models.IntegerField(default=0)
    usable_capacity_per_unit = models.FloatField(default=0)
    total_usable_capacity = models.FloatField(default=0)
    continues_power_per_unit = models.FloatField(default=0)

    # battery system equipment
    battery_manufacturer = models.CharField(max_length=256, null=True)
    battery_manufacturer_url = models.CharField(max_length=512, null=True)
    battery_model = models.CharField(max_length=256, null=True)
    battery_model_url = models.CharField(max_length=512, null=True)
    battery_warranty = models.IntegerField(default=0)
    battery_warranty_cycles = models.IntegerField(default=0)


    def __str__(self):
        return f"{self.user.id}"

class ClientRequestEntry(models.Model):
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='rquest_owner')
    property_type = models.IntegerField(null=True)
    zip_code = models.IntegerField(null=True)
    address = models.CharField(max_length=256, blank=True, null=True)
    city = models.CharField(max_length=256, blank=True, null=True)
    region = models.CharField(max_length=256, blank=True, null=True)
    country = models.CharField(max_length=256, blank=True, null=True)
    currency = models.CharField(max_length=256, blank=True, null=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    energy_bill = models.IntegerField(null=True)
    is_owner = models.BooleanField(default=True)
    is_renting = models.BooleanField(default=True)
    rent_type = models.IntegerField(null=True)

    client_manager = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='client_manager', 
    blank=True, null=True)
