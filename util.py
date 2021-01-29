"""
Utility functions for accessing the dataset
"""

import csv
from pathlib import Path

PROJECT_DIRECTORY = Path(__file__).parent
DATA_PATH = PROJECT_DIRECTORY / 'data'
KEY_GENRE_ENGLISH_PATH = DATA_PATH / 'key_genre_english.csv'
KEY_ENGLISH_PATH = DATA_PATH / 'key_english.csv'

BOOK_KEY = 'b'
CHAPTER_KEY = 'c'
VERSE_KEY = 'v'
TEXT_KEY = 't'
TESTAMENT_KEY = 't'
GENRE_KEY = 'g'
NAME_KEY = 'n'

def make_tarball(output_filename: Path, source_dir: Path) -> None:
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

def get_bible_books_id() -> {str: int}:
    """
    Returns a dictionary where each key is the bible book name (lowercase),
    and each value is that book's id

    Returns:
        {
            'genesis' : 1,
            'exodus' : 2,
            ...
        }
    """
    with open(KEY_ENGLISH_PATH, 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)

        book_index = headers.index(BOOK_KEY)
        name_index = headers.index(NAME_KEY)
        testament_index = headers.index(TESTAMENT_KEY)
        genre_index = headers.index(GENRE_KEY)

        return {book[name_index]: int(book[book_index]) for book in reader}