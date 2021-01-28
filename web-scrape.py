# Standard Libraries
import csv
from pathlib import Path
import tarfile
import os
import re
import requests
import time
from urllib.parse import urljoin, urlparse, parse_qs

# additional libraries (pip install ...)
import bs4
from bs4 import BeautifulSoup
import lxml

# Local libraries
from util import *

# Paths
HELSINKI_PATH = DATA_PATH / "helsinki-raw"
ME_PROSE_VERSE_PATH = DATA_PATH / 'me-prose-raw'
WS_GOSPEL_PATH = DATA_PATH / 't_ws.csv'
WYCLIFFE_PATH = DATA_PATH / 't_wyc.csv'

# BASE URLS
HELSINKI_CORPUS = "https://helsinkicorpus.arts.gla.ac.uk"
ME_PROSE_VERSE = "https://quod.lib.umich.edu"
STUDY_BIBLE = "https://studybible.info"

def _make_tarball(output_filename: Path, source_dir: Path) -> None:
    """
    Generates a tarball (tar.gz) of a source directory at the location "output_filename"

    Arguments:
        output_filename {Path} -- filepath of tarball (should include file extension)
        source_dir {Path} -- directory that comprises the tarball

    Returns:
        None
    """
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def _beautify(url: str, parser="html.parser", session=None) -> BeautifulSoup or None:
    """
    Returns BeautifulSoup object of url or None

    If timeout occurs, will prompt the user to either re-attempt download or not
    raises RequestException if catastrophic error

    Args:
        url {str} -- path to object
        parser{str} -- parser type, default is html.parser
        session {Session} -- Session is being maintained over connection

    Returns:
        success -- BeautifulSoup
        failure -- None
    """
    while True:
        try:
            response = requests.get(url) if session is None else session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, parser)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 504:
                choice = input("Timeout Error Occurred: Re-attempt download? [y|n] ")
                if choice == "y":
                    continue
                else:
                    return None
        except requests.exceptions.RequestException as e:
            raise e


def _get_links(document: BeautifulSoup, href_startswith: str) -> [(str, str)]:
    """
    Extracts <a> tags whose href tags begin with "href_startswith" from document. Returns list of tuple containing
    href value and <a> tag text

    Args:
        document {BeautifulSoup} = html document to extract from
        href_startswith {str} -- beginning of url string

    Returns:
        [(str, str)] -- list of (href value, text)
    """
    tags = document.find_all('a', attrs={"href": re.compile(f'^{href_startswith}')})
    return [(a['href'], a.text) for a in tags]


def _get_url_params(url) -> {str: [str]}:
    """ Helper function to wrap parse_qs """
    parsed = urlparse(url)
    return parse_qs(parsed.query)


def _collect_helsinki() -> None:
    """
    Collects RAW XML from Helsinki Corpus and stores in directory 'data/helsinki-raw'

    Returns:
        void
    """
    # create directory for raw data
    if not os.path.exists(HELSINKI_PATH):
        os.mkdir(HELSINKI_PATH)

    # extract table of contents with links
    toc_url = urljoin(HELSINKI_CORPUS, "browse.py?fs=100")
    hs = _beautify(toc_url)
    toc = hs.find("div", attrs={"id": "toc"}).find("ul")
    doc_links = _get_links(toc, "browse.py?")

    for idx, (href, name) in enumerate(doc_links):
        print(f"[{idx}] {name}")

        # Format link name to acceptable filename
        fn = re.sub("[^A-Za-z0-9]+", "", name)

        params = _get_url_params(href)
        if 'text' not in params:
            print("Unable to retrieve text", name)
            continue

        doc_url = urljoin(HELSINKI_CORPUS, f"hc_xml/{params['text'][0]}.xml")
        print("\t  retrieving:", doc_url)

        xml_doc = requests.get(doc_url)
        if xml_doc is None:
            print("Unable to retrieve text", name)
            continue

        with open(HELSINKI_PATH / f"{idx}_{fn}.xml", 'w') as file:
            file.write(xml_doc.text)


def _collect_me_prose() -> None:
    """
    Collects texts from Middle English Corpus and stores as txt files in 'data/me-prose-raw'

    Returns:
        void
    """
    # create directory for raw data
    if not os.path.exists(ME_PROSE_VERSE_PATH):
        os.mkdir(ME_PROSE_VERSE_PATH)

    # extract table of contents with links
    me = _beautify(urljoin(ME_PROSE_VERSE, '/c/cme/browse.html'))
    toc = me.find('div', attrs={'class': 'maincontent'})
    doc_links = _get_links(toc, '/c/cme/')

    for idx, (href, name) in enumerate(doc_links):
        print(f"[{idx}] {name}")

        # Format link name to acceptable filename
        fn = re.sub("[^A-Za-z0-9]+", "", name)[: 101 if len(name) > 100 else len(name)]

        doc_url = urljoin(ME_PROSE_VERSE, href + '/?rgn=main;view=fulltext')
        print("\t  retrieving: ", doc_url)

        html_doc = _beautify(doc_url)
        if html_doc is None:
            print("Unable to retrieve text", name)
            continue

        content = html_doc.find('div', attrs={'id': 'doccontent'})
        with open(ME_PROSE_VERSE_PATH / f"{idx}_{fn}.txt", 'w', encoding='utf-8') as file:
            file.write(content.text)


def _collect_bible_study(url_path: str, csv_file: Path) -> None:
    """
    Function to generate csv file for bibles at studybible.com. Given the name of the bible and the csv_file,
    generates csv with format following the bible corpus structure

    Args:
        url_path {str} -- part of url following the base URL (https://studybible.info/Wycliffe -> /Wycliffe)
        csv_file {Path} -- destination csv

    Returns:
        void
    """
    # Set up a session
    session = requests.Session()
    session.headers.update({'User-Agent': 'custom-user-agent'})

    # Get ids for books
    id_ref = get_bible_books_id()

    # extract the table of contents for all books
    ws_url = urljoin(STUDY_BIBLE, '/version' + url_path)
    ws = _beautify(ws_url, session=session)
    toc = ws.find('div', attrs={'class': 'version_toc'})
    books = _get_links(toc, url_path)
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the title row
        writer.writerow(['id', BOOK_KEY, CHAPTER_KEY, VERSE_KEY, TEXT_KEY])
        for ex, name in books:
            if name not in id_ref:
                continue
            print("Downloading", name)
            book_id = id_ref[name]
            # extract chapters
            book_url = urljoin(STUDY_BIBLE, ex)
            bs = _beautify(book_url, session=session)
            toc = bs.find('div', attrs={'class': 'book_toc'})
            chapters = _get_links(toc, ex)

            for c, c_num in chapters:
                print("\tCAP. ", c_num)
                c_id = int(c_num)
                chapter_url = urljoin(STUDY_BIBLE, c)
                cs = _beautify(chapter_url, session=session)
                text = cs.find('div', attrs={'class': 'passage'})
                # First and second entry are garbage
                verses = [x.strip() for x in text.contents if not isinstance(x, bs4.element.Tag)][2:]
                for i, v in enumerate(verses):
                    v_id = i+1
                    # Remove notes from the verses
                    v = re.sub(r'\[.*\]', "", v).strip()
                    writer.writerow([f"%d%03d%03d" % (book_id, c_id, v_id), book_id, c_id, v_id, v])
                # delay to not overload server with requests
                time.sleep(10)


def _collect_raw_corpus():
    """ Retrieve corporaa and individual texts """
    # collect the corpus
    _collect_helsinki()
    _collect_me_prose()

    # collect individual texts
    _collect_bible_study("/WestSaxon1175", WS_GOSPEL_PATH)

    # store raw-texts as tarfiles
    _make_tarball(DATA_PATH / 'helsinki-raw.tar.gz', HELSINKI_PATH)
    _make_tarball(DATA_PATH / 'me-prose-raw.tar.gz', ME_PROSE_VERSE_PATH)


if __name__ == '__main__':
    _collect_raw_corpus()
