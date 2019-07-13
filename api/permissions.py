from rest_framework import permissions


class IsOwnerOrFuckOff(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return True if request.method in permissions.SAFE_METHODS else obj.author == request.user

