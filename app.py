from flask import Flask
import random
import logging
import flask
import sentry_sdk
import os

# import the flask extension
from flask.ext.cache import Cache

sentry_sdk.init(
    dsn=os.getenv("SENTRY_URL"),
    traces_sample_rate=0.2,
    sample_rate=0.25
)

file1 = open("./docs/index.html", "r")
data = file1.read()
file1.close()

app = Flask(__name__, static_url_path="/website_files",
            static_folder=(os.getcwd() + '/docs/website_files'))
# log = logging.getLogger('werkzeug')
# log.disabled = True
# app.logger.disabled = True

#import config setting
app.config["CACHE_TYPE"]="memcached"

# register the cache instance and binds it on to your app 
app.cache = Cache(app)

@app.route("/")
@app.cache.cached(timeout=50,key_prefix="hello")  # cache this view for 30 seconds
def main():
    return data

@app.route('/favicon.ico')
@app.cache.cached(timeout=50,key_prefix="hello")
def fav():
    return flask.send_from_directory(os.getcwd() + "/docs/website_files", "open-graph.ico")

if __name__ == "__main__":
    app.run(port=5000, debug=True, host='0.0.0.0')