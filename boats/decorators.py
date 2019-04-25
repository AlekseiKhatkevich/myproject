from functools import wraps
from django.utils.decorators import available_attrs
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

default_message = "If you want to fulfill this action you must log in first"


def user_passes_test(test_func, message=default_message):
    """
    Decorator for views that checks that the user passes the given test,
    setting a message in case of no success. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if not test_func(request.user):
                messages.warning(request, message)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def login_required_message(function=None, message=default_message):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        message=message,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


class MessageLoginRequiredMixin(LoginRequiredMixin):
    """Добавляет в миксин сообщение"""

    redirect_message = default_message

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.add_message(request, messages.WARNING, self.redirect_message,
                                 fail_silently=True)
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
