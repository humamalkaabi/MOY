"""
URL configuration for ministry project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin  # استيراد وحدة إدارة الموقع من Django
from django.urls import path, include  # استيراد الدوال المسؤولة عن تعريف المسارات وربطها
from django.conf import settings  # استيراد إعدادات المشروع
from django.conf.urls.static import static  # استيراد الدالة المسؤولة عن إعداد المسارات للملفات الثابتة والإعلامية أثناء التطوير

#from django.conf.urls.i18n import urlpatterns as i18n_urlpatterns



from django.conf.urls import handler403
from core.views import custom_403  # استدعاء الدالة من تطبيق core

handler403 = 'core.views.custom_403'


urlpatterns = [
    path('admin/', admin.site.urls), # رابط لوحة التحكم
    path('', include('core.urls')), # رابط التطبيق

    
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
   
    path('personalinfo/', include('personalinfo.urls')),
    path('hrhub/', include('hrhub.urls')),
    path('rddepartment/', include('rddepartment.urls')),



    # # path('financialaffairs/', include('financialaffairs.urls')),
    
    path('locations/', include('locations.urls')),
    path('requests_app/', include('requests_app.urls')),
     
  
]


if settings.DEBUG:  # أثناء التطوير
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
   
    pass