from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.db.models import Count
from .models import Governorate, Region, Continent, Country

def main_locations_dashboard(request):
    total_governorates = Governorate.objects.count()

    # Query to get governorates with the most regions
   
    # Query to get the total number of regions
    total_regions = Region.objects.count()

    # Query to get the total number of continents
    total_continents = Continent.objects.count()

    # Query to get the total number of countries
    total_countries = Country.objects.count()

    # Query to get the most recent governorates
    recent_governorates = Governorate.objects.order_by('-created_at')[:1]


    recent_regions = Region.objects.order_by('-created_at')[:1]

    recent_continents = Continent.objects.order_by('-created_at')[:1]

    recent_countries = Country.objects.order_by('-created_at')[:1]

    context = {
        'total_governorates': total_governorates,
        
        'total_regions': total_regions,
        'total_continents': total_continents,
        'total_countries': total_countries,
        'recent_governorates': recent_governorates,
        'recent_regions': recent_regions,
        'recent_countries': recent_countries,
        'recent_continents': recent_continents,
    }

    return render(request, 'locations/main_locations_dashboard.html', context)
