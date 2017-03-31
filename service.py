from flask import Flask, render_template, send_file, Response, redirect

from forms import TranscriptionForm
from werkzeug.utils import secure_filename

import lbp_print
import os
import subprocess
import io
import sys
import multiprocessing

app = Flask(__name__, instance_path=os.getcwd())
app.config.from_object(__name__)  # load config from this file
app.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    UPLOAD_FOLDER=os.path.join(app.instance_path, 'upload')
))


import logging
import logging.handlers

root = logging.getLogger()
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


def upload_file(form_data):
    """
    Save the file given in form.data to upload folder and return the filename.

    :param form_data: FileStorage object from form.data.
    :return: file name.
    """
    f = form_data
    filename = secure_filename(f.filename)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])
    file_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    f.save(file_location)
    return file_location


@app.route('/', methods=('GET', 'POST'))
def submit():
    form = TranscriptionForm()


    if form.validate_on_submit():


        def stream_template(template_name, **context):
            app.update_template_context(context)
            t = app.jinja_env.get_template(template_name)
            rv = t.stream(context)
            return rv

        def process_function(queue, transcription):
            h = logging.handlers.QueueHandler(queue)
            root = logging.getLogger()
            root.addHandler(h)
            root.setLevel(logging.DEBUG)

            if form.xslt_upload_default.data == 'default':
                xslt_script = lbp_print.select_xlst_script(transcription)
            else:
                xslt_script = upload_file(form.xslt_upload.data)

            tex_file = lbp_print.convert_xml_to_tex(transcription.file.name, xslt_script)

            # if form.pdf_tex.data == 'tex':
            #     return send_file(tex_file.name)
            #
            # pdf_file = lbp_print.compile_tex(tex_file)
            #
            # return send_file(pdf_file.name)

            queue.put(None)


        def stream(transcription):
            listener_formatter = logging.Formatter(
                '%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')

            queue = multiprocessing.Queue(0)
            process_worker = multiprocessing.Process(target=process_function, args=(queue, transcription))
            process_worker.start()
            while True:
                try:
                    record = queue.get()
                    if record is None:
                        break
                    yield listener_formatter.format(record)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except:
                    import sys, traceback
                    print('Whoops! Problem:', sys.stderr)
                    traceback.print_exc(file=sys.stderr)


        if form.xml_upload_remote.data == 'upload':
            transcription = lbp_print.LocalTranscription(upload_file(form.xml_upload.data))
        else:
            transcription = lbp_print.RemoteTranscription(form.scta_id.data)
        rows = stream(transcription)
        return Response(stream_template('test.html', rows=rows))


    return render_template('index_form.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)
