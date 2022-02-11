from flask import Flask
from dotenv import load_dotenv
import logging
import flask
import sentry_sdk
import os
from waitress import serve

load_dotenv()

sentry_sdk.init(
    dsn=os.getenv("SENTRY_URL"),
    traces_sample_rate=0.2,
    sample_rate=0.25
)

file1 = open("./docs/index.html", "r")
data = file1.read()
file1.close()

app = Flask(__name__, static_url_path="/website_files",
            static_folder='D:\Programming\Shorty\docs\website_files')
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True


@app.route('/')
def main():
    return data


@app.route('/favicon.ico')
def fav():
    return flask.send_from_directory("./docs/website_files", "open-graph.ico")

def create_app():
    return app