from django.shortcuts import render
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from .models.employee_leave_models import LeaveBalance


def refresh_leave_balance(request, pk):
    # الحصول على الكائن باستخدام id الخاص به
    leave_balance = get_object_or_404(LeaveBalance, pk=pk)
    
    # إذا كانت الرصيد موجودًا، نقوم بإعادة حفظه مما سيؤدي إلى زيادة الرصيد.
    leave_balance.save()  # سيؤدي إلى استدعاء الدالة save في النموذج وبالتالي زيادة الرصيد
    
    # إعادة توجيه المستخدم إلى الصفحة نفسها أو إلى صفحة أخرى
    return redirect('hrhub:leave_balance_detail', pk=leave_balance.pk)


def leave_balance_detail(request, pk):
    leave_balance = get_object_or_404(LeaveBalance, pk=pk)
    return render(request, 'hrhub/leave_balance_detail.html', {'leave_balance': leave_balance})




@login_required
def main_hrhub(request):
    # التحقق من صلاحيات المستخدم
   
    
    context = {
        # 'jobtitles': jobtitles
    }

    return render(request, 'hrhub/main_hrhub.html', context)
