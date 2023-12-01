# trigger webbrowser to open a website
import webbrowser

# from inference import do_inference
from flaskserver import app
from threading import Thread


def open_browser():
    webbrowser.open("http://127.0.0.1:5001")


# start a webserver
def start_flask_server():
    # Run the Flask app in a separate thread
    server_thread = Thread(target=app.run(host='0.0.0.0', port=5001), kwargs={"debug": False})
    server_thread.start()


# flask api that serves:
# / -> index.html
# /inference -> calls do_inference from inference.py
