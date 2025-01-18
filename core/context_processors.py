
from core.models import Logo


def logo_context(request):
    """
    إرجاع الشعار ليكون متاحًا في جميع القوالب.
    """
    logo = Logo.objects.first()
    return {"logo": logo}
