# 1. serve web-inferface (compile react application, stick it in a public folder, serve it)
# 2. open browser
# 3. create inference api for the web interface to talk to
# 4. load and run models
# 5. communicate with qdrant

from client import open_browser, start_flask_server
from inference import load_models
from qdrant_stuff import start_qdrant_connection


start_qdrant_connection()
start_flask_server()
open_browser()
load_models()


### mvc view: react, controller: this python programm, model/ datasoruce: qdrant, gogole cloud storage
