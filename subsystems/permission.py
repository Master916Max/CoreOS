
class PermissionRule:
    def __init__(self,read,write,execute):
        self.read = read
        self.write = write
        self.execute = execute

    def can_read(self) -> bool:
        return self.read
    def can_write(self) ->bool:
        return self.write
    def can_execute(self) ->bool:
        return self.execute


class Permission:
    def __init__(self, owner_uuid, owner_rule, group_rule,other_rule, get_group_id_by_user_id):
        self.owner_id = owner_uuid
        self.owner_rule = owner_rule
        self.group_id = get_group_id_by_user_id(owner_uuid)
        self.group_rule = group_rule
        self.other_rule = other_rule

        self.get_group_id_by_user_id = get_group_id_by_user_id

    def can_read(self,user_id) -> bool:
        return (self.owner_id == user_id and self.owner_rule.can_read()) or (self.group_id == self.get_group_id_by_user_id(user_id) and self.group_rule.can_read()) or self.other_rule.can_read()

    def can_write(self,user_id) -> bool:
            return (self.owner_id == user_id and self.owner_rule.can_write()) or (self.group_id == self.get_group_id_by_user_id(user_id) and self.group_rule.can_write()) or self.other_rule.can_write()
        
    def can_execute(self,user_id) -> bool:
            return (self.owner_id == user_id and self.owner_rule.can_execute()) or (self.group_id == self.get_group_id_by_user_id(user_id) and self.group_rule.can_execute()) or self.other_rule.can_execute()

class PermissionManager:
    def __init__(self):
        pass

    