import requests
import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
import time


esearch = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
efetch = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'


def get_pmids():
    print('Retrieving PMIDs...')
    data = {
        'db': 'pubmed',
        'term': 'cancer',
        'field': 'majr',
        'mindate': '2018/01',
        'maxdate': '2018/12',
        'datetype': 'pdat',
        'retmax': 100000
    }
    request = requests.post(esearch, data)
    xml = request.text
    root = ET.fromstring(xml)
    pmids = [id_node.text for id_node in root.findall('IdList/Id')]

    print('Number of PMIDs: ' + str(len(pmids)))

    return pmids


def get_pub_xml(pmids):
    print('Fetching citation XML data...')
    data = {
        'db': 'pubmed',
        'id': ','.join(pmids),
        'retmode': 'xml'
    }
    request = requests.post(efetch, data)
    return request.text


def get_citation_data(citation):
    citation_data = {}

    pmid_node = citation.find('PMID')
    year_node = citation.find('DateCompleted/Year')
    journal_node = citation.find('Article/Journal/Title')
    title_node = citation.find('Article/ArticleTitle')
    abstract_text_node = citation.find('Article/Abstract/AbstractText')

    names = []
    for author in citation.findall('Article/AuthorList/Author'):
        last_name_node = author.find('LastName')
        fore_name_node = author.find('ForeName')

        last_name = ''
        fore_name = ''

        if last_name_node is not None:
            last_name = last_name_node.text
        if fore_name_node is not None:
            fore_name = fore_name_node.text

        if last_name and fore_name:
            name = last_name + ", " + fore_name
            names.append(name)

    if pmid_node is not None:
        pmid_text = pmid_node.text
        if pmid_text:
            citation_data['pmid'] = int(pmid_text)
    if year_node is not None:
        year_text = year_node.text
        if year_text:
            citation_data['year'] = int(year_text)
    if journal_node is not None:
        journal = journal_node.text
        if journal:
            citation_data['journal'] = journal
    if title_node is not None:
        title = title_node.text
        if title:
            citation_data['title'] = title
    if abstract_text_node is not None:
        abstract = abstract_text_node.text
        if abstract:
            citation_data['abstract'] = abstract
    if names:
        authors = ';'.join(names)
        citation_data['authors'] = authors

    return citation_data


def main():
    pmids = get_pmids()

    print('Parsing XML data...')
    batch_size = 1000
    batches = [pmids[i: i + batch_size] for i in range(0, len(pmids), batch_size)]

    count = 0
    data = []
    for batch in batches:
        xml_data = get_pub_xml(batch)
        root = ET.fromstring(xml_data)

        for citation in root.findall('PubmedArticle/MedlineCitation'):
            count += 1
            if count % 5000 == 0:
                print('STATUS: ' + str(count))

            citation_data = get_citation_data(citation)
            data.append(citation_data)

        time.sleep(5)

    print('STATUS: ' + str(count))

    df = pd.DataFrame(data)
    output_path = Path.home() / '2018_cancer.csv'

    print('Writing data to ' + str(output_path) + '...')
    df.to_csv(output_path, index=False)

    print('Done.')


if __name__ == '__main__':
    main()
