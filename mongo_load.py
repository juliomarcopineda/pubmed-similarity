"""Loads publication data from a CSV file to a MongoDB instance with the collection name: 'publications'.
"""

import csv
from pathlib import Path

from data.mongo_fields import Publications
from data.mongo_provider import MongoProvider

collection = MongoProvider(Path.home() / '.dsca' / 'app.config').get_publications_collection()


def construct_mongo_doc(row):
    """Given a row or record from the publication data, construct a dictionary to be inserted to
    the publications collection

    :param row: row/record of publication data
    :return: dict document of publication data
    """

    doc = {}

    pmid = row['pmid']
    if pmid is not None:
        doc[Publications.PMID.mongo] = int(pmid)

    year = row['year']
    if year is not None and year:
        doc[Publications.PUBLICATION_YEAR.mongo] = int(year)

    journal = row['journal']
    if journal is not None and journal != '':
        doc[Publications.JOURNAL.mongo] = journal

    title = row['title']
    if title is not None and title != '':
        doc[Publications.TITLE.mongo] = title

    authors_string = row['authors']
    if authors_string is not None and authors_string != '':
        doc[Publications.AUTHORS.mongo] = authors_string.split(';')

    abstract = row['abstract']
    if abstract is not None and abstract != '':
        doc[Publications.ABSTRACT.mongo] = abstract

    return doc


def main():
    print('Inserting PubMed records to MongoDB...')
    print('Dropping publications collection...')
    collection.drop()

    journals = ['Cell', 'Nature Medicine', 'Science']
    for journal in journals:
        print('Reading', journal)
        status = 0
        filename = journal + '_cancer_2018_present.csv'
        data_path = Path.home() / filename
        with open(data_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                status += 1
                if status % 100 == 0:
                    print('STATUS:', status)

                doc = construct_mongo_doc(row)
                year = doc.get(Publications.PUBLICATION_YEAR.mongo)
                if year is not None and year >= 2010:
                    collection.insert_one(doc)

        print('STATUS:', status)
    print('Done.')


if __name__ == '__main__':
    main()
