# Standard Libraries
import csv
from pathlib import Path
import re

# additional libraries (pip install ...)
import bs4
from bs4 import BeautifulSoup
import lxml
import pandas as pd

# Paths
PROJECT_DIRECTORY = Path(__file__).parent
DATA_PATH = PROJECT_DIRECTORY / "data"
KEY_ENGLISH_PATH = DATA_PATH / 'key_english.csv'
HELSINKI_DATA = DATA_PATH / "helsinki-raw"
HELSINKI_OT = HELSINKI_DATA / "0_AelfricTheOldTestament.xml"
AELFRIC_OT = DATA_PATH / "t_aelfric.csv"

def _get_bible_books():
    with open(KEY_ENGLISH_PATH, 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)

        book_index = headers.index(BOOK_KEY)
        name_index = headers.index(NAME_KEY)
        testament_index = headers.index(TESTAMENT_KEY)
        genre_index = headers.index(GENRE_KEY)

        return {
            int(book[name_index]): {
                'id': book[book_index],
                'testament': book[testament_index],
                'genre_id': int(book[genre_index]),
                'genre': genres[int(book[genre_index])]
            } for book in reader
        }

def get_book_number(sample_num):
    if 1 <= sample_num <= 4:
        return 1
    elif 5 <= sample_num <= 7:
        return 2
    elif sample_num == 8:
        return 3
    else:
        raise ValueError

def old_eng_old_testament():
    with open(HELSINKI_OT, 'r') as old_test, open(AELFRIC_OT, 'w') as file:
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
    old_eng_old_testament()
    ws_gospels()