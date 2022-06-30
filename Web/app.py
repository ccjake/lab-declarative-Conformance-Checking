from flask import Flask, render_template, request, redirect, url_for,flash
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
# cn = Celonis_Connect()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


@app.route("/", methods=["POST", "GET"])
def login_celonis():
    result = None
    global cn
    if request.method == "POST":
        celonis_url = str(request.form.get("celonis_url"))
        celonis_toke = str(request.form.get("celonis_token"))

        try:
            cn = Celonis_Connect(celonis_url=celonis_url, api_token=celonis_toke)
            result = "Connect uccessfully!"
            return render_template("celonis_login.html",result = result)
        except:
            cn = "no connection"
            result = "Connect Falied!"

    return render_template("celonis_login.html",result=result)


@app.route("/select_function", methods=["POST", "GET"])
def select():
    return render_template("select_func.html")


# manage the pools, datamodels and tables
@app.route("/table_manager", methods=["GET", "POST"])
def table_management():
    # get the uploaded file
    global cn
    pools = [pool.name for pool in cn.get_pools()]
    datamodels = {pool.name:[datamodel.name for datamodel in pool.datamodels] for pool in cn.get_pools()}
    tables = {datamodel.name:[table.name for table in datamodel.tables] for datamodel in cn.get_datamodels()}
    print(datamodels)



    # if request.method == "POST":  # 当以post方式提交数据时
    #     pool_name = request.form.get('pool_name')
    #     print(pool_name)
    #     return redirect("/upload")
    #     uploaded_file = request.files["event_log"]
    #     if uploaded_file.filename != "":
    #
    #         file_path = os.path.join(
    #             app.config["UPLOAD_FOLDER"], uploaded_file.filename
    #         )
    #         print(uploaded_file.filename)
    #
    #     uploaded_file.save(file_path)
    # save the file
    return render_template("table_management.html",pools = pools,datamodels = datamodels,tables = tables)


if __name__ == "__main__":
    app.run(port=5000)
