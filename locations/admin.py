from django.contrib import admin
from .models import Governorate, GovernorateChangeLog, Continent, ContinentChangeLog, Region, RegionChangeLog, Country, CountryChangeLog
# Register your models here.



admin.site.register(Governorate)
admin.site.register(GovernorateChangeLog)


admin.site.register(Continent)
admin.site.register(ContinentChangeLog)

admin.site.register(Country)
admin.site.register(CountryChangeLog)

admin.site.register(Region)
admin.site.register(RegionChangeLog)
