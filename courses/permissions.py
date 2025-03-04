from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsInstructorOrReadOnly(BasePermission):
    """Only instructors can create courses. Read access for everyone."""
    
    def has_permission(self, request, view):
        # Allow GET (read) access for everyone
        if request.method in SAFE_METHODS:
            return True
        
        # Block unauthenticated users
        if not request.user.is_authenticated:
            return False

        # Only instructors can create/update/delete courses
        return request.user.role == "instructor"

class IsOwnerOrForbidden(BasePermission):
    """Only the course creator can edit or delete their own courses."""
    
    def has_object_permission(self, request, view, obj):
        return request.user == obj.instructor  # Ensures only the owner can modify

class IsInstructorOrReadOnly(BasePermission):
    """Only instructors can create courses. Read access for everyone."""
    
    def has_permission(self, request, view):
        # Allow GET (read) access for everyone
        if request.method in SAFE_METHODS:
            return True
        
        # Block unauthenticated users
        if not request.user.is_authenticated:
            return False

        # Only instructors can create/update/delete courses
        return request.user.role == "instructor"

class IsOwnerOrForbidden(BasePermission):
    """Only the course creator can edit or delete their own courses."""
    
    def has_object_permission(self, request, view, obj):
        return request.user == obj.instructor  # Ensures only the owner can modify
    

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

