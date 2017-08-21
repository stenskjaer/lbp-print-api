from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from logging import handlers

from werkzeug.utils import secure_filename
import os
import json
import multiprocessing
import logging
import logging.handlers
import lbp_print.core as lbp_print
import lbp_print.config as lbp_config

lbp_config.cache_dir = 'cache'

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

root = logging.getLogger()
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARN)
file_handler = handlers.RotatingFileHandler('logs/service.log', maxBytes=1024*1000, backupCount=5)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
root.addHandler(stream_handler)
root.addHandler(file_handler)


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

    emit('redirect', {'url': filename})


def stream_processing(form):
    listener_formatter = logging.Formatter(
        '%(levelname)s %(asctime)s %(message)s')

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
                if record.levelname in ['INFO', 'WARNING', 'ERROR']:
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

    logging.info('Starting conversion process...')
    try:
        xslt_script = None
        if form['xslt_default_or_remote'] == 'default':
            logging.info('Using default XSLT conversion script.')
        else:
            logging.info('Using uploaded XSLT conversion script.')
            xslt_script = os.path.join(app.config['UPLOAD_FOLDER'], form['xslt_file'])

        if form['xml_upload_or_remote'] == 'upload':
            logging.info('Uploaded file received.')
            xml_path = os.path.join(app.config['UPLOAD_FOLDER'], form['xml_file'])
            trans = lbp_print.LocalTranscription(xml_path, custom_xslt=xslt_script)
        else:
            logging.info('Looking for remote resource.')
            trans = lbp_print.RemoteTranscription(form['scta_id'], custom_xslt=xslt_script)

        if form['tex_or_pdf'] == 'tex':
            format = 'tex'
        else:
            format = 'pdf'

        return queue.put(lbp_print.Tex(trans, output_format=format,
                                       output_dir='static/output').process())

    except Exception as e:
        return queue.put(e)


@app.route('/compile')
def service():
    parameters = {
        'scta_id': request.args.get('id'),
        'tex_or_pdf': request.args.get('output', 'tex'),
    }

    from flask import jsonify, make_response

    try:

        logging.info('Looking for remote resource.')
        trans = lbp_print.RemoteTranscription(parameters['scta_id'])

        if parameters['tex_or_pdf'] == 'tex':
            format = 'tex'
        else:
            format = 'pdf'

        logging.info('Using default XSLT conversion script.')
        res_file = lbp_print.Tex(trans, output_format=format, output_dir='static/output').process()

    except AttributeError:
        error_message = "You gave the following parameters: %s. 'tex_or_pdf' must be either " \
                        "'tex' or 'pdf' (default is 'tex'). 'scta_id' must be a valid SCTA id" \
                        " (full url or id)." \
                        % format(parameters)
        return make_response(jsonify({'error': error_message}), 404)
    return jsonify({'url': request.host + '/' + res_file})

@app.route('/')
def submit():
    form = TranscriptionForm()
    return render_template('index_form.html', form=form)


if __name__ == '__main__':
    socketio.run(app, debug=True)
