from org.vertx.java.core.json import JsonObject
from org.python.google.common.io import Files
import java.nio.charset
import java.io
import traceback
import sys
from mvc_x import form,session



def authorized(controller):
    def decorated(*args,**kwargs):
        self=args[0]
        try:
            sess=session.load_session(self.req,self.session_dir)
            def on_login_reply(reply):
                if reply.body.getString("status")=="ok":
                    controller(*args,**kwargs)
                else:
                    self.req.response.put_header('Set-Cookie','mvcx.sessionID=')
                    self.see_other("/login")

            def on_auth_reply(reply):
                if reply.body.getString("status")=="ok":
                    controller(*args,**kwargs)
                else:
                    msg = JsonObject({"username":sess.getString("username"),"password":sess.getString("password")})
                    self.eventBus.send("mvcx.authmgr.login", msg,on_login_reply)




            if not sess is None:
                msg = JsonObject().putString("sessionID",sess.getString("auth_id"))
                self.eventBus.send("mvcx.authmgr.authorise", msg,on_auth_reply)

            else:
                print("no session defined:"+str(self.req.params))
                self.see_other("/login")

        except Exception:
            self.see_other("/login")

    return decorated




def admin(controller):
    def decorated(*args,**kwargs):
        self=args[0]
        try:
            def on_user_reply(reply2):
                print(str(reply2.body))
                if reply2.body.getString("status")=="error" or reply2.body.getObject("result") is None:
                    self.req.response.put_header('Set-Cookie','mvcx.sessionID=')
                    self.see_other("/login")
                else:

                    user=dict(reply2.body.getObject("result").toMap())

                    if user.has_key("admin") and user["admin"]:
                        controller(*args,**kwargs)
                    else:
                        self.see_other("/login")


            def send_user_query(username):
                self.eventBus.send("alchemy-persistor", JsonObject({
                    "collection": "User",
                    "action": "findone",
                    "matcher": "username == '%s'" % username
                }),on_user_reply)

            def on_auth_reply(reply):
                if reply.body.getString("status")=="ok":
                    send_user_query(reply.body.getString("username"))

                else:
                    username = sess.getString("username")
                    msg = JsonObject({"username": username,"password":sess.getString("password")})
                    def on_login_reply(reply):
                        if reply.body.getString("status")=="ok":
                            send_user_query(username)
                        else:
                            self.req.response.put_header('Set-Cookie','mvcx.sessionID=')
                            self.see_other("/login")
                    self.eventBus.send("mvcx.authmgr.login", msg,on_login_reply)

            sess=session.load_session(self.req,self.session_dir)
            if not sess is None:
                msg = JsonObject().putString("sessionID",sess.getString("auth_id"))
                self.eventBus.send("mvcx.authmgr.authorise", msg,on_auth_reply)

            else:
                print("no session defined:"+str(self.req.params))
                self.see_other("/login")
        except Exception:
            exc = str(sys.exc_info()[0])+"\n"+str(sys.exc_info()[1])+"\n"+traceback.format_exc(sys.exc_info()[2])

            print(exc)
            self.see_other("/login")

    return decorated



class Controller():
    def render_results(self,results):
        html = self.template_environment.get_template(self.template_name).render(arg=results,form=form)
        self.req.response.end(html)

    def see_other(self,path):
        self.req.response.set_status_code(303)
        self.req.response.put_header("Location",path)
        self.req.response.end()






    def __init__(self,req,eventBus,template_environment,template_name,session_dir):
        self.req=req
        self.eventBus=eventBus
        self.template_environment=template_environment
        self.template_name=template_name
        print("Controller "+self.__class__.__name__+" "+str(session_dir))
        self.session_dir=session_dir


