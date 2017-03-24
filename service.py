from flask import Flask, render_template, send_file, Response
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import RadioField, StringField
from werkzeug.utils import secure_filename

import lbp_print
import os
import subprocess
import io

app = Flask(__name__, instance_path=os.getcwd())
app.config.from_object(__name__)  # load config from this file
app.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    UPLOAD_FOLDER=os.path.join(app.instance_path, 'upload')
))


import logging

root = logging.getLogger()
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


class TranscriptionForm(FlaskForm):
    xml_upload_remote = RadioField('Upload or get XML from SCTA?', default='remote',
                                   description='If you want to use a local XML file, you can upload it. Otherwise you '
                                               'can provide a SCTA resource id.',
                                   choices=[('remote', 'Remote'), ('upload', 'Upload')])
    xslt_upload_default= RadioField('Upload or use default XSLT?', default='default',
                                    description='Supply a custom xslt transformation stylesheet or use the default '
                                                'system stylesheets. If the default system stylesheets are chosen, '
                                                'the correct stylesheet will be determined based on the '
                                                '<code>schemaRef</code> in the XML file.',
                                    choices=[('default', 'Default'), ('upload', 'Upload')])
    pdf_tex = RadioField('Return PDF or TeX', description="Choose whether you want to get a PDF or TeX file.",
                         default='tex', choices=[('tex', 'TeX'), ('pdf', 'PDF')])
    scta_id = StringField('SCTA Id', description='The SCTA id is the id of the resource that you want to process. '
                                                 'Resource ids can be identified on <a '
                                                 'href="http://scta.info">scta.info</a>. For instance <a '
                                                 'href="http://scta.info/resource/deAnima">scta.info/resource/deAnima'
                                                 '</a> lists all resource ids of De anima commentaries, '
                                                 'while <a '
                                                 'href="http://scta.info/resource/sententia">scta.info/resource'
                                                 '/sententia</a> lists all Sentence commentaries, and from there the '
                                                 'resource ids of each the relevant work items.')
    xml_upload = FileField('XML Upload',
                           description='The uploaded file must be valid XML and in comliance with the LombardPress '
                                       'Schema.')
    xslt_upload = FileField('XSLT Upload')


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


def stream():

    import pdb; pdb.set_trace()
    def invoke_subprocess(bufsize):
        lbp_call = 'python /Users/michael/Documents/coding/SCTA/lbp_print/lbp_print.py pdf --local  /Users/michael/Documents/PhD/transcriptions/aegidius-expositio/da-199-prol/mun2805_da-199-prol.xml --xslt /Users/michael/Documents/PhD/transcriptions/tools/xslt/standalone-print/1.0.0/diplomatic.xslt'
        return subprocess.Popen(lbp_call, shell=True, stdout=subprocess.PIPE, bufsize=bufsize)


    p = invoke_subprocess(1)
    import pdb; pdb.set_trace()
    for line in io.open(io_buffer):
        yield line.rstrip('\n')


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    return rv


@app.route('/streamer')
def streamer():
    rows = stream()
    return Response(stream_template('test.html', rows=rows))


@app.route('/', methods=('GET', 'POST'))
def submit():
    form = TranscriptionForm()


    if form.validate_on_submit():

        if form.xml_upload_remote.data == 'upload':
            transcription = lbp_print.LocalTranscription(upload_file(form.xml_upload.data))
        else:
            transcription = lbp_print.RemoteTranscription(form.scta_id.data)

        if form.xslt_upload_default.data == 'default':
            xslt_script = lbp_print.select_xlst_script(transcription)
        else:
            xslt_script = upload_file(form.xslt_upload.data)

        tex_file = lbp_print.convert_xml_to_tex(transcription.file.name, xslt_script)

        if form.pdf_tex.data == 'tex':
            return send_file(tex_file.name)

        pdf_file = lbp_print.compile_tex(tex_file)

        return send_file(pdf_file.name)

    return render_template('index_form.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)
