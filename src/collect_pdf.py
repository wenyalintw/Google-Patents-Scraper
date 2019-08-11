from bs4 import BeautifulSoup
import requests
import os
from fake_useragent import UserAgent
from datetime import date
from tqdm import tqdm
from PyQt5.QtCore import pyqtSignal, QObject


class CollectPdf(QObject):

    signal_update = pyqtSignal(str)
    signal_download_progress = pyqtSignal(float)

    def __init__(self, outdir):
        super().__init__()
        self.origindir = os.getcwd()
        self.dir = outdir
        self.proxies = {}
        self.headers = {}
        self.ua_generator = None

    def setup(self):
        try:
            os.chdir(self.dir)
        except Exception as e:
            self.signal_update.emit(str(e))
            raise
        self.ua_generator = UserAgent(cache=False, verify_ssl=True)
        self.headers['User-Agents'] = self.ua_generator.chrome

    def download_pdf(self, link, dst):
        if os.path.isfile(dst):
            return
        response = requests.get(link, stream="TRUE")
        with open(dst, 'wb') as file:
            data_length = int(response.headers.get('content-length'))
            for data in tqdm(response.iter_content(chunk_size=1024), total=int(data_length / 1024) + 1, unit='KB',
                             unit_scale=True):
                if data:
                    file.write(data)
                    file.flush()

    def start_download(self, links, terms, option):
        self.setup()
        file_overview = open('overview.md', 'w')
        pre_content = ['---', '---', '# Searching Result Information',
                       f'* Search Terms: {terms}',
                       f'* Total Patents found: {len(links)}',
                       f'* Due Date: {date.today().strftime("%B %d, %Y")}', '',
                       '---', '---', ]
        pre_content = [s + '\n' for s in pre_content]
        file_overview.writelines(pre_content)

        no_pdf_count = 0

        pdf_downloaded = []
        pdf_fail_downloaded = []
        if not os.path.isdir('PDFs'):
            os.mkdir('PDFs')
        for index, link in enumerate(links, start=1):
            resp = requests.get(link, proxies=self.proxies, headers=self.headers, stream=True)
            soup = BeautifulSoup(resp.text, 'html.parser')
            temp = [s.strip() for s in soup.title.text.splitlines()[0].split(' - ')]
            number = temp[0]
            title = temp[1]
            abstract = soup.select('head > meta[name=description]')[0]['content'].strip()
            file_overview.write(
                f'<br><div align="center" style="font-size:28px">({index}) <a href="{link}">{number}</a></div>\n'
                f'## Title\n{title}\n## Abstract\n{abstract}\n## Family\n')
            try:
                # some old patent doesn't have pdf link
                pdf_link = soup.select('head > meta[name=citation_pdf_url]')[0]['content']
                # download pdf
                dst = f'PDFs/{number}.pdf'
                self.signal_update.emit(f'Downloading {number}.pdf')
                self.download_pdf(link=pdf_link, dst=dst)
                pdf_downloaded.append(f'{number}')
            except:
                no_pdf_count += 1
                self.signal_update.emit(f'{number}.pdf not found on Google Patents')
                pdf_fail_downloaded.append(f'{number}')

            family_links = soup.select('li[itemprop=applicationsByYear] > ul > li > a')
            family_links = ['https://patents.google.com/' + s.text for s in family_links]
            if link in family_links:
                family_links.remove(link)
            family_numbers = [s.split('/')[-2] for s in family_links]

            # if want to download family patents
            if option == 0:
                if not os.path.isdir('Family_PDFs'):
                    os.mkdir('Family_PDFs')
                family_pdf_downloaded = []
                family_pdf_fail_downloaded = []
                # if list isn't empty
                if family_links:
                    family_no_pdf_count = 0
                    dst = f'Family_PDFs/{number}\'s Family'
                    if not os.path.isdir(dst):
                        os.mkdir(dst)
                    for i, family_link in enumerate(family_links):
                        family_number = family_numbers[i]
                        resp2 = requests.get(family_link, proxies=self.proxies, headers=self.headers, stream=True)
                        soup2 = BeautifulSoup(resp2.text, 'html.parser')
                        try:
                            family_pdf_link = soup2.select('head > meta[name=citation_pdf_url]')[0]['content']
                            self.signal_update.emit(f'Downloading {number}\'s Family {family_number}.pdf')
                            self.download_pdf(link=family_pdf_link, dst=f'{dst}/{family_number}.pdf')
                            family_pdf_downloaded.append(f'{family_number}')
                        except:
                            family_no_pdf_count += 1
                            self.signal_update.emit(f'{number}\'s Family {family_number}.pdf '
                                                    f'not found on Google Patents')
                            family_pdf_fail_downloaded.append(f'{family_number}')
                        self.signal_download_progress.\
                            emit(int((((index-1) / len(links)) + (i / (len(family_links)*len(links))))*100))

                    with open(f'{dst}/readme.txt', 'w') as file:
                        file.write(f'PDFs Downloaded: {len(family_links) - family_no_pdf_count}\n')
                        file.writelines(['\n' + s for s in family_pdf_downloaded])
                        file.write(f'\n\nPDFs Not Found: {family_no_pdf_count}\n')
                        file.writelines(['\n' + s for s in family_pdf_fail_downloaded])
                        file.write(f'\n\nTotal: {len(family_links)}')

            if family_links:
                file_overview.writelines([f'* [{family_numbers[c]}]({s})\n' for c, s in enumerate(family_links)])
            else:
                file_overview.write('None\n')

            file_overview.write(f'\n---\n')

            self.signal_download_progress.emit(int(index/len(links)*100))

        file_overview.close()
        with open('PDFs/readme.txt', 'w') as file:
            file.write(f'PDFs Downloaded: {len(links) - no_pdf_count}\n')
            file.writelines(['\n' + s for s in pdf_downloaded])
            file.write(f'\n\nPDFs Not Found: {no_pdf_count}\n')
            file.writelines(['\n' + s for s in pdf_fail_downloaded])
            file.write(f'\n\nTotal: {len(links)}')

        os.chdir(self.origindir)
        self.signal_update.emit('Download Finished!')
