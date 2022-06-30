from flask import Flask, render_template, request, redirect, url_for, flash
import os
from os.path import join, dirname, realpath
from celonis_connect import Celonis_Connect
from werkzeug.utils import secure_filename
import sys
# sys.path.append(r'./')



app = Flask(__name__)

# enable debugging mode
app.config["DEBUG"] = True

# Uploads folder
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/Uploads/')
ALLOWED_EXTENSIONS = set(["xes"])
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

cn = "no connection"
result = None
# pools = None
# datamodels = None
# tables = None

pools = ["1"]
datamodels = {"1":["aa"]}
tables = {"aa":["bb"]}
# cn = Celonis_Connect()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


@app.route("/", methods=["POST", "GET"])
def login_celonis():
    global result
    global cn
    if request.method == "POST":
        celonis_url = str(request.form.get("celonis_url"))
        celonis_toke = str(request.form.get("celonis_token"))

        try:
            cn = Celonis_Connect(celonis_url=celonis_url, api_token=celonis_toke)
            result = "Connect uccessfully!"
            global pools
            global datamodels
            global tables
            pools = [pool.name for pool in cn.get_pools()]
            datamodels = {
                pool.name: [datamodel.name for datamodel in pool.datamodels]
                for pool in cn.get_pools()
            }
            tables = {
                datamodel.name: [table.name for table in datamodel.tables]
                for datamodel in cn.get_datamodels()
            }

            ## return pools, datamodels, tables for select
            return redirect("/select_function")
        except:
            cn = "no connection"
            result = "Connect Falied!"

    return render_template("celonis_login.html", result=result)


@app.route("/select_function", methods=["POST", "GET"])
def select():
    return render_template("select_func.html")


# manage the pools, datamodels and tables;
@app.route("/table_manager", methods=["GET", "POST"])
def table_management():
    # get the uploaded file
    error = None
    if request.method == "POST":
        global cn
        global pools
        global datamodels
        global tables
        if "add_pool" in request.form:
            try:
                pool_name = str(request.form.get("add_pool"))
                print("request.values",request.values)
                print("request.form",request.form)

                print(pool_name)
                cn.c.create_pool(pool_name)
                pools = [pool.name for pool in cn.get_pools()]
                return render_template(
                    "table_management.html",
                    pools=pools,
                    datamodels=datamodels,
                    tables=tables,
                )
            except:
                return render_template(
                    "table_management.html",
                    pools=pools,
                    datamodels=datamodels,
                    tables=tables,
                    error="pool already exists",
                )

        if "add_datamodel" in request.form:
            try:
                pool_name = str(request.form.get("selected_pool"))
                datamodel_name = str(request.form.get("add_datamodel"))
                cn.c.create_datamodel(datamodel_name,pool_name)
                datamodels = {
                    pool.name: [datamodel.name for datamodel in pool.datamodels]
                    for pool in cn.get_pools()
                }
                return render_template(
                    "table_management.html",
                    pools=pools,
                    datamodels=datamodels,
                    tables=tables,
                )
            except:
                return render_template(
                    "table_management.html",
                    pools=pools,
                    datamodels=datamodels,
                    tables=tables,
                    error="datamodel already exists",
                )


        if "add_table" in request.files:
            # try:
            pool_name = str(request.form.get("selected_pool"))
            datamodel_name = str(request.form.get("selected_datamodel"))
            table = request.files['add_table']
            if table :
                tablename = secure_filename(table.filename)
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], tablename)
                # set the file path
                table.save(file_path)

            #     return render_template(
            #         "table_management.html",
            #         pools=pools,
            #         datamodels=datamodels,
            #         tables=tables,
            #     )
            # except:
            #     print("except")
            #     return render_template(
            #         "table_management.html",
            #         pools=pools,
            #         datamodels=datamodels,
            #         tables=tables,
            #         error="table already exists",
            #     )

    return render_template(
        "table_management.html", pools=pools, datamodels=datamodels, tables=tables
    )


if __name__ == "__main__":
    app.run(port=5000)
