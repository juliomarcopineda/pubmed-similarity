import math

from data.mongo_fields import Publications
from data.mongo_provider import MongoProvider

from text_processing.text_cleaner import tokenize_text
from collections import Counter, OrderedDict


collection = MongoProvider().get_publications_collection()


def main():
    docs = collection.find({}, {Publications.CLEAN_TEXT.mongo: 1})

    print('Determining document and term frequencies...')
    doc_term_freq = {}
    doc_freq = {}
    doc_size = 0
    for doc in docs:
        pmid = doc.get(Publications.PMID.mongo)
        clean_text = doc.get(Publications.CLEAN_TEXT.mongo, '')
        if clean_text:
            doc_size += 1

            tokens = tokenize_text(clean_text)
            counter = Counter(tokens)
            total = sum(count for count in counter.values())

            term_freq = {}
            for token, count in counter.items():
                term_freq[token] = count / total
                doc_freq[token] = doc_freq.get(token, 0) + 1

            doc_term_freq[pmid] = term_freq

    print('Calculating Inverse Document Frequencies...')
    idf = {}
    for token, doc_count in doc_freq.items():
        idf[token] = math.log(doc_size / doc_count)

    print('Calculating TF-IDF vectors...')
    tfidf_vectors = {}
    for pmid, term_freq in doc_term_freq.items():
        tfidf_vector = {}
        for term, freq in term_freq.items():
            tfidf_vector[term] = freq * idf[term]
        tfidf_vectors[pmid] = tfidf_vector

    print('Updating MongoDB with TF-IDF vectors...')
    status = 0
    for pmid, tfidf_vector in tfidf_vectors.items():
        status += 1
        if status % 100 == 0:
            print('STATUS:', status)

        tfidf_vector = OrderedDict(sorted(tfidf_vector.items(), key=lambda kv: kv[1]))
        filter_doc = {
            Publications.PMID.mongo: pmid
        }
        update_doc = {
            '$set': {
                Publications.TFIDF_VECTOR.mongo: tfidf_vector
            }
        }
        collection.update_one(filter=filter_doc, update=update_doc)
    print('STATUS:', status)
    print('Done.')


if __name__ == '__main__':
    main()