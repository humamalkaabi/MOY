from django.urls import path
from . import views
from . import employeegradestep
from . import employement
from . import thanks
from . import punishments
from . import leave
from . import jobtitle
from . import duty_assignment_order 
from . import places_of_employment
from . import placement
from . import office_positions
from . import staffing_structure
from . import central_alloc
from . import employmenthistory
from . import absences
from . import employee_office

app_name = 'hrhub'
urlpatterns = [

     path('main_hrhub/', views.main_hrhub, name='main_hrhub'),

   
    ##########################  Job Title ###########################

    path('main_job_title/', jobtitle.main_job_title, name='main_job_title'),
    path('sub_job_titles/<slug:parent_slug>/', jobtitle.sub_job_titles, name='sub_job_titles'),
    path('add_job_title/', jobtitle.add_job_title, name='add_job_title'),
    path('update_job_title/<slug:slug>/', jobtitle.update_job_title, name='update_job_title'),  # تعديل هنا لاستخدام slug
    path('job_title_detail/<slug:slug>/', jobtitle.job_title_detail, name='job_title_detail'),  # مسار عرض التفاصيل
    path('job_title/delete/<slug:slug>/', jobtitle.delete_job_title, name='delete_job_title'),
        path('upload_job_titles_csv/', jobtitle.upload_job_titles_csv, name='upload_job_titles_csv'),

    
                    ###### Emplyee job title #######
    path('main_employee_job_title/', jobtitle.main_employee_job_title, name='main_employee_job_title'),
   
    path('create_employee_job_title/create/<slug:slug>/', jobtitle.create_employee_job_title, name='create_employee_job_title'),
    path('get-child-job-titles/<int:parent_id>/', jobtitle.get_child_job_titles, name='get_child_job_titles'),
    path('get-related-job-titles/<int:job_title_id>/', jobtitle.get_related_job_titles, name='get_related_job_titles'),
    path('employee_job_titles/<slug:slug>/', jobtitle.employee_job_titles, name='employee_job_titles'),

    path('employee_job_titlesemployee/<slug:slug>/', jobtitle.employee_job_titlesemployee, name='employee_job_titlesemployee'),

    path('update_employee_job_title/<slug:slug>/', jobtitle.update_employee_job_title, name='update_employee_job_title'),
    path('delete_employee_job_title/<slug:slug>/', jobtitle.delete_employee_job_title, name='delete_employee_job_title'),
    path('update_employee_job_title_settings/', jobtitle.update_employee_job_title_settings, name='update_employee_job_title_settings'),
    path('upload_employee_job_titles_csv/', jobtitle.upload_employee_job_titles_csv, name='upload_employee_job_titles_csv'),
    path('employee_job_title_detail/<slug:slug>/', jobtitle.employee_job_title_detail, name='employee_job_title_detail'),

    path('update_employee_job_title_settings/', jobtitle.update_employee_job_title_settings, name='update_employee_job_title_settings'),




#     #######################  Duty assignment order ########################

    path('main_duty_assignment_order/', duty_assignment_order.main_duty_assignment_order, name='main_duty_assignment_order'),
    path('add_duty_assignment_order/', duty_assignment_order.add_duty_assignment_order, name='add_duty_assignment_order'),
    path('duty_assignment_order_detail/<slug:slug>/', duty_assignment_order.duty_assignment_order_detail, name='duty_assignment_order_detail'),  # مسار عرض التفاصيل
    path('update_duty_assignment_order/<slug:slug>/', duty_assignment_order.update_duty_assignment_order, name='update_duty_assignment_order'),  # تعديل هنا لاستخدام slug
    path('delete_duty_assignment_order/<slug:slug>/', duty_assignment_order.delete_duty_assignment_order, name='delete_duty_assignment_order'), 



 ############################################## employeegradestep #######################
                ############### Grade ################
     path('main_employee_grade/', employeegradestep.main_employee_grade, name='main_employee_grade'),
      path('employee_grade_create/', employeegradestep.employee_grade_create, name='employee_grade_create'),
      path('grade_detail/<slug:slug>/',employeegradestep.grade_detail, name='grade_detail'),
    path('update_employee_grade/<slug:slug>/',employeegradestep.update_employee_grade, name='update_employee_grade'),
    path('delete_employee_grade/<slug:slug>/',employeegradestep.delete_employee_grade, name='delete_employee_grade'),
         path('upload_employee_grades_csv/', employeegradestep.upload_employee_grades_csv, name='upload_employee_grades_csv'),

    
    
#                 ############### Step ################   
    path('main_employee_step/', employeegradestep.main_employee_step, name='main_employee_step'),
    path('employee_step_create/', employeegradestep.employee_step_create, name='employee_step_create'),
    path('step_detail/<slug:slug>/', employeegradestep.step_detail, name='step_detail'),
    path('update_employee_step/<slug:slug>/update/', employeegradestep.update_employee_step, name='update_employee_step'),
    path('delete_employee_step/<slug:slug>/delete/', employeegradestep.delete_employee_step, name='delete_employee_step'),
        path('upload_employee_steps_csv/', employeegradestep.upload_employee_steps_csv, name='upload_employee_steps_csv'),


#     ####################### Thankks #######################
        path('main_employeethanks/', thanks.main_employeethanks, name='main_employeethanks'),
        path('add_thanks_to_employees/', thanks.add_thanks_to_employees, name='add_thanks_to_employees'),
        path('save_thanks/', thanks.save_thanks, name='save_thanks'),
        path('employee_thanks_list/<slug:slug>/', thanks.employee_thanks_list, name='employee_thanks_list'),

        path('employee_thanks_listemployee/<slug:slug>/', thanks.employee_thanks_listemployee, name='employee_thanks_listemployee'),

        path('delete_employee_thanks/<slug:slug>/', thanks.delete_employee_thanks, name='delete_employee_thanks'),
        path('update_employee_thanks/<slug:slug>/', thanks.update_employee_thanks, name='update_employee_thanks'),
        path('upload_employee_thanks_csv/', thanks.upload_employee_thanks_csv, name='upload_employee_thanks_csv'),
        path('download_thanks_csv_template/', thanks.download_thanks_csv_template, name='download_thanks_csv_template'),

#     path('employee/<slug:slug>/thanks/', thanks.employee_thanks_view, name='employee_thanks_view'),

    path('main_thanks_type/', thanks.main_thanks_type, name='main_thanks_type'),
    path('add_thanks_type/', thanks.add_thanks_type, name='add_thanks_type'),
    path('update_thanks_type/<slug:slug>/', thanks.update_thanks_type, name='update_thanks_type'),  # تعديل هنا لاستخدام slug
    path('thanks_type_detail/<slug:slug>/', thanks.thanks_type_detail, name='thanks_type_detail'),  # مسار عرض التفاصيل
    path('delete_thanks_type/delete/<slug:slug>/', thanks.delete_thanks_type, name='delete_thanks_type'),



#     ######################## Punishments #######################


         path('main_punishment_types/', punishments.main_punishment_types, name='main_punishment_types'),
         path('add_punishment_type/', punishments.add_punishment_type, name='add_punishment_type'),
         path('punishment_type_detail/<slug:slug>/', punishments.punishment_type_detail, name='punishment_type_detail'),
         path('update_punishment_type/<slug:slug>/edit/', punishments.update_punishment_type, name='update_punishment_type'),
         path('delete_punishment_type/<slug:slug>/delete/', punishments.delete_punishment_type, name='delete_punishment_type'),

         ############## Employee ##########
        path('main_employee_punishments/', punishments.main_employee_punishments, name='main_employee_punishments'),
        path('add_punishments_to_employees/', punishments.add_punishments_to_employees, name='add_punishments_to_employees'),
        path('save_punishments/', punishments.save_punishments, name='save_punishments'),
        path('employee_punishments_list/<slug:slug>/', punishments.employee_punishments_list, name='employee_punishments_list'),

        path('employee_punishments_listemployee/<slug:slug>/', punishments.employee_punishments_listemployee, name='employee_punishments_listemployee'),
        path('download_punishment_csv_template/', punishments.download_punishment_csv_template, name='download_punishment_csv_template'),



        path('delete_employee_punishment/<slug:slug>/', punishments.delete_employee_punishment, name='delete_employee_punishment'),
    path('update_employee_punishment/<slug:slug>/', punishments.update_employee_punishment, name='update_employee_punishment'),
    path('upload_employee_punishment_csv/', punishments.upload_employee_punishment_csv, name='upload_employee_punishment_csv'),


    


         

    
#     ######################## Leave #######################

#     ################## Leave type
     path('main_leave_type/', leave.main_leave_type, name='main_leave_type'),
     path('add_leave_type/', leave.add_leave_type, name='add_leave_type'),
     path('leave_type/<slug:slug>/', leave.leave_type_detail, name='leave_type_detail'),
     path('update_leave_type/<slug:slug>/', leave.update_leave_type, name='update_leave_type'),
      path('delete_leave_type/<slug:slug>/', leave.delete_leave_type, name='delete_leave_type'),

#      ################### Leave Balane #######################
       path('main_leave_balance/', leave.main_leave_balance, name='main_leave_balance'),
       path('create_leave_balance/<slug:slug>/', leave.create_leave_balance, name='create_leave_balance'),
       path('employee_leave_balances/<slug:slug>/', leave.employee_leave_balances, name='employee_leave_balances'),
       path('update_leave_balance_view/<slug:slug>/', leave.update_leave_balance_view, name='update_leave_balance_view'),
       path('delete_leave_balance/<slug:slug>/', leave.delete_leave_balance, name='delete_leave_balance'),
        path('upload_leave_balance_csv/', leave.upload_leave_balance_csv, name='upload_leave_balance_csv'),



       
       ################### Leave Employee #######################
       path('main_leave_request/', leave.main_leave_request, name='main_leave_request'),
       path('employee_leave_requests/<slug:slug>/', leave.employee_leave_requests, name='employee_leave_requests'),


        path('employee_leave_requestsemployee/<slug:slug>/', leave.employee_leave_requestsemployee, name='employee_leave_requestsemployee'),

       path('create_leave_request/<slug:slug>/', leave.create_leave_request, name='create_leave_request'),
       path('leave_request_detail/<slug:slug>/', leave.leave_request_detail, name='leave_request_detail'),
       path('update_leave_request/<slug:slug>/', leave.update_leave_request, name='update_leave_request'),
       path('delete_leave_request/<slug:slug>/', leave.delete_leave_request, name='delete_leave_request'),
        path('upload_leave_requests_csv/', leave.upload_leave_requests_csv, name='upload_leave_requests_csv'),
        path('download_leave_balance_csv_template/', leave.download_leave_balance_csv_template, name='download_leave_balance_csv_template'),
        path('download_leave_requests_csv_template/', leave.download_leave_requests_csv_template, name='download_leave_requests_csv_template'),





#     ########################### Places of employment #############################

        path('list_places_of_employment/', places_of_employment.list_places_of_employment, name='list_places_of_employment'),
        path('list_children_of_employment/<slug:parent_slug>/children/', places_of_employment.list_children_of_employment, name='list_children_of_employment'),
        path('place_of_employment_detail/<slug:slug>/', places_of_employment.place_of_employment_detail, name='place_of_employment_detail'),
        path('add_place_of_employment/', places_of_employment.add_place_of_employment, name='add_place_of_employment'),
        path('update_place_of_employment/<slug:slug>/update/', places_of_employment.update_place_of_employment, name='update_place_of_employment'),
        path('delete_place_of_employment/<slug:slug>/delete/', places_of_employment.delete_place_of_employment, name='delete_place_of_employment'),
        path('upload_place_of_employment_csv/', places_of_employment.upload_place_of_employment_csv, name='upload_place_of_employment_csv'),


        
#         #################### Placement ############################

        path('main_placement/', placement.main_placement, name='main_placement'),
        path('placement_detail/<slug:slug>/', placement.placement_detail, name='placement_detail'),
        path('add_placement/<slug:slug>/', placement.add_placement, name='add_placement'),
         path('all_placement_detail/detail/<slug:slug>/', placement.all_placement_detail, name='all_placement_detail'),

        path('all_placement_detailemployee/detail/<slug:slug>/', placement.all_placement_detailemployee, name='all_placement_detailemployee'),


        path('update_placement/<slug:placement_slug>/', placement.update_placement, name='update_placement'),
        path('delete_placement/<slug:placement_slug>/', placement.delete_placement, name='delete_placement'),
         path('upload_placement_csv/', placement.upload_placement_csv, name='upload_placement_csv'),
       


#     ################################################ Employee Office  ###############################

    path('main_offices/', employee_office.main_offices, name='main_offices'),
    path('add_office/', employee_office.add_office, name='add_office'),
    path('office_detail/<slug:slug>/', employee_office.office_detail, name='office_detail'),  # مسار عرض التفاصيل
    path('update_office/<slug:slug>/', employee_office.update_office, name='update_office'),  # تعديل هنا لاستخدام slug
    path('delete_office/<slug:slug>/', employee_office.delete_office, name='delete_office'),
     path('upload_offices_csv/', employee_office.upload_offices_csv, name='upload_offices_csv'),
     path('download_offices_csv_template/', employee_office.download_offices_csv_template, name='download_offices_csv_template'),
    # path('update_employee_office/<slug:slug>/', employee_office.update_employee_office, name='update_employee_office'),




                                ############ Employee ###################
     path('mainemployeeoffice/', employee_office.mainemployeeoffice, name='mainemployeeoffice'),
     path('upload_employees_csv/', employee_office.upload_employees_csv, name='upload_employees_csv'),
      path('download_employee_offices_csv_template/', employee_office.download_employee_offices_csv_template, name='download_employee_offices_csv_template'),
       path('add_employee_office/<slug:slug>/', employee_office.add_employee_office, name='add_employee_office'),
    path('ajax_load_emplloyee_offices/', employee_office.load_emplloyee_offices, name='ajax_load_emplloyee_offices'),

    path('employee_offices_view/<slug:slug>/', employee_office.employee_offices_view, name='employee_offices_view'),

    path('employee_offices_viewemployee/<slug:slug>/', employee_office.employee_offices_viewemployee, name='employee_offices_viewemployee'),



    path('employee_office/update/<slug:slug>/', employee_office.update_employee_office, name='update_employee_office'),
    path('employee_office/<slug:slug>/', employee_office.delete_employee_office, name='delete_employee_office'),





#     ##############################################  Position ##############################################
    
    path('main_position/', office_positions.main_position, name='main_position'),
    path('add_position/', office_positions.add_position, name='add_position'),
    path('position_detail/<slug:slug>/', office_positions.position_detail, name='position_detail'),  # مسار عرض التفاصيل
    path('update_position/<slug:slug>/', office_positions.update_position, name='update_position'),  # تعديل هنا لاستخدام slug
    path('delete_position/<slug:slug>/', office_positions.delete_position, name='delete_position'),
        path('upload_positions_csv/', office_positions.upload_positions_csv, name='upload_positions_csv'),



#     ################## main_office_positions
     path('main_office_positions/', office_positions.main_office_positions, name='main_office_positions'),
    path('list_employee_office_positions/<slug:slug>/', office_positions.list_employee_office_positions, name='list_employee_office_positions'),

    path('list_employee_office_positionsemployee/<slug:slug>/', office_positions.list_employee_office_positionsemployee, name='list_employee_office_positionsemployee'),

        path('upload_employee_office_position_csv/', office_positions.upload_employee_office_position_csv, name='upload_employee_office_position_csv'),



     path('add_employee_office_position/<slug:slug>/', office_positions.add_employee_office_position, name='add_employee_office_position'),
    path('office_position_detail/<slug:slug>/', office_positions.office_position_detail, name='office_position_detail'),
        path('update_employee_office_position/<slug:slug>/', office_positions.update_employee_office_position, name='update_employee_office_position'),
    path('delete_employee_office_position/<slug:slug>/', office_positions.delete_employee_office_position, name='delete_employee_office_position'),


############################################### Staffing Structure #########################################

    path('main_payroll_budget/', staffing_structure.main_payroll_budget, name='main_payroll_budget'),
    path('add_payroll_budget/', staffing_structure.add_payroll_budget, name='add_payroll_budget'),
    path('update_payroll_budget/<slug:slug>/', staffing_structure.update_payroll_budget, name='update_payroll_budget'),
    path('delete_payroll_budget/<slug:slug>/', staffing_structure.delete_payroll_budget, name='delete_payroll_budget'),
    
    path('main_staff_structer_type/', staffing_structure.main_staff_structer_type, name='main_staff_structer_type'),
    path('add_staff_structer_type/', staffing_structure.add_staff_structer_type, name='add_staff_structer_type'),
    path('update_staff_structer_type/<slug:slug>/', staffing_structure.update_staff_structer_type, name='update_staff_structer_type'),
    path('delete_staff_structer_type/<slug:slug>/', staffing_structure.delete_staff_structer_type, name='delete_staff_structer_type'),
    

    
############################################################### Employee Staffing Structure #############################
    path('main_staff_employee_list/', staffing_structure.main_staff_employee_list, name='main_staff_employee_list'),
    path('add_employee_staff_kind/<slug:slug>/', staffing_structure.add_employee_staff_kind, name='add_employee_staff_kind'),
    path('employee_staff_list/<slug:slug>/', staffing_structure.employee_staff_list, name='employee_staff_list'),
    path('update_employee_staff_kind/<slug:slug>/', staffing_structure.update_employee_staff_kind, name='update_employee_staff_kind'),
    path('delete_employee_staff_kind/<slug:slug>/', staffing_structure.delete_employee_staff_kind, name='delete_employee_staff_kind'),
    path('employee_staff_detail/<slug:slug>/', staffing_structure.employee_staff_detail, name='employee_staff_detail'),
     path('upload_employee_staff_kind_csv/', staffing_structure.upload_employee_staff_kind_csv, name='upload_employee_staff_kind_csv'),




    
# ########## Central Financial Allocation ##################

     path('main_central_financial_allocations/', central_alloc.main_central_financial_allocations, name='main_central_financial_allocations'),
     path('add_central_financial_allocation/', central_alloc.add_central_financial_allocation, name='add_central_financial_allocation'),
     path('update_central_financial_allocation/<slug:slug>/', central_alloc.update_central_financial_allocation, name='update_central_financial_allocation'),
     path('delete_central_financial_allocation/<slug:slug>/', central_alloc.delete_central_financial_allocation, name='delete_central_financial_allocation'),
    path('upload_financial_allocations_csv/', central_alloc.upload_financial_allocations_csv, name='upload_financial_allocations_csv'),



                    ########## Employee Central Financial Allocation ##################
     path('central_alloc_employee_list/', central_alloc.central_alloc_employee_list, name='central_alloc_employee_list'),
     path('add_financial_allocations/<slug:slug>/add_allocations/', central_alloc.add_financial_allocations, name='add_financial_allocations'),
    path('employee_allocations/<slug:slug>/', central_alloc.employee_allocations, name='employee_allocations'),
    path('update_financial_allocation/<slug:slug>/', central_alloc.update_financial_allocation, name='update_financial_allocation'),
    path('delete_financial_allocation/<slug:slug>/', central_alloc.delete_financial_allocation, name='delete_financial_allocation'),
        path('central_financial_allocations_detail/<slug:slug>/', central_alloc.central_financial_allocations_detail, name='central_financial_allocations_detail'),

# ######################## Employee history #####################

#     path('employment_statistics/', employmenthistory.employment_statistics, name='employment_statistics'),



#     path('update_settings/', employeegradestep.update_settings, name='update_settings'),

     path('main_employee_grade_step/', employeegradestep.main_employee_grade_step, name='main_employee_grade_step'),
    #  path('view_employee_grade_step_settings/', employeegradestep.view_employee_grade_step_settings, name='view_employee_grade_step_settings'),
    path('employee_grade_step_detail/<slug:slug>/', employeegradestep.employee_grade_step_detail, name='employee_grade_step_detail'),

     path('update_employee_grade_step_settings/', employeegradestep.update_employee_grade_step_settings, name='update_employee_grade_step_settings'),
         path('employeegradestep/add/<slug:slug>/', employeegradestep.add_employee_grade_step, name='add_employee_grade_step'),

    #  path('add_employee_grade_step/<slug:slug>//', employeegradestep.add_employee_grade_step, name='add_employee_grade_step'),


#     path('employee-grade-step/add/<slug:slug>/', employeegradestep.employee_grade_step_create, name='employee_grade_step_create'),
#     path('employeegradestep/<slug:slug>/', employeegradestep.employee_record_view, name='employee_record_view'),
#     path('upload_employee_grade_csv/', employeegradestep.upload_employee_grade_csv, name='upload_employee_grade_csv'),
#     path('download_sample_employee_grade_csv/', employeegradestep.download_sample_employee_grade_step_csv, name='download_sample_employee_grade_csv'),
#     path('upload_employee_grade_csv/', employeegradestep.upload_employee_grade_csv, name='upload_employee_grade_csv'),
#     path('export_employee_grade_step_csv/', employeegradestep.export_employee_grade_step_csv, name='export_employee_grade_step_csv'),
#     path('employee_thanks_record/<slug:slug>/thanks/', employeegradestep.employee_thanks_record, name='employee_thanks_record'),
#     path('update_thanks_counted/<slug:slug>/updatethanks/', employeegradestep.update_thanks_counted, name='update_thanks_counted'),
#     path('employee_punishments_record/<slug:slug>/punishments/', employeegradestep.employee_punishments_record, name='employee_punishments_record'),
#     path('update_punishment_counted/<slug:slug>/update/', employeegradestep.update_punishment_counted, name='update_punishment_counted'),
#     path('update_date_issued/<slug:slug>/update-date/', employeegradestep.update_date_issued, name='update_date_issued'),


#     ######################## Absence
    path('main_absence_type/', absences.main_absence_type, name='main_absence_type'),
    path('add_absence_type/', absences.add_absence_type, name='add_absence_type'),
    path('absence_type_detail/<slug:slug>/', absences.absence_type_detail, name='absence_type_detail'),
    path('update_absence_type/<slug:slug>/update/', absences.update_absence_type, name='update_absence_type'),
    path('delete_absence_type/<slug:slug>/delete/', absences.delete_absence_type, name='delete_absence_type'),
    path('download_employee_absence_csv_template/', absences.download_employee_absence_csv_template, name='download_employee_absence_csv_template'),



#     ###### Employee absence
     path('main_absences_employee/', absences.main_absences_employee, name='main_absences_employee'),
     path('add_absence_to_employees/', absences.add_absence_to_employees, name='add_absence_to_employees'),
    path('save_absence/', absences.save_absence, name='save_absence'),
    path('employee_absence_list/<slug:slug>/', absences.employee_absence_list, name='employee_absence_list'),

    path('employee_absence_listemployee/<slug:slug>/', absences.employee_absence_listemployee, name='employee_absence_listemployee'),


    path('delete_absence/<slug:slug>/delete/', absences.delete_absence, name='delete_absence'), 
    path('update_absence/<slug:slug>/update/', absences.update_absence, name='update_absence'),
     path('upload_employee_absence_csv/', absences.upload_employee_absence_csv, name='upload_employee_absence_csv'),
    
    
################################### Employement types #########################


    path('main_employement/', employement.main_employement, name='main_employement'),
    path('employement_type_create/', employement.employement_type_create, name='employement_type_create'),
    path('employement_type_detail/<slug:slug>/', employement.employement_type_detail, name='employement_type_detail'),  # عرض التفاصيل

    path('employement_type_update/<slug:slug>/', employement.employement_type_update, name='employement_type_update'),
    path('employement_type_delete/<slug:slug>/', employement.employement_type_delete, name='employement_type_delete'),


    ################################ Employee Employement ###############

      path('employee_employment_history/', employmenthistory.employee_employment_history, name='employee_employment_history'),
    path('upload_employment_history_csv/', employmenthistory.upload_employment_history_csv, name='upload_employment_history_csv'),


     path('add_employment_history/<slug:slug>/', employmenthistory.add_employment_history, name='add_employment_history'),
     path('employment_history_detail/<slug:slug>/employment-history/', employmenthistory.employment_history_detail, name='employment_history_detail'),

     path('employment_history_detailemployee/<slug:slug>/employment-history/', employmenthistory.employment_history_detailemployee, name='employment_history_detailemployee'),



     
     path('employment_history_update/<slug:slug>/', employmenthistory.employment_history_update, name='employment_history_update'),
        path('employment_single_history_detail/<slug:slug>/', employmenthistory.employment_single_history_detail, name='employment_single_history_detail'),
     path('delete_employment_history_update/<slug:slug>/', employmenthistory.delete_employment_history_update, name='delete_employment_history_update'),



]
