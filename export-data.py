import logging
import os
import argparse
import sqlite3
from PyPDF4 import PdfFileWriter, PdfFileReader


# cli-params
ap = argparse.ArgumentParser(description="pamudoan - data exporter")
ap.add_argument("-d", "--data", required=True, default='',
    help="path to the raw data (PDFs).")
ap.add_argument("-o", "--out", required=True, default='',
    help="path for output. In there, one subdirectory per label. In there, the exported pdf-snippets")
ap.add_argument("-b", "--db", required=True, default='',
    help="sqlite3 database-file")
ap.add_argument("-l", "--loglevel", required=False, default='info',
    help="'info' (default) or 'debug'")
ap.add_argument("-c", "--conflict", required=False, default='overwrite',
    help="NOT IMPLEMENTED! how to solve filename-conflicts while exporting: 'overwrite' existing file (default) or create a 'new' one (adds '_1', '_2').")
args = vars(ap.parse_args())

# const
DATA = os.path.abspath(args['data'])
OUT  = os.path.abspath(args['out'])
DBFN = args['db']

# init logger
if args['loglevel'] == 'debug':
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)


####################################################################
#########            H E L P E R                          ##########
####################################################################
def check_env() -> bool:
    '''
    Check sqlite-db connection. Try to open, select, close. 
    Return True, if DB is ok.
    '''
    try:
        # check DB
        con = sqlite3.connect(DBFN)
        con.close()

        # check DATA-PATH
        if not (os.path.exists(DATA) and os.path.isdir(DATA)):
            raise FileNotFoundError(f"data-path '{DATA}' not a directory.")
        # check OUT-PATH
        if not (os.path.exists(OUT) and os.path.isdir(OUT)):
            raise FileNotFoundError(f"out-path '{OUT}' not a directory.")

        logging.info("INIT: Database ready. DATA-Path ok. OUT-Path ok.")
        return True
    except Exception as e:
        logging.error(f"INIT: {e}")
        return False



####################################################################
#########            M A I N                              ##########
####################################################################
if not check_env():
    exit(1)

# get all labels from db
con = sqlite3.connect(DBFN)
cur = con.cursor()
cur.execute("select * from labeling where label <> ''")
labeling = cur.fetchall()
con.close()

# export each label to a new pdf-file
n = len(labeling)
i = 0
for i, l in enumerate(labeling):
    try:
        docid   = str(l[0])
        docfn   = str(l[1])
        labelid = int(l[2])
        label   = str(l[3])
        startp  = int(l[4])
        endp    = int(l[5])
        a_usr   = str(l[7])
        a_dt    = str(l[8])
        
        infn    = f"{DATA}/{docfn}"
        outdir  = f"{OUT}/{label}"
        outfn   = f"{outdir}/{label}-{labelid}__{docfn}"

        if not os.path.exists(infn):
            raise FileNotFoundError(f"Inputfile {infn} not found")
        logging.info(f"[{i+1}/{n}] Export label '{label}' (page {startp}-{endp}) from '{docfn}' (by {a_usr}, {a_dt})...")
        input_pdf  = PdfFileReader(infn)
        output_pdf = PdfFileWriter()

        # Now export pages:
        #  1. copy/export the relevant pages from the docfn
        for p in range(startp - 1, endp):
            logging.debug(f"Add page {p} to output")
            output_pdf.addPage(input_pdf.getPage(p))
        # 2. create new sub-directory for the label (if not already exist) 
        if not os.path.exists(outdir):
            logging.debug(f"Create sub-directory '{outdir}' for label '{label}'")
            os.mkdir(outdir)
        # 3.  finaly save new pdf-file
        with open(outfn, "wb") as output_pdf_stream:
            output_pdf.write(output_pdf_stream)
            logging.info(f"Saved {endp-(startp-1)} pages to '{outfn}' done.")
    except Exception as e:
        logging.warning(f"[{i+1}/{n}] Skiped! {str(e)}")

# TODO: txt-file: dump current ĺabeltree and labeling from db 
logging.info("Finish.")





