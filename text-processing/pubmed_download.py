import ftplib
from pathlib import Path


class PubmedDownloader:
    def __init__(self):
        self.medline_ftp_host = 'ftp.ncbi.nlm.nih.gov'
        self.baseline_directory = 'pubmed/baseline'

    def download_baseline(self, output_dir):
        print('Downloading PubMed articles...')
        ftp = self.setup_ftp()
        files = ftp.nlst()
        count = 0
        for file in files:
            if '.md5' not in file:
                count += 1
                if count % 10 == 0:
                    print("STATUS: " + str(count) + '\t FILE: ' + file)

                local_file = output_dir / file
                with open(local_file, 'wb') as f:
                    ftp.retrbinary('RETR ' + file, f.write)

        ftp.quit()
        print('Done. Downloaded ' + str(count) + ' files.')

    def setup_ftp(self):
        ftp = ftplib.FTP(self.medline_ftp_host)
        ftp.login()
        ftp.cwd(self.baseline_directory)

        return ftp


if __name__ == '__main__':
    output_dir = Path.home() / 'pubmed_baseline'
    downloader = PubmedDownloader()
    downloader.download_baseline(output_dir)
