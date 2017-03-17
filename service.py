from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import RadioField, StringField

import lbp_print

app = Flask(__name__)
app.config.from_object(__name__)  # load config from this file
app.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))


class TranscriptionForm(FlaskForm):
    xml_upload_remote = RadioField('Upload or SCTA XML', default='upload',
                                   description='If you want to use a local XML file, you can upload it. Otherwise you '
                                               'can provide a SCTA resource id.',
                                   choices=[('upload', 'Upload'), ('remote', 'Remote')])
    xslt_upload_remote = RadioField('Upload or default XSLT', default='upload',
                                    description='Supply a custom xslt transformation stylesheet or use the default '
                                                'system stylesheets.',
                                    choices=[('upload', 'Upload'), ('remote', 'Remote')])
    pdf_tex = RadioField('Return PDF or TeX', default='tex', choices=[('tex', 'TeX'), ('pdf', 'PDF')])
    scta_id = StringField('SCTA Id')
    xml_upload = FileField('XML Upload')
    xslt_upload = FileField('XSLT Upload')


@app.route('/success')
def success():
    return render_template('process.html', form=request.args.get('form'))

# Function resource ID: http://scta.info/resource/da-49-l1q1
@app.route('/', methods=('GET', 'POST'))
def submit():
    form = TranscriptionForm()
    if form.validate_on_submit():
        if form.xml_upload_remote == 'upload':
            transcription = lbp_print.LocalTranscription(form.xml_upload.data)
        else:
            transcription = lbp_print.RemoteTranscription(form.scta_id.data)
        print('created transcription object')

        if form.xslt_upload_remote == 'upload':
            xslt_script = form.xslt_upload.data
        else:
            xslt_script = lbp_print.select_xlst_script(transcription)
        print('chose transformation script')

        tex_file = lbp_print.convert_xml_to_tex(transcription.file.name, xslt_script)
        print('converted to tex')

        pdf_file = lbp_print.compile_tex(tex_file)
        print(transcription)
        return redirect(url_for('success'))
    return render_template('index_form.html', form=form)

if __name__ == '__main__':
    app.run(host='0.0.0.0')