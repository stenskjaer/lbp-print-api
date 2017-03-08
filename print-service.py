#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""LBP print as a service.

Usage:
  lbp-print-service.py tex --local <file>
  lbp-print-service.py tex --scta <expression-id>

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
            raise BufferError('The document does not contain a value in TEI/teiHeader/encodingDesc/schemaRef[@n]')

    def __define_file(self):
        """Return the file object.
        """
        file_argument = self.input
        if os.path.isfile(file_argument):
            return open(file_argument)
        else:
            raise IOError( f"The supplied argument ({file_argument}) is not a file." )


class RemoteTranscription(Transcription):
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
    """Convert the list of encoded files to plain text, using the auxilary XSLT script. This requires
    saxon installed.

    Keyword Arguments:
    xml_buffer -- the content of the xml file under conversion
    xslt_script -- the content of the xslt script used for the conversion

    Return: Latex buffer.
    """
    logging.debug(f"Start conversion of {xml_file}")
    return subprocess.run(['saxon', f'-s:{xml_file}', f'-xsl:{xslt_script}'],
                          stdout=subprocess.PIPE).stdout

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

    # schema_version = get_lbp_version(transcription_xml)
    # xslt_script = select_xslt_script(schema_version)
    # tex_buffer = convert_xml_to_tex(transcription_xml, "./critical.xslt")

    logging.info('Results returned sucessfully.')
