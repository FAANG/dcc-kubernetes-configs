import json
import requests
import pandas as pd
import os, subprocess, hashlib

FIRE_USERNAME = os.getenv('FIRE_USERNAME')
FIRE_PASSWORD = os.getenv('FIRE_PASSWORD')
FIRE_API = 'https://hx.fire.sdo.ebi.ac.uk/fire/objects'
FIRE_PATH = 'ftp/ontologies'
FILE = 'faang_ontologies.tsv'

def file_as_bytes(file):
        """This function returns file as bits"""
        with file:
            return file.read()

def get_md5_of_file(file):
    """
    This function will return md5 hash of a file
    :return: md5 hash value
    """
    return hashlib.md5(file_as_bytes(
        open(file, 'rb'))).hexdigest()

def get_file_size(file):
    """
    This function return file size in bytes
    :return: file size in bytes
    """
    return os.path.getsize(file)

def delete_objects(fire_id):
    """This function will delete object from Fire database"""
    cmd = f"curl {FIRE_API}/{fire_id} " \
        f"-u {FIRE_USERNAME}:{FIRE_PASSWORD} " \
        f"-X DELETE"
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

def get_semantic_tag(id):
    OBO = [ 'LBO', 'BTO', 'UBERON', 'OBI', 'PATO', 'NCBITaxon', \
            'CL', 'CLO', 'FMA', 'MONDO', 'EOL', 'CHEBI', 'CHMO', \
            'EO', 'GO', 'HANCESTRO', 'HP', 'NCIT', 'OMIT', 'PO', 'UO']
    INRA = ['ATOL', 'EOL']
    EBI = ['EFO', 'CMPO']
    ontology_id = id.split('_')[0]
    if ontology_id in OBO:
        return 'http://purl.obolibrary.org/obo/' + id
    if ontology_id in INRA:
        return 'http://opendata.inra.fr/' + ontology_id + '/' + id
    elif ontology_id in EBI:
        return 'http://www.ebi.ac.uk/' + ontology_id.lower() + '/' + id
    elif ontology_id == 'MEO':
        return 'http://purl.jp/bio/11/meo/' + id
    elif ontology_id == 'Orphanet':
        return 'http://www.orpha.net/ORDO/' + id
    elif ontology_id == 'topic':
        return 'http://edamontology.org/' + id
    else:
        return id

def main():
    # collect ontology mappings
    url = 'http://daphne-svc:8000/ontology_improver/search/'
    response = requests.get(url)
    ontologies = json.loads(response.content)['ontologies']
    zooma_mappings = []
    for ontology in ontologies:
        # TODO: check if ontology status is verified
        if ontology['ontology_type'] and ontology['ontology_term'] and ontology['ontology_id']:
            mapping = {
                'STUDY': '',
                'BIOENTITY': '',
                'PROPERTY_TYPE': ontology['ontology_type'],
                'PROPERTY_VALUE': ontology['ontology_term'],
                'SEMANTIC_TAG': get_semantic_tag(ontology['ontology_id'])
            }
            zooma_mappings.append(mapping)

    # write data to file
    df = pd.DataFrame(zooma_mappings)
    df = df.drop_duplicates()
    df.to_csv(FILE, sep="\t", index=False)

    # list files and delete ontology file if it already exists
    cmd = f"curl {FIRE_API}?total=1000000 -u {FIRE_USERNAME}:{FIRE_PASSWORD}"
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    out = json.loads(out.decode('utf-8'))
    for file in out:
        if file['filesystemEntry']:
            if file['filesystemEntry']['path'] == f"/{FIRE_PATH}/{FILE}":
                delete_objects(file['fireOid'])
                break

    # upload file to FIRE service
    cmd =   f"curl {FIRE_API} -F file=@{FILE} " \
            f"-u {FIRE_USERNAME}:{FIRE_PASSWORD} " \
            f"-H 'x-fire-size: {get_file_size(FILE)}' " \
            f"-H 'x-fire-md5: {get_md5_of_file(FILE)}'"
    upload_process = subprocess.run(cmd, shell=True, capture_output=True)

    # set file path in FIRE service
    fire_id = json.loads(upload_process.stdout.decode('utf-8'))['fireOid']
    cmd =   f"curl {FIRE_API}/{fire_id}/firePath " \
            f"-u {FIRE_USERNAME}:{FIRE_PASSWORD} " \
            f"-H 'x-fire-path: {FIRE_PATH}/{FILE}' -X PUT"
    subprocess.run(cmd, shell=True, capture_output=True)

    # publish file
    cmd = f"curl {FIRE_API}/{fire_id}/publish " \
            f"-u {FIRE_USERNAME}:{FIRE_PASSWORD} -X PUT"
    subprocess.run(cmd, shell=True, capture_output=True)

if __name__ == "__main__":
    main()
