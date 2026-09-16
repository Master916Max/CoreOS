from enum import IntFlag


class PermissionPreset(IntFlag):
    """The permissions supported by the core permission system."""
    NONE = 0
    READ = 0x100
    WRITE = 0x010
    EXECUTE = 0x001
    READ_WRITE = READ | WRITE
    READ_EXECUTE = READ | EXECUTE
    WRITE_EXECUTE = WRITE | EXECUTE
    ALL = READ | WRITE | EXECUTE


class Permission:
    """A named set of permissions assigned to a subject."""

    def __init__(self, name, value=PermissionPreset.NONE):
        if not name:
            raise ValueError("permission name cannot be empty")
        self.name = str(name)
        self.value = PermissionPreset(value)

    def allows(self, permission):
        permission = PermissionPreset(permission)
        return (self.value & permission) == permission

    def grant(self, permission):
        self.value |= PermissionPreset(permission)
        return self

    def revoke(self, permission):
        self.value &= ~PermissionPreset(permission)
        return self

    def __contains__(self, permission):
        return self.allows(permission)

    def __repr__(self):
        return f"Permission({self.name!r}, {self.value!r})"


class Policy:
    """Maps subjects to their granted permissions."""

    def __init__(self):
        self._permissions = {}

    def set(self, subject, permissions):
        self._permissions[subject] = PermissionPreset(permissions)
        return self

    def grant(self, subject, permissions):
        current = self._permissions.get(subject, PermissionPreset.NONE)
        self._permissions[subject] = current | PermissionPreset(permissions)
        return self

    def revoke(self, subject, permissions):
        current = self._permissions.get(subject, PermissionPreset.NONE)
        self._permissions[subject] = current & ~PermissionPreset(permissions)
        return self

    def allows(self, subject, permission):
        granted = self._permissions.get(subject, PermissionPreset.NONE)
        permission = PermissionPreset(permission)
        return (granted & permission) == permission

    def permissions_for(self, subject):
        return self._permissions.get(subject, PermissionPreset.NONE)

    def remove(self, subject):
        self._permissions.pop(subject, None)
        return self
