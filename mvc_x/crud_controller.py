from exceptions import Exception
import sys
from org.vertx.java.core.json import JsonObject
from mvc_x import remote_debugger
from mvc_x.controller import Controller, admin

__author__ = 'parroit'


class CrudController(Controller):
    edit_form = None
    page_len = 15
    collection = ""
    filter = None
    key_name = ""


    @admin
    def list(self, text_page):



        #remote_debugger.breakpoint()

        page = int(text_page)
        #print("page " + str(page))

        def on_reply(reply):
            print(reply.body)
            if reply.body.getString("status") == "error":
                self.req.response.end("Error:" + reply.body.getString("error"))
            else:
                users = reply.body.getArray("rows").toArray()
                total_rows = reply.body.getNumber("total_rows")
                pages = reply.body.getNumber("pages")
                #remote_debugger.breakpoint()
                self.render_results(
                        {'rows': users, 'current_page': page, 'total_pages': pages, 'total_rows': total_rows,"ctrl":self})

        print(self.filter)

        msg = JsonObject(dict(
            collection=self.collection,
            action="find",
            limit=self.page_len,
            page=page,
            matcher=self.filter
        ))

        self.eventBus.send("alchemy-persistor", msg, on_reply)


    @admin
    def edit(self, key):

        if key == "new":
            key = self.req.params[self.key_name]
            if isinstance(key,[].__class__):
                key=key[0]

        def on_reply(reply):
            if reply.body.getString("status") == "error":

                self.req.response.end("Error:" + reply.body.getString("error"))
            else:


                user = reply.body.getArray("rows").toArray()[0]
                self.render_results({self.key_name:key, 'data': self.edit_form.fill_from_values(user),"ctrl":self})

        msg = JsonObject(dict(
            collection=self.collection,
            action="find",
            limit=1,
            page=1,
            matcher=self.key_name+ " == '%s'" % key
        ))

        print("send event to alchemy-persistor")
        self.eventBus.send("alchemy-persistor", msg, on_reply)

    factory = lambda: None

    @admin
    def create(self):

        self.render_results({self.key_name:"","data":self.edit_form.fill_from_values(self.factory()),"ctrl":self})


    @admin
    def save(self, key):
        if key == "new":
            key = self.req.params[self.key_name]
            if isinstance(key,[].__class__):
                key=key[0]

        try:
            data_binded_form = self.edit_form.fill_from_values(self.req.params)

            def on_reply(reply):
                if reply.body.getString("status") == "error":
                    data = self.edit_form.fill_from_values({"valid": False, "note": reply.body.getString("error")})
                    self.render_results({self.key_name:key,'data': data,"ctrl":self})
                else:
                    data = self.edit_form.fill_from_values(reply.body.getObject("document").toMap())
                    self.render_results({self.key_name:key,'data': data,"ctrl":self})

            if data_binded_form.validate():
                msg = JsonObject()\
                .putString("collection", self.collection)\
                .putString("action", "save")\
                .putObject("document", data_binded_form.to_json())

                self.eventBus.send("alchemy-persistor", msg, on_reply)
            else:
                self.render_results({self.key_name:key,'data': data_binded_form,"ctrl":self})
        except Exception:
            import cgi

            user = self.edit_form.fill_from_values({"valid": False, "note": cgi.escape(str(sys.exc_info()))})
            self.render_results({'data': user,self.key_name:key,"ctrl":self})