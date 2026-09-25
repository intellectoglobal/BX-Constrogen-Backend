from django.contrib import admin
from .models import Clientbase, Company, Costcategory, Costcode


admin.site.register(Clientbase)
admin.site.register(Company)
admin.site.register(Costcategory)
admin.site.register(Costcode)
