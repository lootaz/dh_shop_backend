from rest_framework import permissions

from .models import Schedule, TimeRange


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.owner == request.user


class IsScheduleOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not isinstance(obj, Schedule):
            return False

        return obj.shop.owner == request.user


class IsTimeRangeOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not isinstance(obj, TimeRange):
            return False

        return obj.schedule.shop.owner == request.user
