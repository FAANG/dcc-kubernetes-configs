import json
import requests
import csv
from datetime import datetime

endpoint = 'https://www.ebi.ac.uk/biosamples/samples'
records = []
p = 0
while True:
    response = requests.get(endpoint, params=[
        ('size', 10000), ('page', p), ('filter', 'attr:project:FAANG')])
    response_data = response.content
    json_data = json.loads(response_data)

    if (response.status_code == 200 and '_embedded' in json_data.keys()):
        records += json_data['_embedded']['samples']
        p += 1
    else:
        break

if (response.status_code == 200 and '_embedded' in json_data.keys()):
    records += json_data['_embedded']['samples']


protocol_types = [
    'specimen collection protocol', 
    'pool creation protocol', 
    'purification protocol',
    'cell culture protocol',
    'culture protocol'
]

def getProtocolLinksToUpdate(record):
    old_protocols = []
    new_protocols = []
    if 'characteristics' in record.keys():
        rec_char = record['characteristics']
        for prot_type in protocol_types:
            if prot_type in rec_char.keys():
                for prot in rec_char[prot_type]:
                    protocol_link = prot['text']
                    if 'ftp.faang.ebi' in protocol_link:
                        old_protocols.append({prot_type: protocol_link})
                        filename = protocol_link.split('/')[-1]
                        new_link = 'https://data.faang.org/api/fire_api/samples/' + filename
                        new_protocols.append({prot_type: new_link})
    return {'old_protocols': old_protocols, 'new_protocols': new_protocols}

data = []
for record in records:
    links_to_update = getProtocolLinksToUpdate(record)
    old_protocols = links_to_update['old_protocols']
    new_protocols = links_to_update['new_protocols']
    if len(old_protocols):
        rec = {}
        rec['accession'] = record['accession']
        rec['old_protocol_links'] = old_protocols
        rec['new_protocol_link'] = new_protocols
        data.append(rec)

keys = data[0].keys()
timestamp = datetime.now().strftime("%Y_%m_%d")
filename = "records_" + timestamp + ".csv"
with open(filename, 'w', newline='')  as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(data)

print(str(len(data)) + ' records found')
