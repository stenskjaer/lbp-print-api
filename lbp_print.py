#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""LBP print as a service.

Usage:
  lbp_print.py (tex|pdf) [options] --local <file>
  lbp_print.py (tex|pdf) [options] --scta <expression-id>

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
  --xslt <file>           Use a custom xslt file in place of the default supplied templates.
  --output, -o <dir>      Put results in the specified directory.
  -V, --verbosity <level> Set verbosity. Possibilities: silent, info, debug [default: debug].
  -v, --version           Show version and exit.
  -h, --help              Show this help message and exit.
"""

from docopt import docopt
import subprocess
import logging
import lbppy
import urllib
import os
import lxml


class Transcription:
    """The main object of the script, defining the properties of the text under processing."""

    def __init__(self, input_argument):
        self.input = input_argument

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
        schemaref_number = lxml.etree.parse(self.file).xpath(
            "/tei:TEI/tei:teiHeader[1]/tei:encodingDesc[1]/tei:schemaRef[1]/@n",
            namespaces={"tei": "http://www.tei-c.org/ns/1.0"}
        )[0]                # The returned result is a list. Grab first element.
        if schemaref_number:
            return {
                'version': schemaref_number.split('-')[2],
                'type': schemaref_number.split('-')[1]
            }
        else:
            raise BufferError('The document does not contain a value in '
                              'TEI/teiHeader/encodingDesc/schemaRef[@n]')

    def __define_file(self):
        """Return the file object.
        """
        file_argument = self.input
        if os.path.isfile(file_argument):
            return open(file_argument)
        else:
            raise IOError(f"The supplied argument ({file_argument}) is not a file.")


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


def convert_xml_to_tex(xml_file, xslt_script, output=False):
    """Convert the list of encoded files to tex, using the auxiliary XSLT script.

    The function creates a output dir in the current working dir and puts the tex file in that
    directory. The function requires saxon installed.

    Keyword Arguments:
    xml_buffer -- the content of the xml file under conversion
    xslt_script -- the content of the xslt script used for the conversion

    Return: File object.
    """
    logging.debug(f"Start conversion of {xml_file}")
    tex_buffer = subprocess.run(['java', '-jar', './vendor/saxon9he.jar', f'-s:{xml_file}', f'-xsl:{xslt_script}'],
                                stdout=subprocess.PIPE).stdout.decode('utf-8')
    # Output dir preparation: If output flags, check that dir and set, if not,
    # create or empty the dir "output" in current working dir.
    if output:
        if os.path.isdir(output):
            output_dir = output
        else:
            raise ValueError(f"The supplied output dir, {output}, is not a directory.")
    else:
        output_dir = 'output'
        if not output_dir in os.listdir('.'):
            os.mkdir(output_dir)
        else:
            for (root, dirs, files) in os.walk(output_dir):
                for name in files:
                    os.remove(os.path.join(root, name))

    # Output file name based on transcription object.
    basename, _ = os.path.splitext(os.path.basename(xml_file))
    with open(os.path.join(output_dir, basename + '.tex'), 'w') as f:
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
    verbosity = args['--verbosity']
    if not verbosity:
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
        raise ValueError("Either provide an expression-id or a reference to a local file.")

    # Determine xslt script file (either provided or selected based on the xml transcription)
    if args["--xslt"]:
        xslt_candidate = args["--xslt"]
        if os.path.isfile(xslt_candidate):
            xslt_script = xslt_candidate
        else:
            raise FileNotFoundError(f"The xslt file supplied, {xslt_candidate}, was not found.")
    else:
        xslt_script = select_xlst_script(transcription)

    # Determine output directory
    if args["--output"]:
        output_dir = args["--output"]
    else:
        output_dir = False

    tex_file = convert_xml_to_tex(transcription.file.name, xslt_script, output_dir)

    if args["pdf"]:
        pdf_file = compile_tex(tex_file)


    logging.info('Results returned sucessfully.')
