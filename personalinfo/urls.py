from django.urls import path
from . import nationalism
# from .views import religion_change_log_list
from .import basicinfo
from .import religion
from . import officialdocumentstype
from . import additionainfo
from . import employeeofficialdocuments
from . import views


app_name = 'personalinfo'

urlpatterns = [

    ######################### main_personalinfo ##########################

    path('main_personalinfo/', views.main_personalinfo, name='main_personalinfo'),

    ############################### main_basicinfo ###############################
    path('mainbasicinfo/', basicinfo.mainbasicinfo, name='mainbasicinfo'),
    path('addbasicinfo/<slug:slug>/', basicinfo.addbasicinfo, name='addbasicinfo'),
    path('upload_basic_info_csv/', basicinfo.upload_basic_info_csv, name='upload_basic_info_csv'),
    path('download_sample_basic_info_csv/', basicinfo.download_sample_basic_info_csv, name='download_sample_basic_info_csv'),
    # path('employees/<slug:slug>/add_basic_info/', basicinfo.add_basic_info, name='add_basic_info'),
    path('basicinfodetail/<slug:slug>/', basicinfo.basicinfodetail, name='basicinfodetail'),
     path('updatebasicinfo/<slug:slug>/', basicinfo.updatebasicinfo, name='updatebasicinfo'),
    path('export_basic_info_to_csv/', basicinfo.export_basic_info_to_csv, name='export_basic_info_to_csv'),
    
    path('deletedetailsbasicinfo/<slug:slug>/', basicinfo.deletedetailsbasicinfo, name='deletedetailsbasicinfo'),

########################################### Update Basic info ##############################

    path('basicinfo/update_firstname/<slug:slug>/', basicinfo.update_firstname, name='update_firstname'),
    path('basicinfo/update_secondname/<slug:slug>/', basicinfo.update_secondname, name='update_secondname'),
    path('basicinfo/update_thirdname/<slug:slug>/', basicinfo.update_thirdname, name='update_thirdname'),
    path('basicinfo/update_fourthname/<slug:slug>/', basicinfo.update_fourthname, name='update_fourthname'),
    path('basicinfo/update_surname/<slug:slug>/', basicinfo.update_surname, name='update_surname'),
    path('basicinfo/update_mother_name/<slug:slug>/', basicinfo.update_mother_name, name='update_mother_name'),
    path('basicinfo/update_phone_number/<slug:slug>/', basicinfo.update_phone_number, name='update_phone_number'),
    path('basicinfo/update_email/<slug:slug>/', basicinfo.update_email, name='update_email'),
    path('update_date_of_birth/<slug:slug>/', basicinfo.update_date_of_birth, name='update_date_of_birth'),
    path('update_place_of_birth/<slug:slug>/', basicinfo.update_place_of_birth, name='update_place_of_birth'),
        path('update_gender/<slug:slug>/', basicinfo.update_gender, name='update_gender'),
            path('update_bio/<slug:slug>/', basicinfo.update_bio, name='update_bio'),
                path('update_avatar/<slug:slug>/', basicinfo.update_avatar, name='update_avatar'),





    ########################## Update Additional Info ############################
    path('update_blood_type/<slug:slug>/', additionainfo.update_blood_type, name='update_blood_type'),
    path('update_employee_religion/<slug:slug>/', additionainfo.update_employee_religion, name='update_employee_religion'),
    path('update_nationalism/<slug:slug>/', additionainfo.update_nationalism, name='update_nationalism'),
    path('update_marital_status/<slug:slug>/', additionainfo.update_marital_status, name='update_marital_status'),
    path('update_governorate_of_residence/<slug:slug>/', additionainfo.update_governorate_of_residence, name='update_governorate_of_residence'),
    path('update_address/<slug:slug>/', additionainfo.update_address, name='update_address'),
    path('update_emergency_contact/<slug:slug>/', additionainfo.update_emergency_contact, name='update_emergency_contact'),





    # path('basic-info/toggle-approval/<slug:slug>/', basicinfo.toggle_approval, name='toggle_approval'),
    #  path('export_basic_info_csv/', basicinfo.export_basic_info_csv, name='export_basic_info_csv'),



    

    # path('details_update_basic_info/<slug:slug>/', basicinfo.details_update_basic_info, name='details_update_basic_info'),

######################## Statistics ############################
    #  path('get_statistical_data/', basicinfo.get_statistical_data, name='get_statistical_data'),





    ################################ Update Basic Info ################################

    ###### Dash board ########
    # path('personalinfo/update_basic_info_dash_board/<slug:slug>/', basicinfo.update_basic_info_dash_board, name='update_basic_info_dash_board'),


    # path('basicinfo/update_firstname/<slug:slug>/', basicinfo.update_firstname, name='update_firstname'),
    # path('basicinfo/update_secondname/<slug:slug>/', basicinfo.update_secondname, name='update_secondname'),
    # path('basicinfo/update_thirdname/<slug:slug>/', basicinfo.update_thirdname, name='update_thirdname'),
    # path('basicinfo/update_fourthname/<slug:slug>/', basicinfo.update_fourthname, name='update_fourthname'),
    # path('basicinfo/update_surname/<slug:slug>/', basicinfo.update_surname, name='update_surname'),
    # path('basicinfo/update_mother_name/<slug:slug>/', basicinfo.update_mother_name, name='update_mother_name'),
    # path('basicinfo/update_phone_number/<slug:slug>/', basicinfo.update_phone_number, name='update_phone_number'),
    # path('basicinfo/update_email/<slug:slug>/', basicinfo.update_email, name='update_email'),
    # path('update_date_of_birth/<slug:slug>/', basicinfo.update_date_of_birth, name='update_date_of_birth'),
    # path('update_place_of_birth/<slug:slug>/', basicinfo.update_place_of_birth, name='update_place_of_birth'),
    #     path('update_gender/<slug:slug>/', basicinfo.update_gender, name='update_gender'),
    #         path('update_bio/<slug:slug>/', basicinfo.update_bio, name='update_bio'),
    #             path('update_avatar/<slug:slug>/', basicinfo.update_avatar, name='update_avatar'),

    ################################ additional  Info ################################
    



    # URL لعرض سجلات الحركة باستخدام الـ slug


    # ######################## Religion
    path('mainreligion/', religion.mainreligion, name='mainreligion'),
    path('add_religion/', religion.add_religion, name='add_religion'),
    path('religion_detail/<slug:slug>/', religion.religion_detail, name='religion_detail'),
    path('update_religion/<slug:slug>/', religion.update_religion, name='update_religion'),
    path('religion/delete/<slug:slug>/', religion.delete_religion, name='delete_religion'),
    path('export_religions_csv/', religion.export_religions_csv, name='export_religions_csv'),

    
    # path('religion/<slug:slug>/', religion_change_log_list, name='religion_change_logs'),
    #################### Religion Statistics #####################
    # path('export_religion_csv/', religion.export_religion_csv, name='export_religion_csv'),




    ############################## nationalism ##############################
    path('nationalism/<slug:slug>/logs/', nationalism.nationalism_change_logs, name='nationalism_change_logs'),
    path('main_nationalism/', nationalism.main_nationalism, name='main_nationalism'),
    path('nationalism/add/', nationalism.add_nationalism, name='add_nationalism'),
    path('nationalism_detail/<slug:slug>/', nationalism.nationalism_detail, name='nationalism_detail'),
    path('main_update_nationalism/<slug:slug>/', nationalism.main_update_nationalism, name='main_update_nationalism'),
    path('nationalism/delete/<slug:slug>/', nationalism.delete_nationalism, name='delete_nationalism'),
    path('export_nationalism_csv/', nationalism.export_nationalism_csv, name='export_nationalism_csv'),


     # #################### Additionalinfo ####################

    path('main_additionainfo/', additionainfo.main_additionainfo, name='main_additionainfo'),
    path('add_additional_info/<slug:slug>/', additionainfo.add_additional_info, name='add_additional_info'),
    path('additional_info_detail/<slug:slug>/',additionainfo.additional_info_detail, name='additional_info_detail'),
    path('update_additional_info/<slug:slug>/',additionainfo.update_additional_info, name='update_additional_info'),
    path('delete_additional_info/<slug:slug>/', additionainfo.delete_additional_info, name='delete_additional_info'),
    path('download_sample_additional_info_csv/', additionainfo.download_sample_additional_info_csv, name='download_sample_additional_info_csv'),
    path('upload_additionalinfo_csv/', additionainfo.upload_additional_info_csv, name='upload_additionalinfo_csv'),
    path('export_additional_info_to_csv/', additionainfo.export_additional_info_to_csv, name='export_additional_info_to_csv'),


    

    # path('export_additional_info_csv/', additionalInfo.export_additional_info_csv, name='export_additional_info_csv'),
    # path('download_sample_additional_info_csv/', additionalInfo.download_sample_additional_info_csv, name='download_sample_additional_info_csv'),
    # path('upload_additionalinfo_csv/', additionalInfo.upload_additional_info_csv, name='upload_additionalinfo_csv'),
    # path('additional_info_detail/<slug:slug>/',additionalInfo.additional_info_detail, name='additional_info_detail'),
    # path('update_additional_info/<slug:slug>/',additionalInfo.update_additional_info, name='update_additional_info'),
    # path('delete/<slug:slug>/', additionalInfo.delete_additional_info, name='delete_additional_info'),
    #     path('statistics_additional-info/', additionalInfo.additional_info_statistics_view, name='additional_info_statistics'),


    ########################## Update Additional Info ############################
    # path('update_blood_type/<slug:slug>/', additionalInfo.update_blood_type, name='update_blood_type'),
    # path('update_employee_religion/<slug:slug>/', additionalInfo.update_employee_religion, name='update_employee_religion'),
    # path('update_nationalism/<slug:slug>/', additionalInfo.update_nationalism, name='update_nationalism'),
    # path('update_marital_status/<slug:slug>/', additionalInfo.update_marital_status, name='update_marital_status'),
    # path('update_governorate_of_residence/<slug:slug>/', additionalInfo.update_governorate_of_residence, name='update_governorate_of_residence'),
    # path('update_address/<slug:slug>/', additionalInfo.update_address, name='update_address'),
    # path('update_emergency_contact/<slug:slug>/', additionalInfo.update_emergency_contact, name='update_emergency_contact'),


########################### Official Documents ##########################
    path('mainemployeeofficialdocuments/', employeeofficialdocuments.mainemployeeofficialdocuments, name='mainemployeeofficialdocuments'),
    path('addbasiadd_official_documentcinfo/<slug:slug>/', employeeofficialdocuments.add_official_document, name='add_official_document'),
    path('employee_documents/<slug:slug>/documents/', employeeofficialdocuments.employee_documents, name='employee_documents'),
    path('employee_documents_employee/<slug:slug>/documents/', employeeofficialdocuments.employee_documents_employee, name='employee_documents_employee'),


    path('edit_official_document/<slug:slug>/edit_document/', employeeofficialdocuments.edit_official_document, name='edit_official_document'),
    path('delete_official_document/<slug:slug>/delete_document/', employeeofficialdocuments.delete_official_document, name='delete_official_document'),
    path('upload_official_documents_csv/', employeeofficialdocuments.upload_official_documents_csv, name='upload_official_documents_csv'),
    path('download_sample_official_documents_csv/', employeeofficialdocuments.download_sample_official_documents_csv, name='download_sample_official_documents_csv'),
    path('export_official_documents_csv/', employeeofficialdocuments.export_official_documents_csv, name='export_official_documents_csv'),




    ####################### Official Documents Type #######################
    path('main_official_documents_type/', officialdocumentstype.main_official_documents_type, name='main_official_documents_type'),
    path('add_official_document/', officialdocumentstype.add_official_document, name='add_official_document'),
    path('document_detail/<slug:slug>/', officialdocumentstype.document_detail, name='document_detail'),
    path('update_official_document/<slug:slug>/', officialdocumentstype.update_official_document, name='update_official_document'),
    path('delete_official_document_type/<slug:slug>/', officialdocumentstype.delete_official_document_type, name='delete_official_document_type'),
    path('export_official_documents_csv/', officialdocumentstype.export_official_documents_csv, name='export_official_documents_csv'),




    #     path('download_sample_official_documents_csv/', officialdocuments.download_sample_official_documents_csv, name='download_sample_official_documents_csv'),
    #         path('upload_official_documents_csv/', officialdocuments.upload_official_documents_csv, name='upload_official_documents_csv'),
    #         path('export_official_documents_csv/', officialdocuments.export_official_documents_csv, name='export_official_documents_csv'),
    #         path('all_official_documents/', officialdocuments.all_official_documents, name='all_official_documents'),
    #     path('export_official_documents_csv/', officialdocuments.export_official_documents_csv, name='export_official_documents_csv'),
    # path('official_documents_statistics/', officialdocuments.official_documents_statistics_view, name='official_documents_statistics'),












]
