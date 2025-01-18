from django.urls import path
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth import views as auth_views

from . import views
from . import foreignuniversity
from . import  college
from . import iraqiuniversity
from . import  employeeeducation
from . import coursecertificatetype
from . import educationdegreetype
from . import employeecoursecertificate


app_name = 'rddepartment'



urlpatterns = [

    # #### views
    path('main_rddepartment/', views.main_rddepartment, name='main_rddepartment'),
    



    # # #### main_Education_Degree_Type
    path('main_education_degree_type/', educationdegreetype.main_education_degree_type, name='main_education_degree_type'),
    path('add_education_degree_type/', educationdegreetype.add_education_degree_type, name='add_education_degree_type'),
    path('education_degree_type_detail/<slug:slug>/', educationdegreetype.education_degree_type_detail, name='education_degree_type_detail'),
    path('update_education_degree_type/<slug:slug>/', educationdegreetype.update_education_degree_type, name='update_education_degree_type'),
    path('delete_education_degree_type/<slug:slug>/', educationdegreetype.delete_education_degree_type, name='delete_education_degree_type'),
     path('export_education_degree_type_to_csv/', educationdegreetype.export_education_degree_type_to_csv, name='export_education_degree_type_to_csv'),


     # ################## college ##################

    path('main_college/', college.main_college, name='main_college'),
    path('add_college/', college.add_college, name='add_college'),
    path('college_detail/<slug:slug>/', college.college_detail, name='college_detail'),
    path('update_college/<slug:slug>/', college.update_college, name='update_college'),
    path('delete_college/<slug:slug>/', college.delete_college, name='delete_college'),
    path('export_college_to_csv/', college.export_college_to_csv, name='export_college_to_csv'),



    ############# Foreignuniversity.py
    path('main_foreignuniversity/', foreignuniversity.main_foreignuniversity, name='main_foreignuniversity'),
    path('add_foreignuniversity/', foreignuniversity.add_foreignuniversity, name='add_foreignuniversity'),
    path('get_countries_by_continent/', foreignuniversity.get_countries_by_continent, name='get_countries_by_continent'),
    path('foreignuniversitys_detail/<slug:slug>/', foreignuniversity.foreignuniversitys_detail, name='foreignuniversitys_detail'),
    path('update_foreignuniversitys/<slug:slug>/', foreignuniversity.update_foreignuniversitys, name='update_foreignuniversitys'),
    path('delete_foreignuniversity/<slug:slug>/', foreignuniversity.delete_foreignuniversity, name='delete_foreignuniversity'),
    path('download_sample_foreign_universities_csv', foreignuniversity.download_sample_foreign_universities_csv, name='download_sample_foreign_universities_csv'),
    path('upload_foreign_university_csv', foreignuniversity.upload_foreign_university_csv, name='upload_foreign_university_csv'),

    # path('get_countries_by_continent/<int:continent_id>/', foreignuniversity.get_countries_by_continent, name='get_countries_by_continent'),




   

    # ################### Iraqiuniversity ##################
    path('main_iraqiuniversity/', iraqiuniversity.main_iraqiuniversity, name='main_iraqiuniversity'),
    path('add_iraqiuniversity/', iraqiuniversity.add_iraqiuniversity, name='add_iraqiuniversity'),
    path('upload_iraqi_university_csv/', iraqiuniversity.upload_iraqi_university_csv, name='upload_iraqi_university_csv'),
    path('download_sample_iraqi_university_csv/', iraqiuniversity.download_sample_iraqi_university_csv, name='download_sample_iraqi_university_csv'),
    path('iraqiuniversity_detail/<slug:slug>/', iraqiuniversity.iraqiuniversity_detail, name='iraqiuniversity_detail'),
    path('update_iraqiuniversity/<slug:slug>/', iraqiuniversity.update_iraqiuniversity, name='update_iraqiuniversity'),
    path('delete_iraqiuniversity/<slug:slug>/', iraqiuniversity.delete_iraqiuniversity, name='delete_iraqiuniversity'),
     path('export_iraqi_university_to_csv/', iraqiuniversity.export_iraqi_university_to_csv, name='export_iraqi_university_to_csv'),
    




    # ###############     employeeeducation
    path('main_employeeeducation/', employeeeducation.main_employeeeducation, name='main_employeeeducation'),
    path('add_employeeeducation/<slug:slug>/', employeeeducation.add_employeeeducation, name='add_employeeeducation'),
    path('employeeeducation_detail/<slug:slug>/', employeeeducation.employeeeducation_detail, name='employeeeducation_detail'),
    path('employeeeducation_detail_employee/<slug:slug>/', employeeeducation.employeeeducation_detail_employee, name='employeeeducation_detail_employee'),

    

    
    path('employee_cer_education_detail/<slug:slug>/', employeeeducation.employee_cer_education_detail, name='employee_cer_education_detail'),
    path('update_employeeeducation/<slug:slug>/', employeeeducation.update_employeeeducation, name='update_employeeeducation'),
    path('delete_employee_education/<slug:slug>/', employeeeducation.delete_employee_education, name='delete_employee_education'),

    path('download_employee_education_sample_csv/', employeeeducation.download_employee_education_sample_csv, name='download_employee_education_sample_csv'),
    path('upload_employee_education_csv/', employeeeducation.upload_employee_education_csv, name='upload_employee_education_csv'),
    path('export_filtered_employee_education_csv/', employeeeducation.export_filtered_employee_certificates_csv, name='export_filtered_employee_education_csv'),
    # path('employeeeducation_employee_detail/<slug:employee_slug>/', employeeeducation.employeeeducation_employee_detail, name='employee_education_detail'),
    # path('export_employeeeducation_csv/', employeeeducation.export_employeeeducation_csv, name='export_employeeeducation_csv'),
    # path('employeeeducationstatistics/', employeeeducation.employeeeducationstatistics, name='employeeeducationstatistics'),
    # path('employee_certificates_view/<slug:slug>/certificates/', employeeeducation.employee_certificates_view, name='employee_certificates_view'),



    # ################### coursecertificatetype
    path('main_coursecertificatetype/', coursecertificatetype.main_coursecertificatetype, name='main_coursecertificatetype'),
    path('add_coursecertificatetype/', coursecertificatetype.add_coursecertificatetype, name='add_coursecertificatetype'),
    path('coursecertificatetype_detail/<slug:slug>/', coursecertificatetype.coursecertificatetype_detail, name='coursecertificatetype_detail'),
    path('update_coursecertificatetype/<slug:slug>/', coursecertificatetype.update_coursecertificatetype, name='update_coursecertificatetype'),
    path('delete_coursecertificatetype/<slug:slug>/', coursecertificatetype.delete_coursecertificatetype, name='delete_coursecertificatetype'),

    # #####
    path('main_coursecertificateinstitutions/', coursecertificatetype.main_coursecertificateinstitutions, name='main_coursecertificateinstitutions'),
    path('add_coursecertificateinstitutions/', coursecertificatetype.add_coursecertificateinstitutions, name='add_coursecertificateinstitutions'),
    path('coursecertificateinstitution_detail/<slug:slug>/', coursecertificatetype.coursecertificateinstitution_detail, name='coursecertificateinstitution_detail'),
    path('update_coursecertificateinstitution/<slug:slug>/', coursecertificatetype.update_coursecertificateinstitution, name='update_coursecertificateinstitution'),
    path('delete_coursecertificateinstitution/<slug:slug>/', coursecertificatetype.delete_coursecertificateinstitution, name='delete_coursecertificateinstitution'),
    # #####

      path('mainemployeecoursecertificate/', employeecoursecertificate.mainemployeecoursecertificate, name='mainemployeecoursecertificate'),
      path('add_employeecoursecertificate/<slug:slug>/', employeecoursecertificate.add_employeecoursecertificate, name='add_employeecoursecertificate'),
      path('all_employee_certificates/<slug:slug>/', employeecoursecertificate.all_employee_certificates, name='all_employee_certificates'),
      path('all_employee_certificates_employee/<slug:slug>/', employeecoursecertificate.all_employee_certificates_employee, name='all_employee_certificates_employee'),
      path('download_sample_employee_course_certificate_csv/', employeecoursecertificate.download_sample_employee_course_certificate_csv, name='download_sample_employee_course_certificate_csv'),
      path('upload_employee_course_certificate_csv/', employeecoursecertificate.upload_employee_course_certificate_csv, name='upload_employee_course_certificate_csv'),
      path('export_filtered_employee_certificates_csv/', employeecoursecertificate.export_filtered_employee_certificates_csv, name='export_filtered_employee_certificates_csv'),





      
     path('update_employeecoursecertificate/<slug:slug>/', employeecoursecertificate.update_employeecoursecertificate, name='update_employeecoursecertificate'),
     path('delete_employeecoursecertificate/<slug:slug>/', employeecoursecertificate.delete_employeecoursecertificate, name='delete_employeecoursecertificate'),
#      path('download_sample_employee_course_certificate_csv/', coursecertificatetype.download_sample_employee_course_certificate_csv, name='download_sample_employee_course_certificate_csv'),
#      path('upload_employee_course_certificate_csv/', coursecertificatetype.upload_employee_course_certificate_csv, name='upload_employee_course_certificate_csv'),
# path('employee/<slug:slug>/course-certificates/', coursecertificatetype.employee_course_certificates, name='employee_course_certificates'),





   
    
]

