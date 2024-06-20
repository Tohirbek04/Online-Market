from django.template import Library

from apps.models import LikeModel

register = Library()


@register.filter()
def check_like(request, pk) -> bool:
    if request.user.is_authenticated:
        return LikeModel.objects.filter(user=request.user, product_id=pk).exists()
