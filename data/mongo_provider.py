from enum import Enum
from pymongo import MongoClient
from pathlib import Path


class Collection(Enum):
    """Enums for the different MongoDB collections"""

    PUBLICATIONS = 'publications'

    def __init__(self, collection_name):
        self.collection_name = collection_name


class MongoProvider:
    """Class for establishing connections to MongoDB and convenient collection level commands"""

    def __init__(self, path=Path.home() / '.mongo/config'):
        """Constructor for MongoProvider and establish DB connection"

        :param path: MongoDB connection config file path (defualts tp $HOME/.dsca/app.config)
        """

        config = self._read_config_file(config_file=path)
        client = self._setup_client(config)
        self.db = client[config['mongo.db']]

    def get_publications_collection(self):
        """Return publication collection"""

        return self._get_collection(Collection.PUBLICATIONS)

    def _get_collection(self, collection):
        """Return MongoDB collection given Collection enum

        :param Collection collection: Collection enum
        :return: MongoDB collection
        """

        return self.db[collection.collection_name]

    @staticmethod
    def _read_config_file(config_file):
        """Read config file and return dictionary of config parameters

        :param config_file: MongoDB connection config file path
        :return: dict of config parameters
        """

        config = {}
        with open(config_file, mode='r') as fid:
            for line in fid:
                split = line.split('=')
                config[split[0].strip()] = split[1].strip()

        return config

    @staticmethod
    def _setup_client(config):
        """Establish MongoClient using config parameters and return MongoDB client

        :param dict config: MongoDB-related client parameters for establishing connection
        :return: MongoClient based on config
        """

        return MongoClient(config['mongo.host'],
                           # username=config['mongo.user'],
                           # password=config['mongo.password'],
                           authSource=config['mongo.db'])
