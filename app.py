from flask import Flask, render_template, request, redirect, url_for, flash
import os
from os.path import join, dirname, realpath
from celonis_connect import Celonis_Connect
from werkzeug.utils import secure_filename

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py import convert_to_dataframe
from discovery.model_discover import declare_model_discover

from conformance_checking.conformance_check import conformance_checking
from conformance_checking.conformance_check import variant_table

import json
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
text_model = None
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
            tables = {
                pool.name: {
                    datamodel.name: [table.name for table in datamodel.tables]
                    for datamodel in cn.get_datamodels_by_pool(pool.name)
                }
                for pool in cn.get_pools()
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


def data_handel(request):
    global cn
    global pools
    global datamodels
    global tables

    if "add_pool" in request.form:
        try:
            pool_name = str(request.form.get("add_pool"))
            print("request.values", request.values)
            print("request.form", request.form)

            print(pool_name)
            cn.c.create_pool(pool_name)
            pools = [pool.name for pool in cn.get_pools()]
            return render_template(
                "discover.html",
                pools=pools,
                datamodels=datamodels,
                tables=tables,
            )
        except:
            return render_template(
                "discover.html",
                pools=pools,
                datamodels=datamodels,
                tables=tables,
                error="pool already exists",
            )

    ## add datamodel
    if "add_datamodel" in request.form:
        try:
            pool_name = str(request.form.get("selected_pool"))
            datamodel_name = str(request.form.get("add_datamodel"))
            cn.c.create_datamodel(datamodel_name, pool_name)
            datamodels = {
                pool.name: [datamodel.name for datamodel in pool.datamodels]
                for pool in cn.get_pools()
            }
            return render_template(
                "discover.html",
                pools=pools,
                datamodels=datamodels,
                tables=tables,
            )
        except:
            return render_template(
                "discover.html",
                pools=pools,
                datamodels=datamodels,
                tables=tables,
                error="datamodel already exists",
            )

    ## add table
    if "add_table" in request.files:
        try:
            pool_name = str(request.form.get("selected_pool"))
            datamodel_name = str(request.form.get("selected_datamodel"))
            table = request.files["add_table"]
            if table:
                tablename = secure_filename(table.filename)
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], tablename)
                # set the file path
                table.save(file_path)
                log_path = join(dirname(realpath(__file__)), file_path)
                log = xes_importer.apply(log_path)
                df_act = convert_to_dataframe(log)
                df_act.rename(columns={"case:concept:name": "CASE ID"}, inplace=True)
                colnames = df_act.columns
                pool = cn.get_pools().find(pool_name)
                datamodel = cn.get_datamodels().find(datamodel_name)
                pool.create_table(df_act, tablename)
                tablename = tablename.replace(".", "_")
                datamodel.add_table_from_pool(table_name=tablename)
                for colname in colnames:
                    if "CASE" in colname:
                        case_col = colname
                        continue
                    if "time" in colname:
                        time_col = colname
                        continue
                    if "concept:name" in colname:
                        act_col = colname
                        continue
                datamodel.create_process_configuration(
                    activity_table=tablename,
                    case_column=case_col,
                    activity_column=act_col,
                    timestamp_column=time_col,
                )
                datamodel.reload()
                tables = {
                    pool.name: {
                        datamodel.name: [table.name for table in datamodel.tables]
                        for datamodel in cn.get_datamodels_by_pool(pool.name)
                    }
                    for pool in cn.get_pools()
                }
            return render_template(
                "discover.html",
                pools=pools,
                datamodels=datamodels,
                tables=tables,
            )
        except:
            print("except")
            return render_template(
                "discover.html",
                pools=pools,
                datamodels=datamodels,
                tables=tables,
                error="table already exists",
            )


# manage the pools, datamodels and tables;
@app.route("/discover", methods=["GET", "POST"])
def discover():
    # get the uploaded file
    error = None
    global text_model
    model = {
        "equivalence": [
            ("ER_Registration", "ER_Triage"),
            ("ER_Registration", "IV_Antibiotics"),
            ("ER_Triage", "ER_Registration"),
            ("ER_Triage", "IV_Antibiotics"),
            ("IV_Antibiotics", "ER_Registration"),
            ("IV_Antibiotics", "ER_Triage"),
        ],
        "always_after": [
            ("ER_Registration", "ER_Sepsis_Triage"),
            ("ER_Registration", "ER_Triage"),
            ("ER_Registration", "IV_Antibiotics"),
            ("ER_Triage", "ER_Sepsis_Triage"),
            ("IV_Antibiotics", "ER_Sepsis_Triage"),
            ("IV_Antibiotics", "ER_Triage"),
        ],
        "always_before": [
            ("ER_Triage", "ER_Registration"),
            ("ER_Triage", "IV_Antibiotics"),
            ("IV_Antibiotics", "ER_Registration"),
        ],
        "never_together": [],
        "directly_follows": [
            ("ER_Registration", "IV_Antibiotics"),
            ("ER_Triage", "ER_Sepsis_Triage"),
        ],
        "activ_freq": {
            "ER_Registration": {1},
            "ER_Sepsis_Triage": {5, 6},
            "ER_Triage": {1},
            "IV_Antibiotics": {1},
        },
    }
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
        ("Activity '" + a + "' is alywas followed by '" + b + "' ")
        for (a, b) in model["always_after"]
    ]
    text_model["Always-beforeM"] = [
        ("Activity '" + a + "' is alywas preceded by '" + b + "' ")
        for (a, b) in model["always_before"]
    ]
    text_model["Never-togetherM"] = [
        (
                "Activity '"
                + a
                + "' and activity '"
                + b
                + "' never occur in a same trace"
        )
        for (a, b) in model["never_together"]
    ]
    text_model["Directly-followsM"] = [
        ("Activity '" + a + "' is alywas directly followed by '" + b + "' ")
        for (a, b) in model["directly_follows"]
    ]

    for _ in model["activ_freq"].keys():
        model["activ_freq"][_] = (
                "[" + ", ".join(map(str, model["activ_freq"][_])) + "]"
        )

    text_model["OccurrencesM"] = [
        (
                "Activity '"
                + a
                + "' can happen "
                + model["activ_freq"][a]
                + " times in one trace"
        )
        for a in model["activ_freq"].keys()
    ]
    if request.method == "POST":
        global cn
        global pools
        global datamodels
        global tables

        ## add pool
        data_handel(request)

        ## model discover
        if "table_discover" in request.form:
            # global model
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
                ("Activity '" + a + "' is alywas followed by '" + b + "' ")
                for (a, b) in model["always_after"]
            ]
            text_model["Always-beforeM"] = [
                ("Activity '" + a + "' is alywas preceded by '" + b + "' ")
                for (a, b) in model["always_before"]
            ]
            text_model["Never-togetherM"] = [
                (
                    "Activity '"
                    + a
                    + "' and activity '"
                    + b
                    + "' never occur in a same trace"
                )
                for (a, b) in model["never_together"]
            ]
            text_model["Directly-followsM"] = [
                ("Activity '" + a + "' is alywas directly followed by '" + b + "' ")
                for (a, b) in model["directly_follows"]
            ]

            for _ in model["activ_freq"].keys():
                model["activ_freq"][_] = (
                    "[" + ", ".join(map(str, model["activ_freq"][_])) + "]"
                )

            text_model["OccurrencesM"] = [
                (
                    "Activity '"
                    + a
                    + "' can happen "
                    + model["activ_freq"][a]
                    + " times in one trace"
                )
                for a in model["activ_freq"].keys()
            ]

            # print(declare_model_discover(datamodel, table, (1 - threshold)))
            return render_template(
                "discover.html",
                pools=pools,
                datamodels=datamodels,
                tables=tables,
                text_model=text_model,
            )
    return render_template(
        "discover.html", pools=pools, datamodels=datamodels, tables=tables, text_model=text_model
    )


@app.route("/conformance_checking", methods=["GET", "POST"])
def conformance():
    global pools
    global datamodels
    global tables
    if request.method == "POST":
        global cn
        global pools
        global datamodels
        global tables

        ## add pool
        data_handel(request)




    return render_template(
        "conformance.html", pools=pools, datamodels=datamodels, tables=tables
    )

@app.route("/download",methods=["GET", "POST"])
def download_model():
    global model
    b = json.dumps(model)
    print()
    print()
    if request.method == "POST":
        if "model_name" in request.form:
            print("dsds")
            name = request.form["model_name"]
            dp = join(dirname(realpath(__file__)), "static/")
            f2 = open((dp+name+'.json'),'w')
            f2.write(b)
            f2.close()


    return redirect("/discover")
if __name__ == "__main__":
    app.run(port=5000)
