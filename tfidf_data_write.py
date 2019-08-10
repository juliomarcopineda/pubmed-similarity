import csv
from pathlib import Path

from data.mongo_fields import Publications
from data.mongo_provider import MongoProvider

collection = MongoProvider(Path.home() / '.dsca' / 'app.config').get_publications_collection()


def main():
    docs = collection.find({Publications.TFIDF_VECTOR.mongo: {'$exists': 1}}, {Publications.TFIDF_VECTOR.mongo: 1})
    unique_tokens = set()
    data = {}
    for doc in docs:
        pmid = doc.get(Publications.PMID.mongo)
        tfidf = dict(doc.get(Publications.TFIDF_VECTOR.mongo))
        data[pmid] = tfidf

        for token in tfidf.keys():
            unique_tokens.add(token)
    unique_tokens = list(unique_tokens)

    output_path = Path.home() / 'tfidf_data.csv'
    with open(file=str(output_path), mode='w', encoding='utf8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        headers = ['pmid']
        for token in unique_tokens:
            headers.append(token)
        writer.writerow(headers)

        for pmid, tfidf in data.items():
            record = [pmid]
            for token in unique_tokens:
                weight = tfidf.get(token, 0)
                record.append(weight)
            writer.writerow(record)


if __name__ == '__main__':
    main()