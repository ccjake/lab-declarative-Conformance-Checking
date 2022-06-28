from flask import Flask, render_template, request, redirect, url_for
import os
from os.path import join, dirname, realpath
from celonis_connect import Celonis_Connect

app = Flask(__name__)

# enable debugging mode
app.config["DEBUG"] = True

# Uploads folder
UPLOAD_FOLDER = "static/Uploads"
ALLOWED_EXTENSIONS = set(["xes"])
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

cn = "no connection"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


@app.route("/", methods=["POST", "GET"])
def login_celonis():
    # Set The upload HTML template '\templates\upload.html'
    if request.method == "POST":
        celonis_url = str(request.form.get("celonis_url"))
        celonis_toke = str(request.form.get("celonis_token"))
        print(celonis_url)
        print(celonis_toke)
        global cn
        try:
            cn = Celonis_Connect(celonis_url=celonis_url, api_token=celonis_toke)
            return redirect("/index")
        except:
            cn = "no connection"
            print("except")
            return redirect("/")
    # cn = Celonis_Connect(celonis_url="")

    return render_template("celonis_login.html")


# Root URLh
@app.route("/index", methods=["POST", "GET"])
def index():
    global cn
    if cn == "no connection":
        print(cn)
        return redirect(url_for("login_celonis"))
    # Set The upload HTML template '\templates\upload.html'
    return render_template("upload.html")


#

# Get the uploaded files
# @app.route("/", methods=["GET", "POST"])
# def uploadFiles():
#     # get the uploaded file
#     if request.method == 'POST':  # 当以post方式提交数据时
#         uploaded_file = request.files["event_log"]
#         if uploaded_file.filename != "":
#
#             file_path = os.path.join(app.config["UPLOAD_FOLDER"], uploaded_file.filename)
#             print(uploaded_file.filename)
#
#         uploaded_file.save(file_path)
#     # save the file
#     return redirect("upload.html")


if __name__ == "__main__":
    app.run(port=5000)
