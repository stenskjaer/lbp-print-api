from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import RadioField, StringField
from werkzeug.utils import secure_filename

import lbp_print
import os

app = Flask(__name__, instance_path=os.getcwd())
app.config.from_object(__name__)  # load config from this file
app.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    UPLOAD_FOLDER=os.path.join(app.instance_path, 'upload')
))


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

@app.route('/success')
def success():
    return render_template('process.html', form=request.args.get('form'))

# Function resource ID: http://scta.info/resource/da-49-l1q1
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_debugger=True)
