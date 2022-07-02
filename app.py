from flask import Flask, render_template, request, redirect, url_for, flash
import os
from os.path import join, dirname, realpath
from celonis_connect import Celonis_Connect
from werkzeug.utils import secure_filename

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py import convert_to_dataframe
from discovery.model_discover import declare_model_discover

import pandas as pd
app = Flask(__name__)

# enable debugging mode
app.config["DEBUG"] = True

# Uploads folder
UPLOAD_FOLDER = join(dirname(realpath(__file__)), "static/Uploads/")
ALLOWED_EXTENSIONS = set(["xes"])
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

cn = "no connection"
result = None
# pools = None
# datamodels = None
# tables = None

pools = ["1"]
datamodels = {"1": ["aa"]}
tables = {"aa": ["bb"]}
# cn = Celonis_Connect()
model = None

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
            ## todo: table not assign to the comb. from(datamodels and pools), may leads to bug
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
@app.route("/discover", methods=["GET", "POST"])
def discover():
    # get the uploaded file
    error = None
    global model
    # model = {
    #     "equivalence": [
    #         ("ER_Registration", "ER_Triage"),
    #         ("ER_Registration", "IV_Antibiotics"),
    #         ("ER_Triage", "ER_Registration"),
    #         ("ER_Triage", "IV_Antibiotics"),
    #         ("IV_Antibiotics", "ER_Registration"),
    #         ("IV_Antibiotics", "ER_Triage"),
    #     ],
    #     "always_after": [
    #         ("ER_Registration", "ER_Sepsis_Triage"),
    #         ("ER_Registration", "ER_Triage"),
    #         ("ER_Registration", "IV_Antibiotics"),
    #         ("ER_Triage", "ER_Sepsis_Triage"),
    #         ("IV_Antibiotics", "ER_Sepsis_Triage"),
    #         ("IV_Antibiotics", "ER_Triage"),
    #     ],
    #     "always_before": [
    #         ("ER_Triage", "ER_Registration"),
    #         ("ER_Triage", "IV_Antibiotics"),
    #         ("IV_Antibiotics", "ER_Registration"),
    #     ],
    #     "never_together": [],
    #     "directly_follows": [
    #         ("ER_Registration", "IV_Antibiotics"),
    #         ("ER_Triage", "ER_Sepsis_Triage"),
    #     ],
    #     "activ_freq": {
    #         "ER_Registration": {1},
    #         "ER_Sepsis_Triage": {5, 6},
    #         "ER_Triage": {1},
    #         "IV_Antibiotics": {1},
    #     },
    # }
    if request.method == "POST":
        global cn
        global pools
        global datamodels
        global tables

        ## add pool



        ## model discover
        if "table_discover" in request.form:
            table = request.form["table_discover"]
            datamodel_name = request.form["datamodel_discover"]
            datamodel = cn.c.datamodels.find(datamodel_name)
            threshold = int(request.form["threshold"])
            model = declare_model_discover(datamodel, table, (1 - threshold))
            text_model = {}
            text_model["EquivalenceM"] = [
                (
                    "Activity '"
                    + a
                    + "' and activity '"
                    + b
                    + "' always occur with same frequency into a trace"
                )
                for (a, b) in model["equivalence"]
            ]
            text_model["Always-afterM"] = [
                ("Activity '"
                + a
                + "' is alywas followed by '"
                + b
                + "' ")
                for (a, b) in model["always_after"]
            ]
            text_model["Always-beforeM"] = [
                ("Activity '"
                + a
                + "' is alywas preceded by '"
                + b
                + "' ")
                for (a, b) in model["always_before"]
            ]
            text_model["Never-togetherM"] = [
                ("Activity '"
                 + a
                 + "' and activity '"
                 + b
                 + "' never occur in a same trace")
                for (a, b) in model["never_together"]
            ]
            text_model["Directly-followsM"] = [
                ("Activity '"
                + a
                + "' is alywas directly followed by '"
                + b
                + "' ")
                for (a, b) in model["directly_follows"]
            ]

            for _ in model['activ_freq'].keys():
                model['activ_freq'][_] = "[" + ", ".join(map(str, model['activ_freq'][_])) + "]"

            text_model['OccurrencesM'] = [
                ("Activity '" + a + "' can happen " + model['activ_freq'][a] + " times in one trace")
                for a in model['activ_freq'].keys()
            ]
            print(text_model)

            # print(declare_model_discover(datamodel, table, (1 - threshold)))
            return render_template(
                "discover.html",
                pools=pools,
                datamodels=datamodels,
                tables=tables,
                text_model=text_model,
            )
    return render_template(
        "discover.html", pools=pools, datamodels=datamodels, tables=tables,model = None
    )


@app.route("/conformance_checking",methods=["GET","POST"])
def conformance():
    global pools
    global datamodels
    global tables
    return render_template("conformance.html",pools=pools, datamodels=datamodels, tables=tables)

if __name__ == "__main__":
    app.run(port=5000)
