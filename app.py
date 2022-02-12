from flask import Flask
import random
import logging
import flask
import sentry_sdk
import os

sentry_sdk.init(
    dsn=os.getenv("SENTRY_URL"),
    traces_sample_rate=0.2,
    sample_rate=0.25
)

file1 = open("./docs/index.html", "r")
data = file1.read()
file1.close()

application = Flask(__name__, static_url_path="/website_files",
            static_folder=(os.getcwd() + '/docs/website_files'))
# log = logging.getLogger('werkzeug')
# log.disabled = True
# application.logger.disabled = True

#import config setting
application.config["CACHE_TYPE"]="simple"

@application.route("/")
def main():
    return data

# @application.route('/favicon.ico')
# def fav():
#     return flask.send_from_directory(os.getcwd() + "/docs/website_files", "open-graph.ico")

if __name__ == "__main__":
    application.run(port=5000, host='0.0.0.0')