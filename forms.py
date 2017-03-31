from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import RadioField, StringField

class TranscriptionForm(FlaskForm):
    xml_upload_remote = RadioField('Upload or get XML from SCTA?', default='remote',
                                   description='If you want to use a local XML file, you can upload it. Otherwise you '
                                               'can provide a SCTA resource id.',
                                   choices=[('remote', 'Remote'), ('upload', 'Upload')])
    xslt_upload_default = RadioField('Upload or use default XSLT?', default='default',
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

