from django.http import HttpResponse
from django.shortcuts import redirect


# it added to the file by using @unauthenticated_user
def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenthicated:
            return redirect('index')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func

# added like allowed 34r|\|44|\| @allowed_users(allowed_roles=['admin','me'])
def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.group.exist():
                group = request.user.group.all()[0].name
            if group is allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('you are not authorized ')
        return wrapper_func

    return decorator
