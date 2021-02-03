# Standard Libraries
import csv
from pathlib import Path
import re
import requests
import time
from urllib.parse import urljoin, urlparse, parse_qs

# additional libraries (pip install ...)
import bs4
from bs4 import BeautifulSoup

# Local libraries
from src.data_manager import get_bible_book_id_map
from src.utils import make_tarball, beautify, get_links

from src.data_manager import BOOK_KEY, CHAPTER_KEY, VERSE_KEY, TEXT_KEY, ID_KEY
from src.paths import *

# BASE URLS
HELSINKI_CORPUS_URL = 'https://helsinkicorpus.arts.gla.ac.uk'
MIDDLE_ENGLISH_PROSE_VERSE_URL = 'https://quod.lib.umich.edu'
STUDY_BIBLE_URL = 'https://studybible.info'


def _get_url_params(url: str) -> {str: [str]}:
    """ Helper function to wrap parse_qs """
    parsed = urlparse(url)
    return parse_qs(parsed.query)


def _collect_helsinki() -> None:
    """
    Collects RAW XML from Helsinki Corpus and stores in directory 'data/raw/helsinki'

    Returns:
        None
    """
    # create directory for raw data
    HELSINKI_RAW_PATH.mkdir(parents = True, exist_ok = True)

    # extract table of contents with links
    toc_url = urljoin(HELSINKI_CORPUS_URL, 'browse.py?fs=100')
    hs = beautify(toc_url)
    toc = hs.find('div', attrs={'id': 'toc'}).find('ul')
    doc_links = get_links(toc, 'browse.py?')

    for idx, (href, name) in enumerate(doc_links):
        print(f'[{idx}/{len(doc_links)}] {name}')

        # Format link name to acceptable filename
        fn = re.sub('[^A-Za-z0-9]+', '', name)

        params = _get_url_params(href)
        if 'text' not in params:
            print('Unable to retrieve text', name)
            continue

        doc_url = urljoin(HELSINKI_CORPUS_URL, f"hc_xml/{params['text'][0]}.xml")
        print('\t  retrieving:', doc_url)

        xml_doc = requests.get(doc_url)
        if xml_doc is None:
            print('Unable to retrieve text', name)
            continue

        with open(HELSINKI_RAW_PATH / f'{idx}_{fn}.xml', 'w') as file:
            file.write(xml_doc.text)

def _collect_me_prose() -> None:
    """
    Collects texts from Middle English Corpus and stores as txt files in 'data/raw/middle_english_prose'

    Returns:
        None
    """
    # create directory for raw data
    MIDDLE_ENGLISH_PROSE_VERSE_RAW_PATH.mkdir(parents = True, exist_ok = True)

    # extract table of contents with links
    me = beautify(urljoin(MIDDLE_ENGLISH_PROSE_VERSE_URL, '/c/cme/browse.html'))
    toc = me.find('div', attrs={'class': 'maincontent'})
    doc_links = get_links(toc, '/c/cme/')

    for idx, (href, name) in enumerate(doc_links):
        print(f'[{idx}/{len(doc_links)}] {name}')

        # Format link name to acceptable filename
        fn = re.sub('[^A-Za-z0-9]+', '', name)[: 101 if len(name) > 100 else len(name)]

        doc_url = urljoin(MIDDLE_ENGLISH_PROSE_VERSE_URL, href + '/?rgn=main;view=fulltext')
        print('\t  retrieving: ', doc_url)

        html_doc = beautify(doc_url)
        if html_doc is None:
            print('Unable to retrieve text', name)
            continue

        content = html_doc.find('div', attrs={'id': 'doccontent'})
        with open(MIDDLE_ENGLISH_PROSE_VERSE_RAW_PATH / f'{idx}_{fn}.txt', 'w', encoding='utf-8') as file:
            file.write(content.text)

def _collect_bible_study(url_path: str, csv_file: Path) -> None:
    """
    Function to generate csv file for bibles at studybible.com. Given the name of the bible and the csv_file,
    generates csv with format following the bible corpus structure

    Args:
        url_path {str} -- part of url following the base URL (https://studybible.info/Wycliffe -> /Wycliffe)
        csv_file {Path} -- destination csv

    Returns:
        None
    """
    # Set up a session
    session = requests.Session()
    session.headers.update({'User-Agent': 'custom-user-agent'})

    # Get ids for books
    id_ref = get_bible_book_id_map()

    # extract the table of contents for all books
    ws_url = urljoin(STUDY_BIBLE_URL, '/version' + url_path)
    ws = beautify(ws_url, session=session)
    toc = ws.find('div', attrs={'class': 'version_toc'})
    books = get_links(toc, url_path)
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the title row
        writer.writerow([ID_KEY, BOOK_KEY, CHAPTER_KEY, VERSE_KEY, TEXT_KEY])
        for ex, name in books:
            if name.lower() not in id_ref:
                continue
            print('Downloading', name)
            book_id = id_ref[name.lower()]
            # extract chapters
            book_url = urljoin(STUDY_BIBLE_URL, ex)
            bs = beautify(book_url, session=session)
            toc = bs.find('div', attrs={'class': 'book_toc'})
            chapters = get_links(toc, ex)

            for c, c_num in chapters:
                print('\tCAP. ', c_num)
                c_id = int(c_num)
                chapter_url = urljoin(STUDY_BIBLE_URL, c)
                cs = beautify(chapter_url, session=session)
                text = cs.find('div', attrs={'class': 'passage'})
                # First and second entry are garbage
                verses = [x.strip() for x in text.contents if not isinstance(x, bs4.element.Tag)][2:]
                for i, v in enumerate(verses):
                    v_id = i+1
                    # Remove notes from the verses
                    v = re.sub(r'\[.*\]', '', v).strip()
                    writer.writerow([f'%d%03d%03d' % (book_id, c_id, v_id), book_id, c_id, v_id, v])
                # delay to not overload server with requests
                time.sleep(5)


def _collect_raw_corpus():
    """ Retrieve corpora and individual texts """
    # collect the corpus
    #_collect_helsinki()
    #_collect_me_prose()

    # collect individual texts
    _collect_bible_study('/WestSaxon1175', WEST_SAXON_GOSPEL_CSV_PATH)

    # store raw-texts as tar files
    #make_tarball(HELSINKI_RAW_TAR_PATH, HELSINKI_RAW_PATH)
    #make_tarball(MIDDLE_ENGLISH_PROSE_VERSE_RAW_TAR_PATH, MIDDLE_ENGLISH_PROSE_VERSE_RAW_PATH)

if __name__ == '__main__':
    _collect_raw_corpus()
