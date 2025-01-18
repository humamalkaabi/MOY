from django.shortcuts import render, get_object_or_404, redirect
from hrhub.models.employement_models import EmployementType
from hrhub.forms.Employment_Forms import EmployementTypeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied



@login_required
def main_employement(request):
    types = EmployementType.objects.all()
    return render(request, 'hrhub/employement/main_employement.html', {'types': types})

@login_required
@permission_required('hrhub.can_add_employment_type', raise_exception=True)
def employement_type_create(request):
    if request.method == 'POST':
        form = EmployementTypeForm(request.POST, request.FILES)
        if form.is_valid():
            employement_type = form.save(commit=False)
            employement_type.created_by = request.user  # المستخدم الحالي
            employement_type.save()
            return redirect('hrhub:main_employement')
    else:
        form = EmployementTypeForm()
    return render(request, 'hrhub/employement/employement_type_create.html', {'form': form, 'title': 'إضافة نوع توظيف جديد'})

@login_required
def employement_type_detail(request, slug):
    # جلب نوع التوظيف باستخدام الـ slug
    employement_type = get_object_or_404(EmployementType, slug=slug)
    return render(request, 'hrhub/employement/employement_type_detail.html', {'employement_type': employement_type})

@login_required
@permission_required('hrhub.can_update_employment_type', raise_exception=True)
def employement_type_update(request, slug):
    employement_type = get_object_or_404(EmployementType, slug=slug)
    if request.method == 'POST':
        form = EmployementTypeForm(request.POST, request.FILES, instance=employement_type)
        if form.is_valid():
            form.save()
            return redirect('hrhub:main_employement')
    else:
        form = EmployementTypeForm(instance=employement_type)
    return render(request, 'hrhub/employement/update_employement_type.html', {'form': form, 'title': f'تعديل: {employement_type.name}'})


@login_required
@permission_required('hrhub.can_delete_employment_type', raise_exception=True)
def employement_type_delete(request, slug):
    employement_type = get_object_or_404(EmployementType, slug=slug)
    employement_type.delete()
    return redirect('hrhub:main_employement')
