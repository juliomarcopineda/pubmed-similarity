import csv
from pathlib import Path

from data.mongo_fields import Publications
from data.mongo_provider import MongoProvider

collection = MongoProvider(Path.home() / '.dsca' / 'app.config').get_publications_collection()


def main():
    threshold = 0
    query = {Publications.NEIGHBORS.mongo: {'$exists': 1}}
    docs = collection.find(query)

    similarity_data = {}
    administrative_data = {}
    for doc in docs:
        pmid = doc.get(Publications.PMID.mongo)
        journal = doc.get(Publications.JOURNAL.mongo)
        year = doc.get(Publications.PUBLICATION_YEAR.mongo)
        neighbors = doc.get(Publications.NEIGHBORS.mongo)
        scores = doc.get(Publications.SCORES.mongo)

        admin = {Publications.JOURNAL.mongo: journal, Publications.PUBLICATION_YEAR.mongo: year}
        administrative_data[pmid] = admin

        if neighbors:
            for i in range(len(neighbors)):
                neighbor = neighbors[i]
                neighbor_doc = collection.find_one({Publications.PMID.mongo: neighbor},
                                                   {Publications.PUBLICATION_YEAR.mongo: 1})
                year = int(neighbor_doc.get(Publications.PUBLICATION_YEAR.mongo))
                score = scores[i]
                if score > threshold:
                    similarity = similarity_data.get(pmid, {})
                    similarity[neighbor] = score
                    similarity_data[pmid] = similarity

    # Node CSV
    node_path = Path.home() / 'nodes.csv'
    with open(file=str(node_path), encoding='utf8', newline='', mode='w') as node_csv:
        writer = csv.writer(node_csv, delimiter=',')
        headers = ['pmid', 'journal', 'year']
        writer.writerow(headers)

        for pmid, data in administrative_data.items():
            record = [pmid, data.get(Publications.JOURNAL.mongo, ''),
                      data.get(Publications.PUBLICATION_YEAR.mongo, '')]
            writer.writerow(record)

    # Edges CSV
    edges_path = Path.home() / 'edges.csv'
    with open(file=str(edges_path), encoding='utf8', newline='', mode='w') as edges_csv:
        writer = csv.writer(edges_csv, delimiter=',')
        headers = ['source', 'target', 'weight']
        writer.writerow(headers)

        for pmid_source, similarity in similarity_data.items():
            for pmid_target, weight in similarity.items():
                if pmid_target in administrative_data:
                    record = [str(pmid_source), str(pmid_target), str(weight)]
                    writer.writerow(record)


if __name__ == '__main__':
    main()
