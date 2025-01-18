from django.contrib import admin
from rddepartment.models.Education_Degree_Type import EducationDegreeType, EducationDegreeTypeChangeLog
from rddepartment.models.universities_models import College,CollegeChangeLog, IraqiUniversity, IraqiUniversityChangeLog, ForeignUniversity, ForeignUniversityChangeLog
from rddepartment.models.employee_education_models import EmployeeEducation, EmployeeEducationChangeLog
from rddepartment.models.course_certificate_models import CourseCertificateType, CourseCertificateTypeChangeLog, CourseCertificateInstitution, EmployeeCourseCertificate, EmployeeCourseCertificateChangeLog
# Register your models here.


########################### EducationDegreeType ##########################
admin.site.register(EducationDegreeType)
admin.site.register(EducationDegreeTypeChangeLog)



###################### Universities model #############################
admin.site.register(College)
admin.site.register(CollegeChangeLog)
admin.site.register(IraqiUniversity)
admin.site.register(IraqiUniversityChangeLog)
admin.site.register(ForeignUniversity)
admin.site.register(ForeignUniversityChangeLog)

###################### Employee education models #############################
admin.site.register(EmployeeEducation)
admin.site.register(EmployeeEducationChangeLog)


########################## Course certificate models #########################
admin.site.register(CourseCertificateType)
admin.site.register(CourseCertificateTypeChangeLog)
admin.site.register(CourseCertificateInstitution)
# admin.site.register(CourseCertificateInstitutionChangeLog)
admin.site.register(EmployeeCourseCertificate)
admin.site.register(EmployeeCourseCertificateChangeLog)



