import vertx

def handler(msg):

    print("deploy done: "+msg)

cfg=vertx.config()


vertx.deploy_module('vertx.auth-mgr-v1.0', cfg["auth"],handler=handler)
vertx.deploy_module('eban.alchemy-persistor-v0.1', cfg["persistor"],handler=handler)
vertx.deploy_verticle('mvc_x/controller_verticle.py',  cfg["web"],handler=handler)

