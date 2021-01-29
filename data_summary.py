# Standard libraries
import csv
from pathlib import Path

# Additional libraries (pip install ...)
import texttable

# Paths
PROJECT_DIRECTORY = Path(__file__).parent
DATA_PATH = PROJECT_DIRECTORY /  'data'
KEY_GENRE_ENGLISH_PATH = DATA_PATH / 'key_genre_english.csv'
KEY_ENGLISH_PATH = DATA_PATH / 'key_english.csv'
TABLE_KEY_PATH = DATA_PATH / 't_key.csv'
TABLE_DIRECTORY = DATA_PATH
TABLE_NAME_FORMAT = '{table}.csv'

# CSV header names
BOOK_KEY = 'b'
CHAPTER_KEY = 'c'
VERSE_KEY = 'v'
TEXT_KEY = 't'
TESTAMENT_KEY = 't'
GENRE_KEY = 'g'
NAME_KEY = 'n'
DATASET_KEY = 'dataset'

# Other constants
TESTAMENT_NAMES = { 'OT': 'Old Testament', 'NT': 'New Testament' }

def get_bible_versions() -> [dict]:
    """
    Returns a list of bible version objects, taken from t_key.csv

    Returns:
        [
            {
                'id': 1,
                'table': 't_asv',
                'abbreviation': 'ASV',
                'language': 'english',
                'version': 'American Standard',
                ...
            },
            {
                'id': 2,
                'table': 't_bbe',
                'abbreviation': 'BBE',
                ...
            },
            ...
        ]
    """
    bible_versions = list()

    with open(TABLE_KEY_PATH, 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)

        for line in reader:
            bible_versions.append({k: line[i] for (i, k) in enumerate(headers)})
            bible_versions[-1]['id'] = int(bible_versions[-1]['id'])

    return bible_versions

def get_bible_book_genres() -> {int: str}:
    """
    Returns a dictionary where each key is the bible genre id,
    and each value is the bible genre name (uses key_genre_english.csv)

    Returns:
        {
            1: 'Law',
            2: 'History',
            3: 'Wisdom',
            4: 'Prophets',
            5: 'Gospels',
            6: 'Acts',
            7: 'Epistles',
            8: 'Apocalyptic'
        }
    """
    with open(KEY_GENRE_ENGLISH_PATH, 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)

        genre_index = headers.index(GENRE_KEY)
        name_index = headers.index(NAME_KEY)

        return { int(genre[genre_index]): genre[name_index] for genre in reader }

def get_bible_books() -> {int: dict}:
	"""
	Returns a dictionary where each key is the bible book id,
	and each value is that book's details (uses key_english.csv)

	Returns:
		{
			1: {
				'name': 'Genesis',
				'testament': 'OT', (old testament)
				'genre_id': 1,
				'genre': 'Law',
				'dataset': 'test'
			},
			2: {
				'name': 'Exodus',
				'testament': 'OT',
				'genre_id': 1,
				'genre': 'Law',
				'dataset': 'train'
			},
			...
		}
	"""
	genres = get_bible_book_genres()

	with open(KEY_ENGLISH_PATH, 'r') as csvfile:
		reader = csv.reader(csvfile)
		headers = next(reader)

		book_index = headers.index(BOOK_KEY)
		name_index = headers.index(NAME_KEY)
		testament_index = headers.index(TESTAMENT_KEY)
		genre_index = headers.index(GENRE_KEY)
		dataset_index = headers.index(DATASET_KEY)

		return {
			int(book[book_index]): {
				'name': book[name_index],
				'testament': book[testament_index],
				'genre_id': int(book[genre_index]),
				'genre': genres[int(book[genre_index])],
				'dataset': book[dataset_index]
			} for book in reader
		}

def get_books_contained_by_version(bible_version: dict) -> [int]:
    """
    Some versions might be missing books (once we start web scraping).
    This will return a list of all the book ids for books contained by one of our versions.
    The 7 versions in the Kaggle bible corpus contain all 66 books.

    Arguments:
        bible_version {dict} -- the bible version object, as returned by get_bible_versions

    Returns:
        [int] -- [book id contained by given bible version]

    Example return:
        [1, 2, 3, ..., 64, 65, 66] (if no books are missing)
    """
    table_path = TABLE_DIRECTORY / TABLE_NAME_FORMAT.format(table = bible_version['table'])

    with open(table_path, 'r') as csvfile:
        reader = csv.reader(csvfile)

        headers = next(reader)
        book_index = headers.index(BOOK_KEY)

        return sorted({int(verse[book_index]) for verse in reader})

def get_versions_missing_books(bible_versions: [dict]) -> {int: [int]}:
    """
    Some versions might be missing books (once we start web scraping).
    This will return a dictionary where each key is a version id,
    and each value is a list of books which that version is missing

    Arguments:
        bible_versions {[dict]} -- list of bible version objects, as returned by get_bible_versions

    Example return:
        {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
    """
    all_books = set(get_bible_books().keys())

    return { version['id']: sorted(all_books - set(get_books_contained_by_version(version))) for version in bible_versions }

def _print_table(title: str, headers: [str], rows: [int or str]):
    """
    Helper function to print an ASCII table

    Arguments:
        title {str} -- table title
        headers {[str]} -- list of table headers
        rows {[int or str]} -- list of table rows
    """
    table = texttable.Texttable()
    table.header(headers)
    table.add_rows(rows, header = False)

    print(title)
    print(table.draw())

def _print_version_table():
    bible_versions = get_bible_versions()
    missing_books = get_versions_missing_books(bible_versions)

    rows = [(
        version['id'],
        version['abbreviation'],
        version['version'],
        'contains all books' if len(missing_books[version['id']]) == 0 else ', '.join((str(book_id) for book_id in missing_books[version['id']]))
    ) for version in bible_versions]

    _print_table(
        title = "Bible Version Table",
        headers = ['id', 'abbr', 'version', 'missing books'],
        rows = rows
    )

def _print_genre_table():
    genres = get_bible_book_genres()
    book_genres = [book['genre_id'] for book in get_bible_books().values()]

    rows = [(
        genre_id,
        genre,
        book_genres.count(genre_id)
    ) for (genre_id, genre) in sorted(genres.items())]

    _print_table(
        title = "Bible Genre Table",
        headers = ['id', 'name', '# books'],
        rows = rows
    )

def _print_testament_table():
    books = get_bible_books()
    testament_labels = [book['testament'] for book in books.values()]

    rows = [(
        testament_label,
        TESTAMENT_NAMES[testament_label],
        testament_labels.count(testament_label)
    ) for testament_label in sorted(set(testament_labels))]

    _print_table(
        title = "Bible Testament Table",
        headers = ['label', 'name', '# books'],
        rows = rows
    )

def _print_summary_tables():
    _print_version_table()
    print()
    _print_genre_table()
    print()
    _print_testament_table()

if __name__ == '__main__':
    _print_summary_tables()
