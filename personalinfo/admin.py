from django.contrib import admin
from .models import BasicInfo,BasicInfoChangeLog, Nationalism,NationalismChangeLog, Religion,ReligionChangeLog, AdditionalInfo,AdditionalInfoChangeLog, OfficialDocuments,OfficialDocumentsTypeChangeLog,Official_Documents_Type,OfficialDocumentsChangeLog
# Register your models here.


admin.site.register(BasicInfo)
admin.site.register(BasicInfoChangeLog)
admin.site.register(Nationalism)
admin.site.register(NationalismChangeLog)
admin.site.register(Religion)
admin.site.register(ReligionChangeLog)
admin.site.register(AdditionalInfo)
admin.site.register(AdditionalInfoChangeLog)
admin.site.register(OfficialDocuments)
admin.site.register(OfficialDocumentsTypeChangeLog)
admin.site.register(Official_Documents_Type)
admin.site.register(OfficialDocumentsChangeLog)

