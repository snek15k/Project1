from django.http import request, HttpResponseForbidden


def is_manager(user):
    return user.groups.filter(name="Managers").exists()
