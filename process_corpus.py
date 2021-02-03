# Standard Libraries
import csv
import re

# additional libraries (pip install ...)
import bs4
from bs4 import BeautifulSoup

# Local Libraries
from src.data_manager import get_bible_book_id_map

from src.paths import WYCLIFFE_DIRECTORY_PATH, WYCLIFFE_KEY_PATH, WYCLIFFE_CSV_PATH
from src.paths import AELFRIC_OLD_TESTAMENT_XML_PATH, AELFRIC_CSV_PATH

from src.data_manager import BOOK_KEY, CHAPTER_KEY, VERSE_KEY, TEXT_KEY, ID_KEY

def parse_wycliffe():
    books = []
    id_ref = get_bible_book_id_map()
    # Get book id and fn of book
    with open(WYCLIFFE_KEY_PATH, 'r') as key:
        for line in key:
            name, fn = line.strip().split(' - ')
            if name.lower() in id_ref:
                books.append((id_ref[name.lower()], fn.upper()))

    with open(WYCLIFFE_CSV_PATH, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([ID_KEY, BOOK_KEY, CHAPTER_KEY, VERSE_KEY, TEXT_KEY])
        for book_id, fp in books:
            with open(WYCLIFFE_DIRECTORY_PATH / fp, 'r') as book_fp:
                chapter_id = 1
                for line in book_fp:
                    line = line.strip()
                    line = line.replace(r"\[.*\]", "")
                    if match := re.match(r'^(\d+) (.+)', line):
                        verse_id = int(match.group(1))
                        verse = match.group(2)
                        writer.writerow([f'%d%03d%03d' % (book_id, chapter_id, verse_id),
                                         book_id,
                                         chapter_id,
                                         verse_id,
                                         verse
                                         ])
                    elif match := re.match(r'^CAP (\d+)', line):
                        chapter_id = int(match.group(1))


def parse_aelfric_ot() -> None:
    id_ref = get_bible_book_id_map()
    with open(AELFRIC_OLD_TESTAMENT_XML_PATH, 'r', encoding='utf-8') as src, \
            open(AELFRIC_CSV_PATH, 'w',  newline='', encoding='utf-8') as dest:
        writer = csv.writer(dest)
        writer.writerow([ID_KEY, BOOK_KEY, CHAPTER_KEY, VERSE_KEY, TEXT_KEY])
        xml_doc = BeautifulSoup(src.read(), 'lxml')
        # extract the xml structure and the sample book numbers
        struct = xml_doc.find('biblstruct')
        sample_scope = struct.find('monogr').find_all('biblscope')
        sample_ids = [id_ref[scope.text.split(' ')[0].lower()] for scope in sample_scope]

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
            verse = ''
            cv = s.contents[0]['n'].split('.') + ['0']
            chapter_id = int(cv[0])
            verse_id = int(cv[1])
            i = 1
            while i < len(s.contents):
                if isinstance(s.contents[i], bs4.element.NavigableString):
                    verse += str(s.contents[i]).strip()
                elif isinstance(s.contents[i], bs4.element.Tag):
                    writer.writerow([f'%d%03d%03d' % (idx, chapter_id, verse_id), idx, chapter_id, verse_id, verse])
                    verse = ''
                    cv = s.contents[i]['n'].split('.') + ['0']
                    chapter_id = int(cv[0])
                    verse_id = int(cv[1])
                i += 1


if __name__ == '__main__':
    parse_wycliffe()
    # parse_aelfric_ot()
