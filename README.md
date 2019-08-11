<p align="center">
  <a href=#>
    <img src="resources/spider.png" alt="Spoken-Digit Recognizer" width="96" height="96">
  </a>
  <h2 align="center">Google Patents Scraper</h2>
    <div align="center">
  	(1) Automatically download all PDF files of searching results & their patent families.
  </div>
    <div align="center">
    (2) Generate an overview report of searching results.
  </div>
</p>


## Table of contents
* [Application Demo](#application-demo)
* [Introduction](#introduction)
* [Built With](#built-with)
* [Getting Started](#getting-started)
* [Acknowledgments](#acknowledgments)


## Application Demo
### [Google Patents Scraper – Demo (YouTube)](https://youtu.be/HRl3ChPxbIo)

## Introduction
This application scrape Google Patents by two steps:

* Set Proxy (Optional)
* Search & Download Patents

### Set Proxy (Optional)
* Set proxy to avoid current ip blocked by Google Patents

<p align="center">
    <img src="resources/set_proxy.png" alt="preprocessing" width="600">
</p>


### Search & Download Patents
* Select an output directory to store downloaded/generated files
* Search whatever you like (search terms' format same as Google Patents)
* Download PDF files of searching results & their patent families

PDF files and auto-generated `overview.md` will then be stored in selected directory

<p align="center">
    <img src="resources/search_download.png" alt="preprocessing" width="600">
</p>

### File Structure of Output Directory
<pre>
├── PDFs
│   ├── CN104321947A.pdf
│   ├── ...
│   └── readme.txt
├── Family_PDFs
│   ├── CN104321947A's\ Family
│   │   ├── EP2850716B1.pdf
│   │   ├── ...
│   │   └── readme.txt
│   ├── ...
│   └── ...
└── overview.md
</pre>
* Output directory of demo located at [Demo_outdir](https://github.com/wenyalintw/Google-Patents-Scraper/tree/master/Demo_outdir)
* [overview.md](https://github.com/wenyalintw/Google-Patents-Scraper/blob/master/Demo_outdir/overview.md) represents the summary of completed searching

## Built With
Modules besides python built-ins

 * Web Scarping - [Selenium](https://www.seleniumhq.org/) / [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) / [requests](https://2.python-requests.org//en/master/)
 * GUI framework - [PyQt5](https://pypi.org/project/PyQt5/)
 * Others - [fake-useragent](https://github.com/hellysmile/fake-useragent) / [tqdm](https://pypi.org/project/tqdm/)

## Getting Started
### Prerequisites
* Download a [ChromeDriver](https://chromedriver.chromium.org/) which correspond with your Chrome version
* Replace the one in [src/resources](https://github.com/wenyalintw/Google-Patents-Scraper/tree/master/src/resources)

### Installation

* Clone the repo

```sh
git clone https://github.com/wenyalintw/Google-Patents-Scraper.git
```

* Install required modules listed in [requirements.txt](https://github.com/wenyalintw/Google-Patents-Scraper/blob/master/requirements.txt)

```sh
pip install -r /path/to/requirements.txt
```

* Ready to go

```sh
cd src
python main.py
```


## Acknowledgments
- Checking process of proxies modified from [ApsOps's repo](https://github.com/ApsOps/proxy-checker)
- [search.png](https://github.com/wenyalintw/Google-Patents-Scraper/blob/master/src/resources/iconfinder_search_461380.png) licensed under "CC BY 3.0" downloaded from [ICONFINDER](https://www.iconfinder.com/icons/1609653/brain_organs_icon)

