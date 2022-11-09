# PAMUDOAN - PACE Multi-Document-Annotationtool #

Annotate PDF files, which includes more than one document (i.e. from "MA6-Scanzentrum").

## install ##
1. Create and activate a new Python3 Virtual-Env
2. Clone this GIT-Repo
3. Install Python dependencies via pip


```
    python3 -m venv [INSTALL-PATH]
    cd [INSTALL-PATH]
    source bin/activate

    mkdir src; cd src
    git clone [BITBUCKET-URL]

    cd pamudoan
    pip install -r requirements.txt
```

## run ##
Gubicorn is installed (production-ready wsgi-server). Flask will also serve its own development-server.

Start Production-Server (gunicorn with 4 worker-threats)

```
    cd pamudoan
    PAMUDOAN_DATA=[RAWDATA-PATH] PAMUDOAN_DB=[SQLITE-DB] gunicorn -w 4 wsgi:app
```
Start Development-Server (flask only)

```
    cd pamudoan
    PAMUDOAN_DATA=[RAWDATA-PATH] PAMUDOAN_DB=[SQLITE-DB] python -m flask run
```

