"""

Example script for interacting with scidb.

"""""

import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

username = ''  # we will give you this on the hackathon day
password = ''  # we will give you this on the hackathon day
url = 'https://ugm.scibite.com/api/tie/v1/'


def get_all_datasets(from_type=None, to_type=None):
    """
    Return a list of all the data sets captured in SciDB, and optionally limit.
    No parameter call returns all available data sets

    :param from_type: type of entity link from e.g. 'DRUG'
    :param to_type: type of entity link to e.g. 'GENE'
    :return:
    """

    request_url = '{}/retrieve/datasets'.format(url)
    datasets = json.loads(requests.get(request_url, verify=False, auth=(username, password)).text)['hits']

    pruned_datasets = []

    if from_type or to_type:
        for dataset in datasets:
            try:
                entTypes = [dataset['toType'], dataset['fromType']]
            except KeyError:
                continue
            keep = True
            if from_type:
                if not from_type == entTypes[1]:
                    keep = False
            if to_type:
                if not to_type == entTypes[0]:
                    keep = False
            if keep:
                pruned_datasets.append(dataset)
        return pruned_datasets

    return datasets


def get_linked_entities(entity_type, entity_id, to_type=None, dataset_name=None):
    """
    Optionally specify the type of link you are interested in (i.e. the entity
    type that you want to link to). DRUG, GENE, INDICATION, etc.

    :param entity_type: string entity type e.g. 'DRUG'
    :param entity_id: string entity ID e.g. 'CHEMBL192'
    :param to_type: set of Strings of entity to link to e.g. ['INDICATION', 'DRUG']
    :param dataset_name: name of the dataset that you wish to limit your associations too e.g. 'Drug drug interactions extracted from drug labels'
    :return:
    """

    datasets = get_all_datasets()

    all_links = []
    for dataset in datasets:
        if dataset_name and dataset['datasetName'] == dataset_name or dataset_name is None:
            try:
                entTypes = [dataset['toType'], dataset['fromType']]
            except KeyError:
                continue

            if entity_type == entTypes[0]:
                rel = 'to'
            elif entity_type == entTypes[1]:
                rel = 'from'
            else:
                continue

            if to_type:
                if to_type not in entTypes:
                    continue

            if to_type:
                rel2 = 'toType' if rel == 'from' else 'fromType'

            payload = {'dataset': dataset['datasetName'],
                       'q': '{0}:{1}${2}{3}'.format(rel, entity_type, entity_id,
                                                    ' and %s:%s' % (rel2, to_type) if to_type else '')}

            request_url = '{}/search/concept'.format(url)
            results = json.loads(requests.get(request_url,
                                              params=payload,
                                              verify=False,
                                              auth=(username, password)).text)
            for link in results['hits']:
                links = {'from': link['from'], 'fromName': link['fromName'], 'to': link['to'], 'toName': link['toName'],
                         'dataset': dataset['datasetName']}
                all_links.append(links)

    return all_links


print(get_all_datasets(from_type='DRUG'))
print(get_linked_entities('DRUG', 'CHEMBL192', dataset_name='Drug drug interactions extracted from drug labels'))
