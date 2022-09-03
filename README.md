# LBP Print Api

## Running locally

Start the Flask app
```
python3 app.py
```

Start the redis server
````
redis-server
```

Start the redis worker
```
rq worker
```

# Web app for viewing Lombard Press compliant transcriptions in PDF

One of the many advantages of encoding transcriptions or editions in a semantic
markup language is the separation of presentation and content. This means that
the same file can serve different purposes and be used in different contexts.
One incarnation may represent the text as a traditional critical edition set up
on a print page with one or several critical apparatus, another incarnation may
be a interactive web page presenting the text alongside images of a manuscript,
and yet another a e-reader friendly version with explanatory notes for students.

But this separation of presentation and content also means that it may be
difficult to envision how a finished edition may look like. This app provides an
easy interface for converting a XML transcription to a pdf document.

Your XML document must be valid and in compliance with
the [LombardPress Schema](http://lombardpress.org/schema/docs/) for critical and
diplomatic editions.

You can either upload you own documents or fetch a document from
the [scta database](http://lombardpress.org/schema/docs/). If you have your own
XSLT script for conversion of the XML document, you can upload that. Otherwise
the app will use a default Lombard Press transformation script. The script used
is based on which version of the LombardPress Schema that the transcription is
based on.

## RESTful interface

On the url `/compile` you can also pass the id and output as url parameters. The
url could then look like this:

```
<hostname>/compile?id=lectio1&output=tex
```

This will return a JSON response of either an error message or the url of the
output file.

Parameters:
- `id`: A valid SCTA id. It can either be a full SCTA url
  (`http://scta.info/resource/lectio1`) or just the id (`lectio1`).
- `output`: Which format should be created? Possibilities are `tex` and `pdf`.

When you have a running instance, try `curl -i
http://127.0.0.1:5000/compile\?id\=http://scta.info/resource/lectio1` (or
replace the hostname appropriately).

## Warning

This is still a young app, so it may produce unexpected output. Anything may be
subject to change, and I cannot guarantee for the safety of your texts, computer
or sanity when using the app.

Please report any problems you experience in
the [issue tracker](https://github.com/stenskjaer/lbp_print-web-app/issues).

# Development

Download the repo:
```
git clone https://github.com/stenskjaer/lbp_print-web-app.git
```

If you just want to experiment locally (or maybe make a pull request!), you
should probably create
a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
for the project. To do that, run:

```bash
$ mkvirtualenv -p python3 <name>
```
Where `<name>` is the name you want to give the venv.

After activating the venv (`workon` or `source`), install dependencies:
```bash
$ pip install -r requirements.txt
```

Finally, you also need to create some directories:
```shell
mkdir -p upload static/output logs
```

You can run a local development server with `python3 service.py` if you want to
test it with `gunicorn` (equivalent to the Dockerized server), run:
```bash
gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 service:app
```

# Docker image

If you want to build the Docker image, run (from the project directory):
```
docker build -t lbp-print .
```

Now, to run: 
```
docker run -p 80:80 lbp-print
```

The app should be available on [localhost](http://localhost).

# Contribute

All pull requests and issue reports are very welcome! ♡


to build for a specific architecture run as follows: 

`docker buildx build --platform linux/amd64 -t jeffreycwitt/lbp-print-api:latest --push .`