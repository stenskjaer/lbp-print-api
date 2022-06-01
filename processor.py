import logging
import os
import urllib

import hashlib

from redis import Redis
from rq import get_current_job, Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError

import lbp_print.core as lbp_print
import lbp_print.config as lbp_config
from lbp_print.exceptions import SaxonError

from docopt import docopt
import subprocess
import logging
import lbppy
import urllib
import os
import lxml
import re

import json

from SPARQLWrapper import SPARQLWrapper, JSON

MODULE_DIR = os.path.dirname(__file__)

logger = logging.getLogger()
lbp_config.cache_dir = "cache"
redis_endpoint = os.getenv("REDIS_ENDPOINT", "localhost")
logger.warning(f"Logging redis endpoint: {redis_endpoint}")
redis_connection = Redis(host=redis_endpoint)
q = Queue(connection=redis_connection)


def check_if_file_exists(url):
    if resource_type == "scta":
        trans = lbp_print.RemoteResource(id)
    elif resource_type == "url":
        trans = lbp_print.UrlResource(id)




def handle_job(resource_value: str, resource_type: str) -> dict:
    try:
        logger.debug(f"Checking for job with the id {resource_value}")
        job = Job.fetch(resource_value, connection=redis_connection)
    except NoSuchJobError:
        logger.debug(f"No existing job. Starting one up ...")
        job = q.enqueue(
            convert_resource,
            resource_value,
            resource_type,
            job_id=resource_value,
            job_timeout="1h",
            result_ttl=30,
        )
        return {"Status": f"Started processing {resource_value}"}

    status = job.meta["progress"]

    if job.result:
        response = {"Status": "Finished", "url": job.result}
        logger.debug(f"Job was finished. Result: " + job.result)
    elif job.is_failed:
        response = {"Status": "Failed. Resubmit to retry.", "error": status}
        logger.warn(f"Job failed." + status)
        job.delete()
    else:
        response = {"Status": status}
        logger.debug(f"Job running. Status: " + status)
    return response


def update_status(message, job):
    job.meta["progress"] = message
    job.save_meta()
    logger.info(message)


def convert_resource(id: str, resource_type: str) -> str:
    job = get_current_job()
    update_status(f"Start processing {id}.", job)

    if resource_type == "scta":
        trans = lbp_print.RemoteResource(id)
    elif resource_type == "annolist":
        trans = id
    elif resource_type == "url":
        trans = lbp_print.UrlResource(id)
    else:
        raise ValueError(f"Trying to convert {id} of illegal type {resource_type}")
    update_status(f"Identified and downloaded {id}.", job)

    update_status(f"Converting {id} to pdf.", job)
    try:
        if resource_type == "annolist":
            filename = compile_tex(clean_tex(convert_anno_list(trans)))
            #filename = compile_tex(convert_anno_list(trans))
            #filename = clean_tex(convert_anno_list(trans))
            #filename = convert_anno_list(trans)
        else:
            filename = lbp_print.Tex(trans).process(output_format="pdf")
    except SaxonError as exc:
        update_status(str(exc), job)
        raise
    update_status(f"Successfully converted {id} to pdf.", job)

    return filename

def convert_anno_list(annolist):
    # Output file name based on transcription object.
    if "http" in annolist:
        filehash = getHash(annolist)
    else:
        filehash = annolist.split(".json")[0]
    
    output="cache"    

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

    if "http" in annolist:
        localannotations = os.path.join(output_dir, filehash + ".json")
        urllib.request.urlretrieve(annolist, localannotations)
    else:
        localannotations = annolist
    
    ## save sourcetitlemap needed for index
    getSourceTitleMap(localannotations)
    logging.debug(f"test1 {localannotations}")
    xml_file = "/usr/src/app/annotations.xslt"
    xsl_file = "/usr/src/app/annotations.xslt"
    #logging.debug(f"Start conversion of {xml_file}")
    tex_buffer = subprocess.run(['java', '-jar', os.path.join('/usr/share/java/saxon/saxon-he-10.8.jar'), f'-s:{xml_file}', f'-xsl:{xsl_file}', f"annolist={localannotations}"],
                                stdout=subprocess.PIPE).stdout.decode('utf-8')

   

    if "http" in annolist:
        texoutput = os.path.join(output_dir, filehash + '.tex')
    else: 
        texoutput = filehash + '.tex'
    
    with open(texoutput, mode='w', encoding='utf-8') as f:
        f.write(tex_buffer)
    
    return f

def clean_tex(tex_file):
    """Clean the content of the tex file for different whitespace problems.
    Side effect: This changes the content of the file.
    :param tex_file: File object of the tex file.
    :return: File object of the tex file after cleanup.
    """
    logging.info("Trying to remove whitespace...")
    patterns = [
        (r' ?{ ?', r'{'),                 # Remove redundant space around opening bracket.
        (r' }', r'}'),                    # Remove redundant space before closing bracket.
        (r' ([.,?!:;])', r'\1'),          # Remove redundant space before punctuation.
        (r' (\\edtext{})', r'\1'),        # Remove space before empty lemma app notes.
        (r'}(\\edtext{[^}]})', r'} \1'),  # Add missing space between adjacent app. notes.
        # (r'\s+', ' ')
    ]

    buffer = open(tex_file.name).read()
    for pattern, replacement in patterns:
        buffer = re.sub(pattern, replacement, buffer)

    with open(tex_file.name, 'w') as f:
        f.write(buffer)
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
                                  '-output-directory=cache'], stdout=subprocess.PIPE).stdout
    logging.debug(process_out.decode('utf-8'))
    output_basename, _ = os.path.splitext(tex_file.name)
    return output_basename + '.pdf'
    #return open(output_basename + '.pdf')


def getHash(filepath):
    filepathhash_sha1 = hashlib.sha256(filepath.encode('utf-8')).hexdigest()
    return filepathhash_sha1

def getSourceTitleMap(annolist):
    eids = getExpressionIdsFromAnnoList(annolist)
    valuesString = " ".join(eids)
    query = """
    SELECT ?source ?long_title ?authorTitle ?topLevelExpressionTitle ?itemLevelExpressionTitle ?cquote 
    WHERE {
    VALUES ?resources { %s }
	?e <http://scta.info/property/isMemberOf> ?resources .
	{
	    ?e <http://scta.info/property/source> ?source .
	}
    UNION
	{
	    ?e <http://scta.info/property/source> ?bn .
    	?bn <http://scta.info/property/source> ?source .
    }
		OPTIONAL{
  	?source <http://scta.info/property/longTitle> ?long_title .
		}
		?source <http://scta.info/property/isMemberOf> ?topLevelExpression .
		?topLevelExpression <http://scta.info/property/level> '1' .
		?topLevelExpression <http://purl.org/dc/elements/1.1/title> ?topLevelExpressionTitle .
		OPTIONAL{
		?topLevelExpression <http://www.loc.gov/loc.terms/relators/AUT> ?author .
		?author <http://purl.org/dc/elements/1.1/title> ?authorTitle .
		}
		OPTIONAL{
			{
			?source <http://scta.info/property/isMemberOf> ?itemLevelExpression .
			?itemLevelExpression <http://scta.info/property/structureType> <http://scta.info/resource/structureItem> .
			?itemLevelExpression <http://purl.org/dc/elements/1.1/title> ?itemLevelExpressionTitle .
			}
			UNION
			{
			?source <http://scta.info/property/structureType> <http://scta.info/resource/structureItem> .
			?source <http://purl.org/dc/elements/1.1/title> ?itemLevelExpressionTitle .
			}
		}
    }"""%(valuesString)

    sparql = SPARQLWrapper("https://sparql-docker.scta.info/ds/query")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    titleMap = {}
    for r in results["results"]["bindings"]:
        source = r["cquote"]["value"] if "cquote" in r else r["source"]["value"]
        lt = r["long_title"]["value"] if "long_title" in r else "x"
        et = r["topLevelExpressionTitle"]["value"]
        at = r["authorTitle"]["value"] if "authorTitle" in r else "x"
        it = r["itemLevelExpressionTitle"]["value"] if "itemLevelExpressionTitle" in r else "x"
        #ite = lt.split(",").count > 1 ? lt.split(",").drop(1).join(", ").split(it)[0] + it : it
        lt_split = lt.split(", ")
        ite = "" 

        if "Biblia" in lt:
            ite = it
        elif len(lt_split) > 2:
            #puts lt.split(", ").drop(1).join(", ")
            #puts it
            #ite = ", ".join(lt.split(", ").pop(1)).split(it)[0] if ", ".join(lt.split(", ").pop(1)).split(it)[0] + it else it
            ite = lt_split.pop(1).split(it)[0] if lt_split.pop(1).split(it)[0] + it else it
        elif len(lt_split) > 1:
            ite = lt_split.pop(1)
        else:
            ite = lt

        cquote =  r["cquote"]["value"] if "cquote" in r else "x"
        titleMap[source] = {"lt": lt, "et": et, "at": at, "it": it, "ite": ite }

    mapElements = ""
    for c, i in titleMap.items():
        xml = "  <pair>\n    <source>" + c + "</source>\n    <longTitle>" + i["lt"] + "</longTitle>\n       <topLevelExpressionTitle>" + i["et"] + "</topLevelExpressionTitle>\n      <authorTitle>" + i["at"] + "</authorTitle>\n      <itemLevelExpressionTitle>" + i["ite"] + "</itemLevelExpressionTitle>\n      <itemLevelExpressionTitleOld>" + i["it"] + "</itemLevelExpressionTitleOld>\n  </pair>\n"
        mapElements = mapElements + xml
    
    output = "<?xml version='1.0' encoding='UTF-8'?>\n<pairs xmlns='http://scta.info/ns/source-title-map'>\n" + mapElements + "</pairs>"

    with open("./cache/sourceTitleMap.xml", 'w') as f:
        f.write(output)
        return f

def getExpressionIdsFromAnnoList(annolist): 
    ids = []
    with open(annolist, 'r') as annolistfile:
        anno_data = json.load(annolistfile)
        for a in anno_data: 
            ids.append("<http://scta.info/resource/" + a["target"]["source"].split("/")[-3] + ">")
    
    return ids