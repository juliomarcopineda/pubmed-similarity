"""Retrieve publication data from PubMed using eUtils API. This script limits the data
for publications published between 2018/01 and 2018/12 with MeSH major topic: 'cancer'.
The result is stored to disk as a CSV file.
"""

import csv
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

# URLs for API calls to retrieve PubMed publication information
esearch = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'
efetch = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'


def get_pmids(query):
    """Obtain PMIDs from PubMed given the following query for the API

    :param query: dict of parameters
    :return: list of PMIDs
    """

    print('Retrieving PMIDs...')
    request = requests.post(esearch, query)
    xml = request.text
    root = ET.fromstring(xml)
    pmids = [id_node.text for id_node in root.findall('IdList/Id')]

    print('Number of PMIDs: ' + str(len(pmids)))

    return pmids


def get_pub_xml(pmids):
    """Obtain XML data associated to the provided PMIDs

    :param pmids: list of PMIDs
    :return: str XML representation of publication data
    """

    print('Fetching citation XML data...')
    data = {
        'db': 'pubmed',
        'id': ','.join(pmids),
        'retmode': 'xml'
    }
    request = requests.post(efetch, data)
    return request.text


def get_citation_data(citation):
    """Given the citation node from the XML, obtain the data associated to the citation

    :param citation: XML node with citation data
    :return: dict of citation data
    """
    citation_data = {}

    pmid_node = citation.find('PMID')
    year_node = citation.find('Article/Journal/JournalIssue/PubDate/Year')
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
            citation_data['pmid'] = pmid_text
    if year_node is not None:
        year_text = year_node.text
        if year_text:
            citation_data['year'] = year_text
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
    journals = ['Cell', 'Nature Medicine', 'Science']
    for journal in journals:
        print('Querying for', journal)
        term_query = 'cancer[majr] AND ' + journal + '[ta]'

        # Setup query to get PubMed IDs
        pmid_query = {
            'db': 'pubmed',
            'term': term_query,
            # 'mindate': '2018/01/01',
            # 'maxdate': '2019/08/09',
            # 'datetype': 'pdat',
            'retmax': 100000
        }
        pmids = get_pmids(pmid_query)

        print('Parsing XML data...')

        # Batch XML requests
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
                    print('STATUS:', count)

                citation_data = get_citation_data(citation)
                data.append(citation_data)

            # Slow down API requests to not exceed limit
            time.sleep(5)

        print('STATUS:', count)

        print('Remove data elements with no abstract')
        data = [citation_data for citation_data in data if citation_data.get('abstract', '')]

        # Convert citation data to DataFrame for easy CSV conversion
        filename = journal + '_cancer_2018_present.csv'
        output_path = Path.home() / filename

        print('Writing data to ' + str(output_path) + '...')
        with open(file=output_path, mode='w', newline='', encoding='utf8') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            headers = ['pmid', 'year', 'journal', 'title', 'abstract']
            writer.writerow(headers)

            for citation_data in data:
                record = [citation_data.get('pmid', ''), citation_data.get('year', ''),
                          citation_data.get('journal', ''), citation_data.get('title', ''),
                          citation_data.get('abstract', '')]
                writer.writerow(record)

    print('Done.')


if __name__ == '__main__':
    main()
