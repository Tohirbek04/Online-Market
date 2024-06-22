from django.contrib.auth.mixins import LoginRequiredMixin


class OperatorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_operator:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

