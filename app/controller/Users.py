#from app.model.model import create_new_session
#from app.model.user import User
import sys
from org.vertx.java.core.json import JsonObject
from uuid import UUID
import uuid
from java.io import File
from org.python.google.common.io import Files

from mvc_x import  bindable, session
from mvc_x.crud_controller import CrudController
from mvc_x.bindable import Required, email, alfanum, text
from mvc_x.controller import admin


class Users(CrudController):
    collection = "User"
    key_name="username"
    filter="username <> 'admin'"
    factory=lambda s:dict(username="new user")

    edit_form=bindable.Bindable("edit-form",
        bindable.Field("username",Required(),alfanum ,type="text",description="User Name:"),
        bindable.Field("fullname",Required(),text ,type="text",description="Full Name:",note="your complete name"),
        bindable.Field("email",Required(),email,type="text",description="E-Mail:"),
        bindable.Field("password",Required(),type="password",description="Password:"),
        bindable.Field("confirmed",type="checkbox",description="Confirmed:"),
        bindable.Field("admin",type="checkbox",description="Admin:"),
        action="/edit/new",
    )


    add_role_form=bindable.Bindable("add-role-form",
        bindable.Field("rolename",Required(),type="select",description="Add role:",items=[("doctor","a doctor"),("patient","a patient")]),
        action="/edit/new/addrole",
    )


    login_form=bindable.Bindable("login-form",
        bindable.Field("username",Required(),alfanum ,type="text",description="User name:",note="your login user name"),
        bindable.Field("password",Required(),type="password",description="Password:",note="your login password"),
        bindable.Field("remember",type="checkbox",description="Remember status:"),
        bindable.Field("login",type="submit",content="Login"),
        action="/login",
    )


    @admin
    def addrole(self, name):

        data_binded_form = self.add_role_form.fill_from_values(self.req.params)

        def on_reply(reply):
            if reply.body.getString("status") == "error":
                data = self.edit_form.fill_from_values({"username":name,"valid": False, "note": reply.body.getString("error")})
                self.render_results({'data': data,"ctrl":self})
            else:
                self.edit(name)

        if data_binded_form.validate():
            print(data_binded_form["rolename"].get_value())
            new_role=JsonObject(dict(user_id=name,role_id=data_binded_form["rolename"].get_value()))
            print("ROLE:"+str(new_role))
            msg = JsonObject()\
            .putString("collection", "UserRole")\
            .putString("action", "save")\
            .putObject("document", new_role)


            self.eventBus.send("alchemy-persistor", msg, on_reply)
        else:
            data = self.edit_form.fill_from_values({"username":name,"valid": False, "note": "You must specify which role to add"})
            self.render_results({'data': data,"ctrl":self})



    @admin
    def removerole(self,name,role):


        def on_reply_delete(reply):
            if reply.body.getString("status") == "error":

                data = self.edit_form.fill_from_values({"valid": False, "note": reply.body.getString("error")})
                self.render_results({'data': data,"ctrl":self})
            else:
                self.edit(name)



        msg_delete = JsonObject(dict(
            collection="UserRole",
            action="delete",
            matcher="user_id == '%s' and role_id == '%s'"%(name,role)
        ))
        self.eventBus.send("alchemy-persistor", msg_delete,on_reply_delete)


    def login_page(self):
        self.render_results({'login_form':self.login_form,'user':None})

    def do_login(self):

        global login_bindable
        try:

            login_bindable=self.login_form.fill_from_values(self.req.params)

            def on_reply(reply):
                if reply.body.getString("status")=="ok":
                    print "LOGGED IN"


                    msg = login_bindable.to_json()

                    auth_id = reply.body.getString("sessionID").strip()

                    username = msg.getString("username")
                    password = msg.getString("password")
                    remember=msg.getString("remember")

                    session.save_session(self.req,remember,auth_id=auth_id,username=username,password=password,session_dir=self.session_dir)
                    self.render_results({'login_form':login_bindable,'user':login_bindable.source["username"][0]})
                else:
                    print "LOGGED OUT:"+reply.body.getString("status")
                    login_bindable.valid=False
                    login_bindable.note="Username or password invalid."

                    self.render_results({'login_form':login_bindable,'user':None})

            if login_bindable.validate():
                msg = login_bindable.to_json()
                msg.removeField("remember")
                msg.removeField("login")

                print(msg)
                print("send event to mvcx.authmgr")
                self.eventBus.send("mvcx.authmgr.login", msg,on_reply)

            else:
                self.render_results({'login_form':login_bindable,'user':None})

        except Exception:
            print(sys.exc_info())
            self.render_results({'login_form':login_bindable,'user':None})

