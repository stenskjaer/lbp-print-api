#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""LBP print as a service.

Usage:
  lbp-print-service.py (tex|pdf) [options] --local <file>
  lbp-print-service.py (tex|pdf) [options] --scta <expression-id>

Pull LBP-compliant files from SCTA repositories, convert them into tex or pdf.

Arguments:
  <file>                  Location of (local) file to be processed.
  <expression-id>         The expression id of the item to be processed.

Commands:
  tex                     Convert the xml to a tex-file.
  pdf                     Convert the xml to a tex-file and compile it into a pdf.

Options:
  --scta                  Boolean. When True, the <identifier> should be an expression id of the
                          SCTA database.
  --local                 Boolean. Process local file.
  -V, --verbosity <level> Set verbosity. Possibilities: silent, info, debug [default: debug].
  -v, --version           Show version and exit.
  -h, --help              Show this help message and exit.
"""

from docopt import docopt
import subprocess
import logging
import untangle
import lbppy
import urllib
import os
import lxml


class Transcription:
    """The main object of the script, defining the properties of the text under processing."""

    def __init__(self, input):
        self.input = input

    def get_schema_info(self):
        """Return schema version info."""
        pass

    def __define_file(self):
        """Return file object.
        """
        pass

class LocalTranscription(Transcription):
    """Object for handling local files."""

    def __init__(self, input):
        Transcription.__init__(self, input)
        self.file = self.__define_file()
        self.lbp_schema_info = self.get_schema_info()

    def get_schema_info(self):
        """Return the validation schema version."""
        schemaRef_number = lxml.etree.parse(self.file).xpath(
            "/tei:TEI/tei:teiHeader[1]/tei:encodingDesc[1]/tei:schemaRef[1]/@n",
            namespaces={"tei": "http://www.tei-c.org/ns/1.0"}
        )[0]                # The returned result is a list. Grab first element.
        if schemaRef_number:
            return {
                'version': schemaRef_number.split('-')[2],
                'type': schemaRef_number.split('-')[1]
            }
        else:
            raise BufferError('The document does not contain a value in '\
                              'TEI/teiHeader/encodingDesc/schemaRef[@n]')

    def __define_file(self):
        """Return the file object.
        """
        file_argument = self.input
        if os.path.isfile(file_argument):
            return open(file_argument)
        else:
            raise IOError( f"The supplied argument ({file_argument}) is not a file." )


class RemoteTranscription(Transcription):
    """Object for handling remote transcriptions.

    Keyword arguments:
    input -- SCTA resource id of the text to be processed.
    """
    def __init__(self, input):
        Transcription.__init__(self, input)
        self.resource = lbppy.Resource.find(input)
        self.canonical_transcriptions = [m.resource().canonical_transcription()
                                         for m in self.resource.manifestations()]
        self.transcription_object = [trans for trans in self.canonical_transcriptions
                                     if trans.resource().transcription_type() == 'critical'][0]
        if not self.transcription_object:
            # If no critical, can we just take the first diplomatic? Better alternatives?
            self.transcription_object = self.canonical_transcriptions[0]
        self.file = self.__define_file()
        self.lbp_schema_info = self.get_schema_info()

    def get_schema_info(self):
        """Return the validation schema version."""
        return {
            'version': self.transcription_object.resource().file().validating_schema_version(),
            'type': self.transcription_object.resource().transcription_type()
        }

    def __define_file(self):
        """Determine whether the file input supplied is local or remote and return its file object.
        """
        logging.debug("Remote resource located. Downloading ...")
        transcription_file, _ = urllib.request.urlretrieve(
            self.transcription_object.resource().file().file().geturl()
        )
        logging.info("Download of remote resource finished.")
        return open(transcription_file)


def convert_xml_to_tex(xml_file, xslt_script):
    """Convert the list of encoded files to plain text, using the auxilary XSLT script.

    The function creates a output dir in the current working dir and puts the tex file in that
    directory. The function requires saxon installed.

    Keyword Arguments:
    xml_buffer -- the content of the xml file under conversion
    xslt_script -- the content of the xslt script used for the conversion

    Return: File object.
    """
    logging.debug(f"Start conversion of {xml_file}")
    tex_buffer =  subprocess.run(['saxon', f'-s:{xml_file}', f'-xsl:{xslt_script}'],
                                 stdout=subprocess.PIPE).stdout.decode('utf-8')
    # Output dir preparation: Create if not exists, empty if exists.
    if not 'output' in os.listdir('.'):
        os.mkdir('./output/')
    else:
        for (root, dirs, files) in os.walk('output'):
            for name in files:
                os.remove(os.path.join(root, name))

    # Output file name based on transcription object.
    basename, _ = os.path.splitext(os.path.basename(xml_file))
    with open(f'./output/{basename}.tex', 'w') as f:
        f.write(tex_buffer)
    return f

def compile_tex(tex_file):
    """Convert a tex file to pdf with XeLaTeX.

    This requires `latexmk` and `xelatex`.

    Keyword Arguments:
    tex_file -- the tex file object to be converted.

    Return: Output file object.
    """
    logging.info(f"Start compilation of {tex_file.name}")
    process_out = subprocess.run(['latexmk', f'{tex_file.name}', '-xelatex',
                                  '-output-directory=output'], stdout=subprocess.PIPE).stdout
    logging.debug(process_out.decode('utf-8'))
    output_basename, _ = os.path.splitext(tex_file.name)
    return open(output_basename + '.pdf')

def select_xlst_script(trans_obj):
    """Determine which xslt should be used.

    If a URL is provided, the script is downloaded and stored temporarily. If a local file is
    provided, its location is used.

    Keyword Arguments:
    -- trans_obj: Required. The object of the text under processing.
    -- url: The url of an external script.
    -- local: The location of a local script.

    Return: Directory as string.
    """
    schema_info = trans_obj.lbp_schema_info
    if schema_info['type'] == 'critical':
        xslt_document_type = 'critical'
    else:
        xslt_document_type = 'diplomatic'
    xslt_version = schema_info['version']
    top = './xslt'
    if xslt_version in os.listdir(top):
        if xslt_document_type + '.xslt' in os.listdir(os.path.join(top, xslt_version)):
            return os.path.relpath(os.path.join(top, xslt_version, xslt_document_type)) + '.xslt'
        else:
            raise FileNotFoundError(f"The file '{xslt_document_type}.xslt' was not found in '\
                                    {os.path.join(top, xslt_version)}.")
    else:
        raise NotADirectoryError(f"A directory for version {xslt_version} was not found in {top}")

if __name__ == "__main__":

    # Read command line arguments
    args = docopt(__doc__, version="0.0.1")

    # Setup logging
    log_formatter = logging.Formatter()
    # verbosity = args['--verbosity']
    # if not verbosity:
    verbosity = 'DEBUG'
    logging.basicConfig(level=verbosity.upper(), format="%(levelname)s: %(message)s")
    logging.debug(args)

    logging.info('App initialized.')
    logging.info('Logging initialized.')

    # Initialize the object
    if args["--scta"]:
        transcription = RemoteTranscription(args["<expression-id>"])
    elif args["--local"]:
        transcription = LocalTranscription(args["<file>"])
    else:
        raise IOError("Either provide an expression-id or a reference to a local file.")
    if args["pdf"]:
        print(compile_tex(tex_file))


    logging.info('Results returned sucessfully.')
