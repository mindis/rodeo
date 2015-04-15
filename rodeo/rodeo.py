from kernel import Kernel

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, jsonify
import os
import sys


app = Flask(__name__)
__dirname = os.path.dirname(os.path.abspath(__file__))
active_dir = "."
kernel = None

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method=="GET":
        packages = []
        files = os.listdir(active_dir)
        return render_template("index.html", packages=packages, files=files)
    else:
        code = request.form.get('code')
        if code:
            if code=="getvars":
                kernel.execute("import json")
                code = 'print(json.dumps([{ "name": v, "dtype": type(vars()[v]).__name__ } for v in list(set(vars()))]))'
            result = kernel.execute(code)
            # if request.form.get('complete'):
            #     result = kernel.complete(code)
            # else:
            #     result = kernel.execute(code)

            print("*"*40 + "START RESULT" + "*"*40)
            print(result)
            print("*"*40 + "END RESULT" + "*"*40)
            result['output'] = result.get("stdout")
            if not result['output']:
                result['output'] = result.get("repr", '')
            return jsonify(result)
        else:
            return "BAD"

@app.route("/plots", methods=["GET"])
def plots():
    plot_dir = os.path.join(__dirname, "static", "plots")
    plots = []
    for plot in os.listdir(plot_dir):
        if plot.endswith(".png"):
            plots.append(url_for("static", filename="plots/%s" % plot))
    return jsonify({ "plots": plots })

@app.route("/file/<filename>", methods=["GET"])
def get_file(filename):
    filename = os.path.join(active_dir, filename)
    return open(filename).read()

@app.route("/file", methods=["POST"])
def save_file():
    filename = os.path.join(active_dir, request.form['filename'])
    with open(filename, 'wb') as f:
        f.write(request.form['source'])
    return "OK"

def main(directory, port=5000):
    global kernel
    global active_dir
    active_dir = os.path.realpath(directory)
    # get rid of plots
    for f in os.listdir(os.path.join(__dirname, "static", "plots")):
        f = os.path.join(__dirname, "static", "plots", f)
        if f.endswith(".png"):
            os.remove(f)
    kernel = Kernel()
    sys.stderr.write("rodeo is running\n\turl: http://localhost:%d/\n\tdirectory: %s\n" % (port, active_dir))
    app.run(debug=False, port=port)

if __name__=="__main__":
    if len(sys.argv)==1:
        directory = "."
    else:
        directory = sys.argv[1]
    main(directory)