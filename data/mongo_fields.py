from enum import Enum


class MongoField(Enum):
    """Base class for all enum fields in MongoDB"""

    def __init__(self, mongo, spreadsheet=''):
        """Constructor for the base class that sets the MongoDB field name and Spreadsheet
        column names for each field

        :param str mongo: MongoDB field representation
        :param str spreadsheet: Column spreadsheet representation
        """

        self.mongo = mongo
        self.spreadsheet = spreadsheet


class Publications(MongoField):
    """Enums for fields in the publications collection"""

    PMID = ('_id', 'PMID')
    PUBLICATION_YEAR = ('publicationYear', 'Publication Year')
    JOURNAL = ('journal', 'Journal')
    TITLE = ('title', 'Article Title')
    AUTHORS = ('authors', 'Authors')
    ABSTRACT = ('abstract', 'Abstract Text')
    CLEAN_TEXT = ('cleanText', 'Clean Text')
