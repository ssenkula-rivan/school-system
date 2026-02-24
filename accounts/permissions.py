"""
Permission system for account management
"""

def can_delete_user(deleter_profile, target_profile):
    """
    Check if deleter can delete target user
    
    Hierarchy:
    1. System Administrator - Can delete anyone
    2. Director - Can delete anyone except System Admin and other Directors
    3. HR Manager - Can delete employees (not Director, HR, or System Admin)
    4. Others - Cannot delete anyone
    """
    deleter_role = deleter_profile.role
    target_role = target_profile.role
    
    # System Administrator can delete anyone
    if deleter_profile.user.is_superuser:
        return True
    
    # Director permissions
    if deleter_role == 'director':
        # Cannot delete System Admin or other Directors
        if target_profile.user.is_superuser or target_role == 'director':
            return False
        return True
    
    # HR Manager permissions
    if deleter_role == 'hr_manager':
        # Can only delete regular employees
        protected_roles = ['admin', 'director', 'hr_manager']
        if target_role in protected_roles or target_profile.user.is_superuser:
            return False
        return True
    
    # All other roles cannot delete
    return False


def can_change_role(changer_profile, target_profile, new_role):
    """
    Check if changer can change target user's role
    
    Hierarchy:
    1. System Administrator - Can change anyone to any role
    2. Director - Can change anyone except System Admin, cannot create Directors
    3. HR Manager - Can change employees (not Director, HR, or System Admin)
    4. Others - Cannot change roles
    """
    changer_role = changer_profile.role
    target_role = target_profile.role
    
    # System Administrator can change anyone to any role
    if changer_profile.user.is_superuser:
        return True
    
    # Director permissions
    if changer_role == 'director':
        # Cannot change System Admin
        if target_profile.user.is_superuser:
            return False
        # Cannot create new Directors (but can change existing Director to other role)
        if new_role == 'director' and target_role != 'director':
            return False
        return True
    
    # HR Manager permissions
    if changer_role == 'hr_manager':
        # Can only change regular employees
        protected_roles = ['admin', 'director', 'hr_manager']
        if target_role in protected_roles or target_profile.user.is_superuser:
            return False
        # Cannot promote to protected roles
        if new_role in protected_roles:
            return False
        return True
    
    # All other roles cannot change
    return False


def get_manageable_users(manager_profile):
    """
    Get list of users that the manager can manage
    """
    from accounts.models import UserProfile
    
    # System Administrator can manage everyone
    if manager_profile.user.is_superuser:
        return UserProfile.objects.all()
    
    # Director can manage everyone except System Admin and other Directors
    if manager_profile.role == 'director':
        return UserProfile.objects.exclude(
            user__is_superuser=True
        ).exclude(
            role='director'
        ).exclude(
            id=manager_profile.id  # Exclude self
        )
    
    # HR Manager can manage regular employees only
    if manager_profile.role == 'hr_manager':
        protected_roles = ['admin', 'director', 'hr_manager']
        return UserProfile.objects.exclude(
            role__in=protected_roles
        ).exclude(
            user__is_superuser=True
        )
    
    # Others cannot manage anyone
    return UserProfile.objects.none()
