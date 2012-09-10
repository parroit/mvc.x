from pydev import pydevd
from pydev import pydevd_comm
from pydev import pydevd_vm_type
from pydev.pydevd_comm import CMD_SET_BREAK,GetGlobalDebugger
import threading
import sys

__author__ = 'parroit'

sys.path.append("C:\projects\vertx\jython2.5.3\Lib\pydev")

def connect():
    try:


        pydevd.settrace(
            'localhost',
            port=10000,
            stdoutToServer=True,
            stderrToServer=True,
            suspend=False,
            trace_only_current_thread=True ,
            overwrite_prev_trace=True
        )
    except Exception:
        pass

def breakpoint():
    try:


        pydevd.settrace(
            'localhost',
            port=10000,
            stdoutToServer=True,
            stderrToServer=True,
            suspend=True,
            trace_only_current_thread=True ,
            overwrite_prev_trace=True
        )
    except Exception:
        pass