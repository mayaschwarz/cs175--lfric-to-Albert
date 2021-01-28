# Standard Libraries
import csv
import math
import re

# additional libraries (pip install ...)
import bs4
from bs4 import BeautifulSoup
import lxml
import pandas as pd

# Local Libraries
from util import *

WEBSITE = "http://wesley.nnu.edu/fileadmin/imported_site/biblical_studies/wycliffe/"

# Paths
PROJECT_DIRECTORY = Path(__file__).parent
DATA_PATH = PROJECT_DIRECTORY / "data"
KEY_ENGLISH_PATH = DATA_PATH / 'key_english.csv'
HELSINKI_DATA = DATA_PATH / "helsinki-raw"

AELFRIC_OT_XML = HELSINKI_DATA / "0_AelfricTheOldTestament.xml"
AELFRIC_CSV = DATA_PATH / "t_alf.csv"

WYCLIFFE_PATH = DATA_PATH / "wycbible"
WYCLIFFE_KEY = WYCLIFFE_PATH / "index.txt"
WYCLIFFE_CSV = DATA_PATH / 't_wyc.csv'

def parse_wycliffe():
    books = []
    id_ref = get_bible_books_id()
    # Get book id and fn of book
    with open(WYCLIFFE_KEY, 'r') as key:
        for line in key:
            name, fn = line.strip().split(' - ')
            if name in id_ref:
                books.append((id_ref[name], fn))

    with open(WYCLIFFE_CSV, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['id', BOOK_KEY, CHAPTER_KEY, VERSE_KEY, TEXT_KEY])
        for book_id, fp in books:
            with open(WYCLIFFE_PATH / fp, 'r') as book_fp:
                chapter_id = 1
                for line in book_fp:
                    line = line.strip()
                    if match := re.match(r"^(\d+) (.+)", line):
                        verse_id = int(match.group(1))
                        verse = match.group(2)
                        writer.writerow([f"%d%03d%03d" % (book_id, chapter_id, verse_id),
                                         book_id,
                                         chapter_id,
                                         verse_id,
                                         verse
                                         ])
                    elif match := re.match(r"^CAP (\d+)", line):
                        chapter_id = int(match.group(1))


def parse_aelfric_ot() -> None:
    id_ref = get_bible_books_id()
    with open(AELFRIC_OT_XML, 'r') as src, open(AELFRIC_CSV, 'w',  newline='', encoding='utf-8') as dest:
        writer = csv.writer(dest)
        writer.writerow(['id', BOOK_KEY, CHAPTER_KEY, VERSE_KEY, TEXT_KEY])
        xml_doc = BeautifulSoup(src.read(), 'lxml')
        # extract the xml structure and the sample book numbers
        struct = xml_doc.find('biblstruct')
        sample_scope = struct.find('monogr').find_all('biblscope')
        sample_ids = [id_ref[scope.text.split(" ")[0]] for scope in sample_scope]

        # extract the text
        text = xml_doc.find('text')

        # remove all the linebreaks in the text
        for lb in text.find_all('lb'):
            lb.decompose()

        # If run into <choice> tag, replace with correction
        for c in text.find_all('choice'):
            errata = c.find('corr')
            c.replaceWith(errata.text if errata else '')

        # If run into <supplied> or <foreign>, insert text into string
        for s in text.find_all(re.compile('(supplied|foreign)')):
            s.replaceWith(c.text)

        # If run into milestone, remove type with scriptural
        for m in text.find_all('milestone', attrs={'type': 'scriptural'}):
            m.decompose()

        # Remove notes
        for n in text.find_all(re.compile('(note|pb)')):
            n.decompose()

        samples = text.find_all('div', attrs={'type': 'sample'})
        for idx, s in zip(sample_ids, samples):
            s = s.find('p')
            verse = ""
            cv = s.contents[0]['n'].split('.') + ['0']
            chapter_id = int(cv[0])
            verse_id = int(cv[1])
            i = 1
            while i < len(s.contents):
                if isinstance(s.contents[i], bs4.element.NavigableString):
                    verse += str(s.contents[i]).strip()
                elif isinstance(s.contents[i], bs4.element.Tag):
                    writer.writerow([f"%d%03d%03d" % (idx, chapter_id, verse_id), idx, chapter_id, verse_id, verse])
                    verse = ""
                    cv = s.contents[i]['n'].split('.') + ['0']
                    chapter_id = int(cv[0])
                    verse_id = int(cv[1])
                i += 1

def old_eng_old_testament():
    with open(AELFRIC_OT_XML, 'r') as old_test, open(AELFRIC_OT, 'w') as file:
        contents = old_test.read()
        bs = BeautifulSoup(contents, 'lxml')
        text = bs.find('text')
        # Extract all the samples
        samples = text.find_all('div', attrs={'type': 'sample', 'n': re.compile('^sample[0-9]')})
        for s in samples:
            # get book number
            book_id = get_book_number(int(s['n'][len('sample'):]))

            # extract paragraph
            s = s.find('p')

            # remove unnecessary milestones
            for m in s.select('milestone'):
                if m['type'] == 'scriptural':
                    m.decompose()

            for c in s.find_all(re.compile('(lb|choice|supplied|pb)')):
                print(c.text)

            print(s.contents)
            raise
            paired = []
            running_str = ''
            milestone = s.contents[0]
            i = 1
            while i < len(s.contents):
                if isinstance(s.contents[i], bs4.element.Tag):
                    paired.append((milestone, running_str))
                    running_str = ""
                    milestone = s.contents[i]
                elif isinstance(s.contents[i], bs4.element.NavigableString):
                    running_str += str(s.contents[i]).strip()
                i += 1

            for m, s in paired:
                print(m)
                c_v = float(m['n'])
                chapter = int(c_v)
                verse = int((c_v * 100) % 100)
                file.write(f"{chapter}, {verse}, {s}")


if __name__ == '__main__':
    #parse_wycliffe()
    parse_aelfric_ot()