"""
Georgia Smith
Regeneron App

Web app that manages workflow w/i lab for confirmatory sanger sequencing
"""

from random import sample


from app import app
from app import *
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
import secrets
from flask_principal import Principal
Bootstrap(app)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from app.forms import *
from flask import request, render_template, redirect, url_for

import datetime
import time
import sys
import pandas as pd
import os
import json
import re



from app.site_class import site, site_functions, table_functions

# Custom class that builds items
from app import build_items
from app.build_items import table_items

mysite = table_functions()

from functools import wraps

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "admin":
            return f(*args, **kwargs)
        else:
            flash("You need to be an admin to view this page.")
            return redirect(url_for('index'))

    return wrap


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(15), unique= True)
    firstname = db.Column(db.String(15))
    lastname  = db.Column(db.String(15))
    role = db.Column(db.String(50))
    password = db.Column(db.String(800))

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def user_len(): 
    return len(User.query.all())

def get_names():
    return {user.username: user.firstname + " " + user.lastname for user in User.query.all()}


def landing_page(args):
    pagedata = mysite.build_tables('landing', args = args)
    return render_template("public/table_view.html", bigdata = pagedata)

@app.before_request
def ensure_sampleversion():
    if user_len() == 0: 
        hashed_password = generate_password_hash("root", method= 'sha256')
        new_user = User(username="root", role="admin", firstname = "root", lastname = "root", password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
    if request.endpoint == "static":
        return
    
    if not current_user.is_authenticated:
        if request.endpoint != "login":
            return redirect("/login")
    if mysite.current_sample_version  == "":
        mysite.set_sample_version("RGC_trial_RoR_042522")
        mysite.load_data()
        mysite.load_users(get_names())
        #return redirect(url_for('index'))

@app.route("/user_mgmt",  methods=['GET', 'POST'])
@admin_required
def user_mgmt(): 
    userform = AllUserForm()
    print("AUF")
    print(userform.validate())
    print(userform.errors)
    userform.title.data = "All Users"
    if userform.validate_on_submit():
        for user in userform.users:
            print(user.oldusername.data)
            dbuser = User.query.filter_by(username=user.oldusername.data).first()
            dbuser.username = user.username.data
            dbuser.role = user.role.data
            dbuser.firstname = user.firstname.data
            dbuser.lastname = user.lastname.data
            if user.password.data != "":
                dbuser.password = generate_password_hash(user.password.data, method= 'sha256')
        db.session.commit()
        return render_template("public/user_mgmt.html", userform = userform)
    for user in User.query.all():
        singleform = MgmtForm()
        singleform.username = user.username
        singleform.oldusername = user.username
        singleform.role = user.role
        singleform.firstname = user.firstname
        singleform.lastname = user.lastname
        singleform.password = ""
        singleform.confpassword = ""
        userform.users.append_entry(singleform)
    return render_template("public/user_mgmt.html", userform = userform)


@app.route("/settings_admin",  methods=['GET', 'POST'])
@admin_required
def settings_admin(): 
    form = PasswordForm()
    auform = RegisterationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        print(current_user.username)
        if user:
            user.password = generate_password_hash(form.password.data, method= 'sha256')
            db.session.commit()
            mysite.load_users(get_names())
            logout_user()
            return redirect(url_for('index'))
    
    if auform.validate_on_submit():
        hashed_password = generate_password_hash(auform.password.data, method= 'sha256')
        new_user = User(username=auform.username.data, role=auform.role.data, password=hashed_password, firstname = auform.firstname.data, lastname = auform.lastname.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return(render_template("/public/settings_admin.html", form=form,  adduserform =auform))


@app.route("/settings",  methods=['GET', 'POST'])
def settings(): 
    form = PasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        print(current_user.username)
        if user:
            print(form.password)
            user.password = generate_password_hash(form.password, method= 'sha256')
            db.session.commit()
            logout_user()
            return redirect(url_for('index'))
    if current_user.role == "admin":
        return redirect("/settings_admin")
    return(render_template("/public/settings.html", form=PasswordForm()))

@app.route("/favicon.ico")
def favicon():
    return "", 200 

@app.route("/")
def index():
    return render_template("public/queues.html", args = request.args)

@app.route("/home")
def home():
    return render_template("public/queues.html")

@app.route("/construction")
def const():
    return render_template("public/construction.html")

@app.route("/plate_organize", methods = ["POST"])
def save_plate_organize(): 
    save_form = request.form
    ## save_form format ("samplename", "row-col")
    save_dict = {
       "cell": {
        }
    }
    primer_save = {

    }
    print(save_form)
    change_list = []
    print(save_form)
    for a in save_form: 
        if a == "plate": 
            plate = save_form[a]
        elif a.startswith("primer"):
            try: 
                primer_save[a] = {"plate_id": plate, "primer": int(save_form[a])}
            except:
                primer_save[a] = {"plate_id": plate, "primer": save_form[a]}

            print(primer_save)
            continue
        else:
            vals = a.split("-")
            colrow = save_form[a]
            rowval, colval = [int(x) for x in colrow.split("-")]
            # table cols: plate_id,well_row,well_column,sample_name,control,direction
            print(vals)
            if rowval == 0 and colval == 0: 
                sample_name = vals[0]
                sample_dir = vals[2]
                save_dict["cell"][colrow + sample_name] = {"plate_id": plate, "well_row": '',  "well_column": '', "sample_name": sample_name, "control": "", "direction": sample_dir, "count": "", "assigned": "", "primer": "", "primer_status": ""}
            elif (vals[1][1] == "s"): 
                ### samp
                sample_name = vals[0]
                count = int(vals[1][0])
                sample_dir = vals[2]
                pairset = vals[3]
                change_list.append(sample_name)
                save_dict["cell"][colrow] = {"plate_id": plate, "well_row": rowval, "well_column": colval, "sample_name": sample_name, "control": "", "direction": sample_dir, "count": count, "assigned": "", "primer": pairset, "primer_status": ""}
                mysite.log_comment(action = "saved", user = "global", sampleid = sample_name, plateid = plate, comment = "")
            else: 
                ### control
                control_name = vals[0]
                control_id = vals[1]
                pairset = vals[3]
                if control_name == "": 
                    continue
                mysite.log_comment(action = "saved", user = "global", sampleid = control_name, plateid = plate, comment = "")
                save_dict["cell"][colrow] = {"plate_id": plate, "well_row": rowval, "well_column": colval, "sample_name": control_name, "control": control_id, "direction": "", "count": -1, "assigned": "", "primer": pairset, "primer_status": ""}
    for samp in change_list:
        if "0-0" +  samp in save_dict["cell"].keys():
            save_dict["cell"]["0-0" + samp]["assigned"] = 1
    
    mysite.insertupdate(primer_save, "plate_primers", main_id = ["plate_id", "primer"],  main_col = "plate_id", samp = ["primer"], main_col_val = plate)
    mysite.insertupdate(save_dict["cell"], "plate_wells", main_id = ["plate_id", "sample_name", "count"],  main_col = "plate_id", samp = ["sample_name", "count"], main_col_val = plate)
    return "success", 200



@app.route("/plate_organize/<args>")
@app.route("/plate_organize/")
def plate_organize(args = "{}"):
    arg_dict = eval(args)
    if mysite.datadict == {}:
        return redirect("/")
    elif "plate_id" not in request.args.keys() and "plate_id" not in arg_dict.keys():
        return redirect(url_for('choose_plate', return_page = "design_plate"))
    else:
        arg_dict = arg_dict if "plate_id" in arg_dict.keys() else dict(request.args)
        return render_template("public/plate_organize.html", page = "organize_plate", args = arg_dict, bigdata = mysite.build_tables("organize_plate", args = arg_dict))


@app.route("/choose_plate")
@app.route("/choose_plate/<return_page>")
def choose_plate(return_page = ""):
    return_page = return_page if return_page != "" else "build_plate"
    myargs = dict(request.args)
    myargs['return_page'] = return_page
    return render_template("public/table_view.html", args=myargs, page = "choose_plate", bigdata = mysite.build_tables("choose_plate", myargs))

@app.route("/build_plate/<pid>")
@app.route("/build_plate/")
def build_plate(pid = ""):
    if "plate_id" not in request.args.keys() and pid == "":
        return redirect(url_for('choose_plate'))
    else:
        newargs = dict(request.args)
        newargs["plate_id"] = pid if pid != "" else newargs["plate_id"]
        return render_template("public/table_view.html", page = "build_plate", args = newargs, bigdata = mysite.build_tables("build_plate", args = newargs))

@app.route("/plate_report_new/<pid>")
@app.route("/plate_report_new/")
def plate_report_new(pid = ""):
    args = dict(request.args) if 'args' not in request.args.keys() else eval(request.args['args'])
    if "plate_id" not in args and pid == "":
        return redirect(url_for('choose_plate'))
    else:
        newargs = args
        newargs["plate_id"] = pid if pid != "" else newargs["plate_id"]
        return render_template("public/table_view.html", page = "plate_report", args = newargs, bigdata = mysite.build_tables("plate_report", args = newargs))


@app.route("/primer_list",  methods=['GET', 'POST'])
def primer_list():
    form = NewPrimer()
    print(form.validate())
    print(form.errors)
    if form.validate_on_submit():
        mysite.savePrimer(form)
    return render_template("public/primer_list.html", page = "primer_list", form = form, bigdata = mysite.build_tables("primer_list", args ={}))

@app.route("/design_plate/<args>")
@app.route("/design_plate/")
def design_plate(args = "{}"):
    arg_dict = eval(args)
    print(request.args)
    if "plate_id" not in request.args.keys() and "plate_id" not in arg_dict.keys():
        return redirect(url_for('choose_plate', return_page = "design_plate"))
    else:
        arg_dict = arg_dict if "plate_id" in arg_dict.keys() else dict(request.args)
        return render_template("public/table_view.html", page = "design_plate", args = arg_dict, bigdata = mysite.build_tables("design_plate", args = arg_dict))


@app.route("/new_plate")
def new_plate():
    return render_template("public/new_plate.html")

@app.route("/new_plate", methods = ['POST'])
def create_new_plate():
    mysite.add_row("plate_overview", request.form)
    mysite.log_comment(action = "created", user = "global", sampleid = "", plateid = request.form['plate_id'], comment = "")
    print(request.form['plate_id'])
    return redirect(url_for("build_plate", pid = str(request.form['plate_id'])))


@app.route("/set_sample_version", methods = ['POST'])
def set_sample_version():
    mysite.current_sample_version = request.form["sampv_dropdown"]
    mysite.load_data()
    print(request.method)
    return landing_page(args = request.args)

@app.route("/build_plate", methods = ["POST"])
def build_plate_samps():
    print(request.method)
    print(request.form)
    print(request.args)
    return redirect(url_for("/design_plate?"))

@app.route("/submit_table", methods= ["POST"])
def submit_table():
    submit_tab = request.args['table']
    mainpage = request.args['page']
    print(request.args)
    dd = eval(request.form['data'])["tables"][submit_tab]
    files = eval(request.form['data'])["files"]
    print(request.form['oldargs'])
    oldargs = eval(request.form['oldargs']) if len(request.form['oldargs']) > 0 else {}
    rd = ""
    sample_list = []
    for item,val in request.form.items():
        if val != "" and item not in ["data", "oldargs"]:
            page, pagetab, dd, col, row = item.split(".")
            pagetab = pagetab.replace("_", " ").title()
            if dd != "":
                dd = dd.replace("_", " ").title()
                main_id = eval("mysite." + files[pagetab]['dropdown'][dd]+".iloc["+row+",0]")
                main_col = eval("mysite." + files[pagetab]['dropdown'][dd]+".columns[0]")
                mysite.save_value(pagetab, col, row, val, main_id, main_col, current_user.username, files[pagetab]['dropdown'][dd])
            elif pagetab == "Build Plate" and col == "select_sample":
                sample_list.append(eval("mysite." + files[pagetab]['main_file']+".iloc["+row+",0]"))
                #mysite.add_sample_to_plate(eval("mysite." + files[pagetab]['main_file']+".iloc["+row+",0]"), oldargs['plate_id'], row = "", col = "")
            else:
                main_id = eval("mysite." + files[pagetab]['main_file']+".iloc["+row+",0]")
                main_col = eval("mysite." + files[pagetab]['main_file']+".columns[0]")
                mysite.save_value(pagetab, col, row, val, main_id =main_id, main_col=main_col, user=current_user.username)

    if len(sample_list)>0:
        mysite.add_samples_to_plate(sample_list, oldargs['plate_id'], row="", col = "")
        rd = "plate_organize"

    if rd != "":
        return redirect(url_for(rd, args = oldargs))
    if mainpage == "plate_report": 
        return redirect(url_for(mainpage+"_new", args = oldargs))
    else:
        redirstr = "/table_view.html?page="+mainpage
        for key, val in oldargs.items():
            redirstr = redirstr + "&" + key + "=" + val
        return redirect(redirstr)

@app.route("/view_datacsv/<filename>")
def view_datacsv(filename):
    data = pd.read_csv(os.path.join(mysite.basedir, 'static/resources/'+filename), index_col = 0)
    data.fillna('VOID', inplace=True)
    return render_template("public/view_datacsv.html", name = filename, data = data.to_html())

@app.route("/get_data")
def get_data(): 
    print(request.args)
    table =  request.args['table']
    args = json.loads(request.args['args'])
    resp = mysite.js_get_data(table, args)
    return resp

@app.route("/sequenced_plate/<pid>")
@app.route("/sequenced_plate")
def seq_plate_report(pid = ""): 
    args = dict(request.args) if 'args' not in request.args.keys() else eval(request.args['args'])
    if "plate_id" not in args and pid == "":
        return redirect(url_for('choose_plate'))
    else:
        newargs = args
        newargs["plate_id"] = pid if pid != "" else newargs["plate_id"]
        return render_template("public/sequenced_plate.html", page = "sequenced_plate", args = newargs, bigdata = mysite.build_tables("sequenced_plate", args = newargs))
 

@app.route("/plate_report/<pid>")
@app.route("/plate_report")
def plate_report(pid = ""): 
    args = dict(request.args) if 'args' not in request.args.keys() else eval(request.args['args'])
    if "plate_id" not in args and pid == "":
        return redirect(url_for('choose_plate'))
    else:
        newargs = args
        newargs["plate_id"] = pid if pid != "" else newargs["plate_id"]
        return render_template("public/plate_report.html", page = "plate_report", args = newargs, bigdata = mysite.build_tables("plate_report", args = newargs))
        render_template("public/table_view.html", page = "plate_report", args = newargs, bigdata = mysite.build_tables("plate_report", args = newargs))

    if "plate_id" in request.args.keys(): 
        return render_template("public/plate_report.html", plate_id = request.args["plate_id"])
    else: 
        return redirect("/")


@app.route("/table_view.html")
def landing():
    if mysite.datadict == {}:
        return redirect("/")
    elif request.args['page'] in mysite.pages['pages']:
        current_page = request.args['page']
        bd = mysite.build_tables(current_page, dict(request.args))
        return render_template("public/table_view.html", args=dict(request.args), page = current_page, bigdata = bd)
    else:
        return redirect("/")


@app.route("/plate_data", methods = ["POST"])
def add_plate_data():
    submit_tab = "Plate Report"
    dd = eval(request.form['data'])["tables"][submit_tab]
    files = eval(request.form['data'])["files"]
    rd = ""
    pdata = eval(request.form['plate_data'])
    for item,val in request.form.items():
        if val != "" and item not in ["plate_data", "data"]:
            page, pagetab, dd, col, row = item.split(".")
            pagetab = pagetab.replace("_", " ").title()
            if dd != "":
                dd = dd.replace("_", " ").title()
                main_id = eval("mysite." + files[pagetab]['dropdown'][dd]+".iloc["+row+",0]")
                main_col = eval("mysite." + files[pagetab]['dropdown'][dd]+".columns[0]")
                print(mysite.save_value(pagetab, col, row, val, main_id, main_col, current_user.username, files[pagetab]['dropdown'][dd]))
            elif pagetab == "Build Plate" and col == "select_sample":
                mysite.add_sample_to_plate(eval("mysite." + files[pagetab]['main_file']+".iloc["+row+",0]"), oldargs['plate_id'], row = "", col = "")
                rd = "plate_organize"
            else:
                main_id = eval("mysite." + files[pagetab]['main_file']+".iloc["+row+",0]")
                print(main_id)
                main_col = eval("mysite." + files[pagetab]['main_file']+".columns[0]")
                mysite.save_value(pagetab, col, row, val, main_id =main_id, main_col=main_col, user =current_user.username)
    return redirect(url_for("plate_report", pid = pdata["plate_id"][0]))

@app.route("/seq_plate_data", methods = ["POST"])
def add_seq_plate_data():
    submit_tab = "Sequenced Samples"
    dd = eval(request.form['data'])["tables"][submit_tab]
    files = eval(request.form['data'])["files"]
    rd = ""
    pdata = eval(request.form['plate_data'])
    for item,val in request.form.items():
        if val != "" and item not in ["plate_data", "data"]:
            page, pagetab, dd, col, row = item.split(".")
            pagetab = pagetab.replace("_", " ").title()
            if dd != "":
                dd = dd.replace("_", " ").title()
                main_id = eval("mysite." + files[pagetab]['dropdown'][dd]+".iloc["+row+",0]")
                main_col = eval("mysite." + files[pagetab]['dropdown'][dd]+".columns[0]")
                print(mysite.save_value(pagetab, col, row, val, main_id, main_col, current_user.username, files[pagetab]['dropdown'][dd]))
            elif pagetab == "Build Plate" and col == "select_sample":
                mysite.add_sample_to_plate(eval("mysite." + files[pagetab]['main_file']+".iloc["+row+",0]"), oldargs['plate_id'], row = "", col = "")
                rd = "plate_organize"
            else:
                main_id = eval("mysite." + files[pagetab]['main_file']+".iloc["+row+",0]")
                print(main_id)
                main_col = eval("mysite." + files[pagetab]['main_file']+".columns[0]")
                mysite.save_value(pagetab, col, row, val, main_id =main_id, main_col=main_col, user = current_user.username)
    return redirect(url_for("seq_plate_report", pid = pdata["plate_id"][0]))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect("/")
        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + '' + form.password.data + '</h1>'
    return render_template('public/login.html', form=form)


@app.route('/logout') 
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

