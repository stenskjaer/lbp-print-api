from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

from werkzeug.utils import secure_filename
import lbp_print
import os
import json
import multiprocessing

from forms import TranscriptionForm
from upload_file import UploadFile



app = Flask(__name__, instance_path=os.getcwd())
app.config.from_object(__name__)  # load config from this file
app.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    UPLOAD_FOLDER=os.path.join(app.instance_path, 'upload')
))
socketio = SocketIO(app)


import logging
import logging.handlers
#
# root = logging.getLogger()
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
# ch.setFormatter(formatter)
# root.addHandler(ch)


# TODO: Wrap up the upload functionality.
ALLOWED_EXTENSIONS = {'xml', 'xslt'}
IGNORED_FILES = {'.gitignore'}


def upload_file(form_data):
    """
    Save the file given in form.data to upload folder and return the filename.

    :param form_data: FileStorage object from form.data.
    :return: file name.
    """
    # TODO: Build this upload function together with the upload utility
    f = form_data
    filename = secure_filename(f.filename)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])
    file_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    f.save(file_location)
    return file_location


def allowed_file(filename):

    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # request.files dictionary holds data about the file object. They are indexed by input name value (<input
        # name="xxx">) but we want to the info even though we don't know the name value in advance, so we need to
        # always just get the first item in the dictionary (as there will always be just one item).
        file_obj = next(iter(request.files.values()))

        if file_obj:
            filename = secure_filename(file_obj.filename)
            mime_type = file_obj.content_type

            if not allowed_file(file_obj.filename):
                result = UploadFile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")

            else:
                # save file to disk
                uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_obj.save(uploaded_file_path)

                # get file size after saving
                size = os.path.getsize(uploaded_file_path)

                # return json for js call back
                result = UploadFile(name=filename, type=mime_type, size=size)

            return json.dumps({"files": [result.get_file()]})

    else:
        # TODO: Make proper error handling of upload url when method is not POST.
        return('Error')


@socketio.on('submit_form')
def process_file(form):
    # TODO: We really need some form validation action before moving on with the processing.

    # Start the processing
    # When the stream process is successful, it returns the filename of the tex or pdf file.
    filename = stream_processing(form)

    emit('server_form_response', {'content': 'Conversion done!'})

    if form['tex_or_pdf'] == 'tex':
        file_ext = '.tex'
    else:
        file_ext = '.pdf'
    emit('redirect', {'url': filename})


def stream_processing(form):
    listener_formatter = logging.Formatter(
        '%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')

    queue = multiprocessing.Queue(0)
    process_worker = multiprocessing.Process(target=process_function, args=(queue, form))
    process_worker.start()
    while True:
        try:
            record = queue.get()
            if isinstance(record, Exception):
                # We have caught an exception that we raise and return.
                raise record
            elif isinstance(record, str):
                # We have finished successfully and received the filename as final item in queue.
                # We should now return that to the handler.
                break
            elif isinstance(record, logging.LogRecord):
                emit('server_form_response', {'content': listener_formatter.format(record)})
            else:
                raise TypeError('Unexpected queue object type.')
            socketio.sleep(0.001)
        except:
            raise
    return record


def process_function(queue, form):
    h = logging.handlers.QueueHandler(queue)
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.DEBUG)

    logging.info('Starting conversion...')
    if form['xml_upload_or_remote'] == 'upload':
        try:
            xml_path = os.path.join(app.config['UPLOAD_FOLDER'], form['xml_file'])
            transcription = lbp_print.LocalTranscription(xml_path)
        except Exception as e:
            return queue.put(e)
    else:
        transcription = lbp_print.RemoteTranscription(form['scta_id'], download_dir='upload')

    if form['xslt_default_or_remote'] == 'default':
        xslt_script = lbp_print.select_xlst_script(transcription)
    else:
        xslt_script = upload_file(form['xslt_file'])

    tex_file = lbp_print.convert_xml_to_tex(transcription.file.name, xslt_script, output='static/output')
    tex_file = lbp_print.clean_tex(tex_file)

    if form['tex_or_pdf'] == 'tex':
        logging.info('Send tex file.')
        return queue.put(tex_file.name)
    else:
        logging.info('Compile tex file.')
        pdf_file = lbp_print.compile_tex(tex_file)
        return queue.put(pdf_file.name)


@app.route('/')
def submit():
    form = TranscriptionForm()
    return render_template('index_form.html', form=form)


if __name__ == '__main__':
    socketio.run(app, debug=True)
#
# if __name__ == "__main__":
#     app.run(debug=True)
