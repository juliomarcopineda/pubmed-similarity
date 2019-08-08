from nlpre import identify_parenthetical_phrases, dedash, titlecaps, decaps_text, unidecoder, separate_reference, \
    url_replacement, replace_acronyms, pos_tokenizer, token_replacement, replace_from_dictionary
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

lemmatizer = WordNetLemmatizer()
default_stopwords = stopwords.words('english')

pre_pos_blacklist = ['cardinal', 'punctuation', 'connector']
post_pos_blacklist = ['pronoun', 'verb', 'adverb', 'adjective']


def clean_text(text):
    if not text:
        return ''

    abbreviations = identify_parenthetical_phrases()(text)
    parsers = [dedash(), titlecaps(), decaps_text(),
               unidecoder(), separate_reference(), url_replacement(),
               replace_acronyms(counter=abbreviations, underscore=False),
               pos_tokenizer(pre_pos_blacklist), token_replacement(remove=True),
               replace_from_dictionary(), pos_tokenizer(post_pos_blacklist)]

    for parser in parsers:
        text = parser(text)

    text = remove_stopwords(text)
    text = lemmatize(text)

    return text


def tokenize_text(text):
    return [word for sentence in sent_tokenize(text) for word in word_tokenize(sentence)]


def lemmatize(text):
    tokens = tokenize_text(text)
    return ' '.join([lemmatizer.lemmatize(token) for token in tokens])


def remove_stopwords(text):
    tokens = [word for word in tokenize_text(text) if word not in default_stopwords]
    return ' '.join(tokens)
