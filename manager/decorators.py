from django.shortcuts import redirect
from manager.models import Manager

def manager_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user_id = request.session.get('user')
        if not user_id:
            return redirect('/manager/login/')

        try:
            request.manager = Manager.objects.get(pk=user_id)
        except Manager.DoesNotExist:
            return redirect('/manager/login/')

        return view_func(request, *args, **kwargs)

    return _wrapped_view
