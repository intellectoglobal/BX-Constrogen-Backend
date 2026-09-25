from django.contrib import admin
from .models import (Amenity, Projecttype, Projectstatus,
                     Project, Projcostcode, Projectamenity)

admin.site.register(Amenity)
admin.site.register(Projecttype)
admin.site.register(Projectstatus)
admin.site.register(Project)
admin.site.register(Projcostcode)
admin.site.register(Projectamenity)
