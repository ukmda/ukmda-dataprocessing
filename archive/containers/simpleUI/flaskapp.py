# Copyright (C) 2018-2023 Mark McIntyre#

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)