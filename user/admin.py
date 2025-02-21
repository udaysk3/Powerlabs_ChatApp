from django.contrib import admin
from .models import ExtendedUser, SupplierCompany, SupplierQuoteEntry, ClientRequestEntry
# Register your models here.

admin.site.register(ExtendedUser)
admin.site.register(SupplierCompany)
admin.site.register(SupplierQuoteEntry)
admin.site.register(ClientRequestEntry)
