from java.io import File
from org.vertx.java.core.json import JsonObject, JsonArray
from org.vertx.java.deploy.impl import VertxLocator
from java.lang import Long
import cgi
import os
import sys
import traceback
import imp
import vertx
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from core.http import RouteMatcher

__author__ = 'parroit'
class ControllerHttpServer:

    server = vertx.create_http_server()


    def __init__(self,route,config):
        self.route=route
        self.config=config



    def start(self):
        if self.config.getBoolean("ssl",False):
            self.server.set_ssl(True)\
                .set_key_store_password(self.config.getString("key_store_password","wibble"))\
                .set_key_store_path(self.config.getString("key_store_path","app/server-keystore.jks"))


        bridge = self.config.getBoolean("bridge",False)
        if bridge:
            sjsServer = VertxLocator.vertx.createSockJSServer(self.server._to_java_server())
            inboundPermitted = self.config.getArray("inbound_permitted", JsonArray())
            outboundPermitted = self.config.getArray("outbound_permitted", JsonArray())
            auth_timeout=self.config.getInteger("auth_timeout")
            if auth_timeout is None:
                auth_timeout=0

            sjsServer.bridge(self.config.getObject("sjs_config", JsonObject().putString("prefix", "/eventbus")),
                inboundPermitted, outboundPermitted,
                Long(auth_timeout),
                self.config.getString("auth_address", "vertx.basicauthmanager.authorise"))


        #gzipFiles = self.config.getBoolean("gzip_files", False)
        webRoot = self.config.getString("web_root", "web")
        index = self.config.getString("index_page", "index.html")
        self.webRootPrefix = webRoot + File.separator
        self.indexPage = self.webRootPrefix + index

        print("Starting server on %s:%s" % (self.config.getString("host", "0.0.0.0"),self.config.getInteger("port")))
        self.server.request_handler(self.route).listen(self.config.getInteger("port"), self.config.getString("host", "0.0.0.0"))



def load_from_file(file_package,expected_class):
    print("loading %s from %s" % (expected_class,file_package))

    compiled_file = File(file_package.replace(".", "/") + "/" + expected_class + "$py.class")
    source_file = File(file_package.replace(".", "/") + "/" + expected_class + ".py")
    print("get request for controller %s. Compiled file outdated."%expected_class)
    if compiled_file.exists():
        if compiled_file.lastModified()<source_file.lastModified():
            print("get request for controller %s. Compiled file outdated."%expected_class)
            compiled_file.delete()
        else:
            print("get request for controller %s. Compiled file is up-to-date."%expected_class)
    else:
        print("get request for controller %s. Compiled file does not exists."%expected_class)
    py_mod = imp.load_source("module_"+expected_class, source_file.getAbsolutePath())


    if hasattr(py_mod, expected_class):
        class_inst = getattr(py_mod,expected_class)

    else:
        class_inst =None

    print(class_inst.__doc__)
    print(class_inst.__name__)
    return class_inst



def static_files_renderer(folder_path):

    def render(req):
        path=req.params["path"]
        absolute_path = File(folder_path, path).getAbsolutePath()
        if not ".." in req.path and os.path.exists(absolute_path):
            req.response.send_file(absolute_path)
        else:
            req.response.set_status_code(404)
            req.response.end("File not found "+str(path))
    return render

def controller_renderer(controller_path,controller_name,template_name,action,session_dir):

    def render(req):
        @req.body_handler
        def body_handler(body):
            print("BODY: "+str(body))
            for name,value in cgi.parse_qs(str(body)).iteritems():
                print name+"->"+str(value)
                if req.params.has_key(name):
                    if isinstance(req.params[name],list):
                        lst=req.params[name]
                    else:
                        lst=[]
                        lst+=req.params[name]
                        req.params[name]=lst
                    lst+=value
                else:
                    req.params[name]=value

            for name,value in req.headers.iteritems():
                if name=="cookie":
                    print (value)
                    for cookie in value.split(";"):
                        res =cookie.split("=",2)
                        print ("cookie found"+res[0]+" = "+res[1] )

                        req.params[str(res[0]).strip()]=str(res[1]).strip()



            try:
                def timeout_handle(msg):

                    req.response.set_status_code(500)
                    req.response.end("<html><body>timeout error:" + str(msg) + "</body></html>")

                #req.response.timeout=vertx.set_timer(5000, timeout_handle)


                jinja_environment =  Environment(loader=FileSystemLoader(["app/view","mvc_x"]))
                #remote_debugger.breakpoint()
                ctrl=load_from_file(controller_path,controller_name)

                ctrl_instance=ctrl(req, vertx.java_vertx().eventBus(), jinja_environment,template_name,session_dir)
                action(ctrl_instance,req)
            except Exception:
                req.response.set_status_code(500)

                exc = str(sys.exc_info()[0])+"\n"+str(sys.exc_info()[1])+"\n"+traceback.format_exc(sys.exc_info()[2])
                print exc
                req.response.end("<html><body>controller error:" + cgi.escape(exc)+"</body></html>")


    return render



def renderer(route,controller_description):
    def render_route(ctrl,req):
        print("rendering:"+str(route))
        action_call = controller_description.split(".",2)[1]
        print("action_call:"+action_call)
        action_name = action_call.split("(")[0].strip()
        print("action_name:"+action_name)
        action_call_params=action_call.split("(")[1].strip().replace(")","").strip()
        action=getattr(ctrl, action_name)

        if action_call_params!='':
            action_params = action_call_params.split(",")
            print("action_params:"+str(action_params))
            params=[ req.params[name[1:]] for name in action_params ]
            print("params:"+str(params))
            action(*params)
        else:
            action()

    return render_route



def build_route():
    router=RouteMatcher()

    cfg = vertx.config()
    config=JsonObject(cfg).getObject("router")

    for route in config.getArray("routes"):
        controller_description = route.getString("controller")



        def controller_name(): return str(controller_description).split(".")[0]

        if not route.getString("get") is None:
            print("get:"+str(route))
            router.get( route.getString("get"),controller_renderer(config.getString("controller-path"),controller_name(),route.getString("view"),renderer(route,controller_description),cfg["session-dir"]))
        elif not route.getString("post") is None:
            print("post:"+str(route))
            router.post( route.getString("post"),controller_renderer(config.getString("controller-path"),controller_name(),route.getString("view"),renderer(route,controller_description),cfg["session-dir"]))
        elif not route.getString("static") is None:
            print("static:"+str(route))
            router.get(route.getString("static"),static_files_renderer(route.getString("folder")) )
    return router


server=ControllerHttpServer(build_route(),VertxLocator.container.getConfig())
server.start()