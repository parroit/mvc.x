
from mvc_x import bindable
from mvc_x.crud_controller import CrudController

from mvc_x.bindable import Required, text

__author__ = 'parroit'

class Roles(CrudController):
    collection = "Role"
    filter="role_name <> 'admin'"
    key_name="role_name"
    factory=lambda s:dict(name="new role")
    edit_form=bindable.Bindable("edit-form",
        bindable.Field("role_name",Required(),text ,type="text",description="Name:"),
        bindable.Field("description",Required(),text ,type="text",description="Description:",note="a concise description of the role"),
        action="/roles/edit/new",
    )

