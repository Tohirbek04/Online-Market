import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect

from users.models import Account


class OperatorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        current_time = time.localtime()
        formatted_time = time.strftime("%H:%M:%S", current_time)
        account = Account.objects.filter(
            Q(opertor=request.user) and
            Q(from_working_time__lte=formatted_time) and
            Q(to_working_time__gte=formatted_time))
        if not (request.user.is_operator and account):
            try:
                self.handle_no_permission()
            except:
                return redirect('status_403')
        return super().dispatch(request, *args, **kwargs)
