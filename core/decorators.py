from django.contrib.auth.decorators import user_passes_test

def role_required(role):
    def decorator(view_func):
        decorated_view_func = user_passes_test(
            lambda user: user.is_authenticated and user.role == role,
            login_url='/'
        )(view_func)
        return decorated_view_func
    return decorator

def parent_required(view_func):
    return role_required('PARENT')(view_func)

def teacher_required(view_func):
    return role_required('TEACHER')(view_func)

def student_required(view_func):
    return role_required('STUDENT')(view_func)

def admin_required(view_func):
    return role_required('ADMIN')(view_func)
