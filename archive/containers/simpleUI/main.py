# Copyright (C) 2018-2023 Mark McIntyre

from flask import Flask, render_template
from dbaccess import getCamList

app = Flask(__name__)


@app.route('/')
def index():
    camlist = getCamList()
    print(camlist)
    return render_template('bootstrap_table.html', title='Current Cameras',
                           users=camlist)


if __name__ == '__main__':
    app.run()