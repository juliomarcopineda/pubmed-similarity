from data.mongo_provider import MongoProvider
from pathlib import Path
import csv


publications = MongoProvider(Path.home() / '.dsca' / 'app.config').get_publications_collection()


def construct_mongo_doc(row):
    pass


def main():
    data_path = Path.home() / '2018_cancer.csv'
    with open(data_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            doc = construct_mongo_doc(row)


if __name__ == '__main__':
    main()
