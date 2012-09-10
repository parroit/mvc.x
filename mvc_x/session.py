from org.vertx.java.core.json import JsonObject
import uuid
from java.io import File
from org.python.google.common.io import Files
from java.nio.charset import Charset

def save_session(req,remember,session_dir,**kwargs):
    session=JsonObject()
    id=str(uuid.uuid1())

    session.putString("id", id)
    for name,value in kwargs.iteritems():
        session.putString(name, value)
    print("remember = "+remember)
    cookie = 'mvcx.sessionID=%s' % id.strip()
    if remember=="1":
        cookie += ";max-age=864000"

    req.response.put_header('set-cookie', cookie)
    session_file=File("%s/%s.json" % (session_dir,id))
    print("session_path:"+str(session_file.getAbsolutePath()))
    session_file.getParentFile().mkdirs()
    Files.write(str(session),session_file)

def load_session(req,session_dir):
    if req.params.has_key("mvcx.sessionID"):

        session_file=File("%s/%s.json" % (session_dir,req.params["mvcx.sessionID"]))
        print("session_path:"+str(session_file.getAbsolutePath()))
        if session_file.exists():
            session=JsonObject("\n".join(Files.readLines(session_file,Charset.defaultCharset())))

            return session
        else:
            return None
    else:
        return None