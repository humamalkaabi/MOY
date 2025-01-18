from django.urls import path

from . import views
from . import governorate
from . import region
from . import continent
from . import country



app_name = 'locations' 

urlpatterns = [
    
    #### Views 
    path('main_locations_dashboard/', views.main_locations_dashboard, name='main_locations_dashboard'),

    #### Governorate
    path('governorate_create/', governorate.create_governorate, name='governorate_create'),
    path('governorate_statistics/', governorate.governorate_statistics, name='governorate_statistics'),
    path('export_governorates_csv/', governorate.export_governorates_csv, name='export_governorates_csv'),
    path('governorates/<slug:slug>/', governorate.governorate_detail, name='governorate_detail'),
    path('governorates/<slug:slug>/update/', governorate.update_governorate, name='update_governorate'),
    path('governorates/<slug:slug>/delete/', governorate.delete_governorate, name='delete_governorate'),
    path('download_sample_governorates_csv/', governorate.download_sample_governorates_csv, name='download_sample_governorates_csv'),
    path('upload_governorates_csv/', governorate.upload_governorates_csv, name='upload_governorates_csv'),
    path('download_all_governorates_csv/', governorate.download_all_governorates_csv, name='download_all_governorates_csv'),



    
    #### Region

   path('create_region/', region.create_region, name='create_region'),
   path('region_statistics/', region.region_statistics, name='region_statistics'),
   path('export_regions_csv/', region.export_regions_csv, name='export_regions_csv'),
    path('regions/<slug:slug>/', region.region_detail, name='region_detail'),

    path('regions/<slug:slug>/update/', region.update_region, name='update_region'),

    path('regions/<slug:slug>/delete/', region.delete_region, name='delete_region'),
     path('download_sample_regions_csv/', region.download_sample_regions_csv, name='download_sample_regions_csv'),
    path('upload_regions_csv/', region.upload_regions_csv, name='upload_regions_csv'),
    path('export_all_regions_csv/', region.export_all_regions_csv, name='export_all_regions_csv'),



   ##### Continent
   path('create_continent/', continent.create_continent, name='create_continent'),
   path('continent_statistics/', continent.continent_statistics, name='continent_statistics'),
   path('export_continents_csv/', continent.export_continents_csv, name='export_continents_csv'),
  path('continents/<slug:slug>/', continent.continent_detail, name='continent_detail'),
  path('continents/<slug:slug>/update/', continent.update_continent, name='update_continent'),
  path('continents/<slug:slug>/delete/', continent.delete_continent, name='delete_continent'),
     path('export_all_continents_csv/', continent.export_all_continents_csv, name='export_all_continents_csv'),



   


   #### Country
   path('create_country/', country.create_country, name='create_country'),
   path('country_statistics/', country.country_statistics, name='country_statistics'),
    path('export_countries_csv/', country.export_countries_csv, name='export_countries_csv'),
     path('countries/<slug:slug>/', country.country_detail, name='country_detail'),
    
    path('countries/<slug:slug>/update/', country.update_country, name='update_country'),
    
    path('countries/<slug:slug>/delete/', country.delete_country, name='delete_country'),
    path('download_sample_countries_csv/', country.download_sample_countries_csv, name='download_sample_countries_csv'),
    path('upload_countries_csv/', country.upload_country_csv, name='upload_countries_csv'),
        path('export_all_countries_csv/', country.export_all_countries_csv, name='export_all_countries_csv'),



    



]
