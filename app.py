from flask import Flask
from flask import render_template, send_from_directory, flash, redirect, url_for, request
import logging
import os
import random
import json
import sqlite3

# const
DATA = '~/projects/pamudoan/src/pamudoan_data/pdf'
DBFN = '~/projects/pamudoan/src/pamudoan_data/db/pamudoan.db'
PVP_USER_HEADER = 'X-PORTAL-USER'

# init flask
app = Flask(__name__)
random.seed()
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# init flask-logger. use the gunicorn-logger, if possible
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
logging.basicConfig(level=logging.INFO, format=f'%(asctime)s %(levelname)s %(message)s')#


# get all documents from the filesys 
# read rawdata file-names
# rawdata_path = DATA
# rawdata_files = os.listdir(rawdata_path)
# app.logger.info(f"Found {len(rawdata_files)} rawdata-documents in {rawdata_path}")



####################################################################
#########            H E L P E R                          ##########
####################################################################
def check_config() -> bool:
    '''
    Try to load Environment/shell-variables: 
     * PAMUDOAN_DATA: path to pdfs with no trailing slash
     * PAMUDOAN_DB: sqlite db-file.
    Return True (and sets the global variables) if both are set on flask-startup
    '''
    global DATA
    global DBFN
    try:
        DATA = os.environ['PAMUDOAN_DATA']
        DBFN = os.environ['PAMUDOAN_DB']
        app.logger.info("INIT: Environment ok. PAMUDOAN_DATA='{}' PAMUDOAN_DB='{}'".format(DATA, DBFN))
        return True
    except:
        app.logger.error("INIT: Environment/Shell-Variables missing: PAMUDOAN_DATA and PAMUDOAN_DB")
        return False


def check_db() -> bool:
    '''
    Check sqlite-db connection. Try to open, select, close. 
    Return True, if DB is ok.
    '''
    try:
        # try to connect to sqlite3-db and get allavailable documents
        con = sqlite3.connect(DBFN)
        cur = con.cursor()
        cur.execute('select count(id) from document')
        cnt_docs = cur.fetchone()[0]
        con.close()
        app.logger.info("INIT: Database ready. Found {} documents.".format(cnt_docs))
        return True
    except Exception as e:
        app.logger.error(f"INIT: Can't open sqlite DB '{DBFN}': {e}")
        return False

def get_docfn(id, dbcon) -> str:
    '''check if document with id is available. Return the docfn (filename) if found. Empty str otherwise'''
    cur = dbcon.cursor()
    cur.execute('select id, filename from document where id = ?', (id,))
    r = cur.fetchone()
    return r[1] if r else ""

    
def get_rnd_docid(dbcon) -> int: 
    '''Returns randomly an un-annotated doc-id or -1 if all documents were annotated. TODO: add inter-annotator-agreement-level'''
    cur = dbcon.cursor()
    cur.execute('select id from document where id not in (select documentid from annotation)')
    docs_to_annotate = cur.fetchall()

    rnd_id = random.choice(docs_to_annotate)[0] if docs_to_annotate else -1
    return rnd_id


def get_category_data(dbcon):
    '''
    Returns the data for the category-combo-box. (from DB). Data looks like:
    [
        [   "Plan", 
            [ {'label': "Lageplan", 'value': "p001"}, {'label': "Grundriss", 'value': "p002"} ]
        ],
        [   "Gutachten", 
            [ {'label': "Gutachten Schall", 'value': "g002"}, ]
        ]
    ]    
    '''
    cur_groups = dbcon.cursor()
    cur_labels = dbcon.cursor()
    r = list()

    cur_groups.execute('SELECT DISTINCT label_group FROM labeltree')
    group_list = cur_groups.fetchall()
    for g in group_list:
        gname = g[0]
        labels4group = list()
        cur_labels.execute('SELECT label_id, label_group, label_name FROM labeltree where label_group = ?', (gname, ))
        labels_list = cur_labels.fetchall()
        for l in labels_list:
            lval = l[0]
            lnam = l[2]
            labels4group.append({'label':lnam, 'value':lval})
        r.append([gname, labels4group])

    return r


def get_username() -> str:
    '''Returns the pvp-username or 'anonymous'.'''
    usr = "anonymous"
    if PVP_USER_HEADER in request.headers:
        usr = request.headers.get(PVP_USER_HEADER)
    return usr




####################################################################
#########            M A I N                              ##########
####################################################################
if not check_config() or not check_db():
    exit(1)


#####################################
## annotation-form for a rnd document
@app.route("/")
def main():
    con = sqlite3.connect(DBFN)
    username  = get_username()
    rnd_docid = get_rnd_docid(con)
    rnd_docfn = get_docfn(rnd_docid, con)
    lo = get_category_data(con)
    con.close()

    if rnd_docid != -1:
        app.logger.info(f"MAIN ({username}): using random docid={rnd_docid} ({rnd_docfn})")
        return render_template("main.html", docid=rnd_docid, docfn=rnd_docfn, labeloptions=lo, user=username)
    else:
        # every doument is annoted - nothing left to do :)
        app.logger.info(f"MAIN ({username}): all done, no more documents left to annotate :)")
        return render_template("alldone.html", user=username)



#####################################
## send rawdata pdf-document (if exist)
@app.route("/doc/<int:id>")
def get_doc(id):
    con = sqlite3.connect(DBFN)
    docfn = get_docfn(id, con)
    if docfn:
        return send_from_directory(DATA, docfn)
    else:
        app.logger.warning(f"DOC: docid {id} not found in db")
        return f"Document #{id} not found. Sorry."


#####################################
## save/add new annotation
@app.route("/save/", methods=['POST'])
def save_annotation():
    con = sqlite3.connect(DBFN)
    username  = get_username()

    # extract carefuly the data from html-form json. Redirect to main on error
    try:
        reqdata = request.form.get('jsondata')
        app.logger.info(f"SAVE ({username}): {reqdata}")
        data = json.loads(str(reqdata))
        docid = data['docid']
        docfn = get_docfn(docid, con)
        annotations = data['annotations']
        if not docfn:
            raise Exception(f"Document id={docid} not found in db.")
        if not (type(annotations) is list and len(annotations) > 0):
            raise Exception(f"No annotation/labels in there.")
    except Exception as e:
        con.close()
        flash(f"Nicht gespeichert, Daten ungültig.", 'danger')
        app.logger.warning(f"SAVE CHANCELED ({username}) by corrupt data: {e}")
        return redirect(url_for('main'))

    # save the new annotation + labels to DB. Rollback on error
    try:
        cur = con.cursor()
        cur.execute('BEGIN TRANSACTION')
        # add a new annotation for the document
        cur.execute("insert into annotation (documentid, username) values (?, ?)", 
            (docid, username))
        new_annotation_id = cur.lastrowid
        # add labels to the new annotation
        for a in annotations:
            a_label  = a['category']
            a_startp = a['startpage']
            a_endp   = a['endpage']
            cur.execute("insert into label (label, startpage, endpage, annotationid) values (?,?,?,?)", 
                (a_label, a_startp, a_endp, new_annotation_id))
        con.commit()

        # user feedback
        app.logger.info(f"SAVE DONE ({username}): new annotation for docid={docid} saved (id={new_annotation_id} with {len(annotations)} labels)")
        flash(f'Gespeichert.', 'success')
    except Exception as e:
        con.rollback()
        app.logger.warning("SAVE CHANCELED by DB: {}".format(e))
        flash(f'Nicht gespeichert', 'danger')
            
    # done. now bring user back to the start/main to annotate the next rnd document
    con.close()
    return redirect(url_for('main'))

