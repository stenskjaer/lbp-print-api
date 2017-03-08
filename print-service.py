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

    def __init__(self, input, input_source):
        self.input = input
        self.input_source = input_source
        # Set parameters depending on source
        if self.input_source == "scta":
            self.scta = True
            self.local = False
            self.scta_resource = lbppy.Resource.find(input)
            self.scta_manifestation_transcriptions = [m.resource().canonical_transcription()
                                        for m in self.scta_resource.manifestations()]
            self.scta_critical_transcription = [
                trans for trans in self.scta_manifestation_transcriptions
                if trans.resource().transcription_type() == 'critical'][0]
        elif self.input_source == "local":
            self.scta = False
            self.local = True
            self.scta_resource = False
            self.scta_manifestation_transcriptions = False
            self.scta_critical_transcription = False
        self.file = self.__define_file__()
        self.lbp_schema_version = self.__get_schema_version__()

    def __get_schema_version__(self):
        """Return the validation schema version."""
        if self.scta:
            return self.scta_critical_transcription.resource().file().validating_schema_version()
        else:
            xml_obj = lxml.etree.parse(self.file)
            schemaRef_number = xml_obj.xpath(
                "/tei:TEI/tei:teiHeader[1]/tei:encodingDesc[1]/tei:schemaRef[1]/@n",
                namespaces={"tei": "http://www.tei-c.org/ns/1.0"}
            )[0]                # The returned result is a list. Grab first element.
            if schemaRef_number:
                return schemaRef_number.split('-')[2]
            else:
                raise BufferError('The document does not contain a value in TEI/teiHeader/encodingDesc/schemaRef[@n]')

    def __define_file__(self):
        """Determine whether the file input supplied is local or remote and return its file object.
        """
        if self.scta:
            logging.debug("Remote resource located. Downloading ...")
            transcription_file, _ = urllib.request.urlretrieve(
                self.scta_critical_transcription.resource().file().file().geturl()
            )
            logging.info("Download of remote resource finished.")

        elif self.local:
            file_argument = self.input
            if os.path.isfile(file_argument):
                transcription_file = file_argument
            else:
                raise IOError( f"The supplied argument ({file_argument}) is not a file." )
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

    if args["--scta"]:
        file_argument = args["<expression-id>"]
        input_source = "scta"
    elif args["--local"]:
        file_argument = args["<file>"]
        input_source = "local"
    else:
        raise IOError("Either provide an expression-id or a reference to a local file.")

    # Initialize the object
    transcription = Transcription(file_argument, input_source)

    # schema_version = get_lbp_version(transcription_xml)
    # xslt_script = select_xslt_script(schema_version)
    # tex_buffer = convert_xml_to_tex(transcription_xml, "./critical.xslt")

    logging.info('Results returned sucessfully.')
