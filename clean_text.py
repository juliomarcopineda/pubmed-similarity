import sys
import pickle
from concurrent.futures.process import ProcessPoolExecutor
from pathlib import Path
from joblib import Parallel, delayed

from data.mongo_fields import Publications
from data.mongo_provider import MongoProvider
from text_processing import text_cleaner

collection = MongoProvider(Path.home() / '.dsca' / 'app.config').get_publications_collection()


def get_text(doc):
    title = doc.get(Publications.TITLE.mongo, '')
    abstract = doc.get(Publications.ABSTRACT.mongo, '')

    if title or abstract:
        return doc.get(Publications.TITLE.mongo, '') + ' ' + doc.get(Publications.ABSTRACT.mongo, '')
    else:
        return ''


def pipeline(text):
    cleaned_text = text_cleaner.clean_text(text)
    return cleaned_text


def main():
    docs = collection.find({Publications.CLEAN_TEXT.mongo: {'$exists': 0}},
                           {Publications.ABSTRACT.mongo: 1, Publications.TITLE.mongo: 1})
    size = collection.estimated_document_count({Publications.CLEAN_TEXT.mongo: {'$exists': 0}})
    print('Number of docs:', size)
    status = 0
    for doc in docs:
        status += 1
        if status % 10 == 0:
            print('STATUS:', status)

        text = get_text(doc)
        clean_text = text_cleaner.clean_text(text)

        if clean_text:
            filter_doc = {
                Publications.PMID.mongo: doc.get(Publications.PMID.mongo)
            }
            update_doc = {
                '$set': {
                    Publications.CLEAN_TEXT.mongo: clean_text
                }
            }

            collection.update_one(filter=filter_doc, update=update_doc)
    print('STATUS:', status)
    print('Done.')


if __name__ == '__main__':
    main()
