from django.contrib import admin
from hrhub.models.grade_step_models import EmployeeGrade, EmployeeStep, EmployeeGradeChangeLog, EmployeeStepChangeLog
from hrhub.models.hr_utilities_models import DutyAssignmentOrder, DutyAssignmentOrderChangeLog, PlaceOfEmployment, PlaceOfEmploymentChangeLog
from hrhub.models.office_position_models import Office,EmployeeOffice,EmployeeOfficeChangeLog, OfficeChangeLog, Position, PositionChangeLog , EmployeeOfficePosition, EmployeeOfficePositionChangeLog
from hrhub.models.thanks_punishment_absence_models import ThanksType, ThanksTypeChangeLog, EmployeeThanks, EmployeeThanksChangeLog, PunishmentType, PunishmentTypeChangeLog, EmployeePunishment, EmployeePunishmentChangeLog , AbsenceType, AbsenceTypeChangeLog, EmployeeAbsence, EmployeeAbsenceChangeLog
from hrhub.models.central_financial_allocations_models import CentralFinancialAllocations, CentralFinancialAllocationsChangeLog
from hrhub.models.employee_leave_models import LeaveBalance, LeaveBalanceChangeLog, LeaveRequest, LeaveRequestChangeLog, LeaveType, LeaveTypeChangeLog
from hrhub.models.employement_models import EmployementType, EmploymentHistory, EmployementTypeChangeLog, EmploymentHistoryChangeLog
from hrhub.models.placement_models import Placement, PlacementActivityLog
from hrhub.models.staffing_structure_models import PayrollBudgetType, StaffStructerType, EmployeeStaffKind, PayrollBudgetTypeChangeLog, StaffStructerTypeChangeLog, EmployeeStaffKindChangeLog
from hrhub.models.employee_job_title_models import EmployeeJobTitle, JobTitleChangeLog, EmployeeJobTitleChangeLog, EmployeeJobTitleSettings, EmployeeJobTitleSettingsChangeLog, JobTitle
from hrhub.models.grade_step_upgrade_models import EmployeeGradeStepSettings, EmployeeGradeStepSettingsChangeLog
# from hrhub.models.grade_step_upgrade_models import EmployeeGradeStepSettings, EmployeeGradeStepSettingsChangeLog, EmployeeGradeStep, EmployeeGradeStepChangeLog

# Register your models here.

################################### Grade step models ##################### 
admin.site.register(EmployeeGrade)
admin.site.register(EmployeeStep)
admin.site.register(EmployeeGradeChangeLog)
admin.site.register(EmployeeStepChangeLog)


################################### hr_utilities_models ##################### 
admin.site.register(DutyAssignmentOrder)
admin.site.register(DutyAssignmentOrderChangeLog)
admin.site.register(PlaceOfEmployment)
admin.site.register(PlaceOfEmploymentChangeLog)

###################################### Office position models #################
admin.site.register(Office)
admin.site.register(OfficeChangeLog)
admin.site.register(Position)
admin.site.register(PositionChangeLog)
admin.site.register(EmployeeOfficePosition)
admin.site.register(EmployeeOfficePositionChangeLog)
admin.site.register(EmployeeOffice)
admin.site.register(EmployeeOfficeChangeLog)


###################################  Thanks punishment absence models ##################

admin.site.register(ThanksType)
admin.site.register(ThanksTypeChangeLog)
admin.site.register(EmployeeThanks)
admin.site.register(EmployeeThanksChangeLog)
admin.site.register(PunishmentType)
admin.site.register(PunishmentTypeChangeLog)
admin.site.register(EmployeePunishment)
admin.site.register(EmployeePunishmentChangeLog)
admin.site.register(AbsenceType)
admin.site.register(AbsenceTypeChangeLog)
admin.site.register(EmployeeAbsence)
admin.site.register(EmployeeAbsenceChangeLog)


################# Central Financial Allocations Models  ###############
admin.site.register(CentralFinancialAllocations)
admin.site.register(CentralFinancialAllocationsChangeLog)

###################### Employee Leave Models ######################
admin.site.register(LeaveBalance)
admin.site.register(LeaveBalanceChangeLog)
admin.site.register(LeaveRequest)
admin.site.register(LeaveRequestChangeLog)
admin.site.register(LeaveType)
admin.site.register(LeaveTypeChangeLog)


######################## Employement Models ###################
admin.site.register(EmployementType)
admin.site.register(EmploymentHistory)
admin.site.register(EmployementTypeChangeLog)
admin.site.register(EmploymentHistoryChangeLog)


################### Placement ######################
admin.site.register(Placement)
admin.site.register(PlacementActivityLog)



########################### Staffing Structure Models ##########
admin.site.register(PayrollBudgetType)
admin.site.register(StaffStructerType)
admin.site.register(EmployeeStaffKind)
admin.site.register(PayrollBudgetTypeChangeLog)
admin.site.register(StaffStructerTypeChangeLog)
admin.site.register(EmployeeStaffKindChangeLog)


########################### Job title  ########################
admin.site.register(EmployeeJobTitle)
admin.site.register(JobTitleChangeLog)
admin.site.register(EmployeeJobTitleChangeLog)
admin.site.register(EmployeeJobTitleSettings)
admin.site.register(EmployeeJobTitleSettingsChangeLog)
admin.site.register(JobTitle)


###################### Employee Grade Step ####################
admin.site.register(EmployeeGradeStepSettings)
admin.site.register(EmployeeGradeStepSettingsChangeLog)
# admin.site.register(EmployeeGradeStep)
# admin.site.register(EmployeeGradeStepChangeLog)

