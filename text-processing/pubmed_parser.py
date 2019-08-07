from pathlib import Path
import gzip
import xml.etree.ElementTree as ET
import pandas as pd
import ftplib
import sys
from io import BytesIO

medline_ftp_host = 'ftp.ncbi.nlm.nih.gov'
baseline_directory = 'pubmed/baseline'


def get_citation_data(citation):
    citation_data = {}

    pmid_node = citation.find('PMID')
    year_node = citation.find('DateCompleted/Year')
    journal_node = citation.find('Article/Journal/Title')
    title_node = citation.find('Article/ArticleTitle')
    abstract_text_node = citation.find('Article/Abstract/AbstractText')

    names = []
    for author in citation.findall('Article/AuthorList/Author'):
        last_name_node = author.find('LastName')
        fore_name_node = author.find('ForeName')

        last_name = ''
        fore_name = ''

        if last_name_node is not None:
            last_name = last_name_node.text
        if fore_name_node is not None:
            fore_name = fore_name_node.text

        if last_name and fore_name:
            name = last_name + ", " + fore_name
            names.append(name)

    if pmid_node is not None:
        pmid_text = pmid_node.text
        if pmid_text:
            citation_data['pmid'] = int(pmid_text)
    if year_node is not None:
        year_text = year_node.text
        if year_text:
            citation_data['year'] = int(year_text)
    if journal_node is not None:
        journal = journal_node.text
        if journal:
            citation_data['journal'] = journal
    if title_node is not None:
        title = title_node.text
        if title:
            citation_data['title'] = title
    if abstract_text_node is not None:
        abstract = abstract_text_node.text
        if abstract:
            citation_data['abstract'] = abstract
    if names:
        authors = ';'.join(names)
        citation_data['authors'] = authors

    return citation_data


def setup_ftp():
    ftp = ftplib.FTP(medline_ftp_host)
    ftp.login()
    ftp.cwd(baseline_directory)

    return ftp


def main():
    print('Parsing PubMed XML files...')

    data = []
    corrupted_files = []

    ftp = setup_ftp()
    files = ftp.nlst()
    valid_files = [file for file in files if '.md5' not in file and 'README.txt' != file]
    for file in valid_files:
        print("READING: " + file)
        bio = BytesIO()
        ftp.retrbinary('RETR ' + file, bio.write)
        bio.seek(0)
        try:
            xml_bytes = bio.read()
            decompressed = gzip.decompress(xml_bytes)
            xml = decompressed.decode('utf-8')
            root = ET.fromstring(xml)

            for citation in root.findall('PubmedArticle/MedlineCitation'):
                year_node = citation.find('DateCompleted/Year')
                if year_node is not None:
                    year_string = year_node.text
                    if year_string:
                        year = int(year_string)
                        if year == 2018:
                            citation_data = get_citation_data(citation)
                            data.append(citation_data)
        except:
            print("Corrupted file: " + file)
            corrupted_files.append(file)

    ftp.quit()

    # pubmed_dir = Path.home() / 'pubmed_baseline'
    # for gz_file in pubmed_dir.iterdir():
    #     print('READING: ' + str(gz_file))
    #     pubmed_gz = gzip.GzipFile(gz_file, mode='rb')
    #     try:
    #         gz_read_data = pubmed_gz.read()
    #         xml_string = gz_read_data.decode('utf-8')
    #         root = ET.fromstring(xml_string)
    #
    #         for citation in root.findall('PubmedArticle/MedlineCitation'):
    #             year_node = citation.find('DateCompleted/Year')
    #             if year_node is not None:
    #                 year_string = year_node.text
    #                 if year_string:
    #                     year = int(year_string)
    #                     if year == 2018:
    #                         citation_data = get_citation_data(citation)
    #                         data.append(citation_data)
    #     except:
    #         print("Corrupted file: " + str(gz_file))
    #         corrupted_files.append(gz_file)

    print('Converting data to DataFrame...')
    df = pd.DataFrame(data)

    output_file = Path.home() / 'pubmed_data_2018.csv'
    print('Writing data to ' + str(output_file) + '...')

    df.to_csv(output_file, index=False)
    print('Done.')

    corrupted_output = Path.home() / 'corrupted_files.txt'
    with open(corrupted_output, mode='w') as f:
        for file in corrupted_files:
            f.write(str(file) + '\n')


if __name__ == '__main__':
    main()
