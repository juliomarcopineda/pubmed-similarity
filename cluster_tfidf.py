import csv
import math
import sys
from collections import OrderedDict, Counter
from pathlib import Path

from data.mongo_fields import Publications
from data.mongo_provider import MongoProvider
from text_processing.text_cleaner import tokenize_text

collection = MongoProvider(Path.home() / '.dsca' / 'app.config').get_publications_collection()


def main():
    print('Reading Cluster Data...')
    clusters_path = Path.home() / 'clusters.csv'
    clusters = {}
    with open(file=str(clusters_path), mode='r', encoding='utf8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cluster_id = row['ClusterID']
            pmid = row['PMID']

            pmids = clusters.get(cluster_id, [])
            pmids.append(pmid)
            clusters[cluster_id] = pmids

    print('Generating TF-IDF for each cluster...')
    doc_term_freq = {}
    doc_freq = {}
    doc_size = len(clusters)
    for cluster_id, pmids in clusters.items():
        text = ''
        for pmid in pmids:
            doc = collection.find_one({Publications.PMID.mongo: int(pmid)},
                                      {Publications.CLEAN_TEXT.mongo: 1})
            text = text + ' ' + doc.get(Publications.CLEAN_TEXT.mongo)

        tokens = [token for token in tokenize_text(text) if len(token) > 3]
        counter = Counter(tokens)
        total = sum(count for count in counter.values())

        term_freq = {}
        for token, count in counter.items():
            term_freq[token] = count / total
            doc_freq[token] = doc_freq.get(token, 0) + 1

        doc_term_freq[cluster_id] = term_freq

    idf = {}
    for token, doc_count in doc_freq.items():
        idf[token] = math.log(doc_size / doc_count)

    cluster_tfidf_vectors = {}
    for cluster_id, term_freq in doc_term_freq.items():
        tfidf_vector = {}
        for term, freq in term_freq.items():
            tfidf_vector[term] = freq * idf[term]
        cluster_tfidf_vectors[cluster_id] = tfidf_vector

    output_path = Path.home() / 'clusters_tfidf.csv'
    with open(file=str(output_path), encoding='utf8', mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        header = ['ClusterID', 'Token', 'Weight']
        writer.writerow(header)

        for cluster_id, tfidf_vector in cluster_tfidf_vectors.items():
            for token, weight in tfidf_vector.items():
                record = [str(cluster_id), token, str(weight)]
                writer.writerow(record)


if __name__ == '__main__':
    main()
