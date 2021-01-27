# Standard libraries
import csv
from pathlib import Path
from collections import defaultdict, namedtuple

# Paths
PROJECT_DIRECTORY = Path(__file__).parent
DATA_PATH = PROJECT_DIRECTORY /  'data'
DATA_SPLIT_PATH = DATA_PATH / 'split'
KEY_GENRE_ENGLISH_PATH = DATA_PATH / 'key_genre_english.csv'
KEY_ENGLISH_PATH = DATA_PATH / 'key_english.csv'
TABLE_KEY_PATH = DATA_PATH / 't_key.csv'
TABLE_DIRECTORY = DATA_PATH
TABLE_NAME_FORMAT = '{table}.csv'
SPLIT_DATASET_FORMAT = '{table}_{dataset}.txt'

# CSV header names
BOOK_KEY = 'b'
CHAPTER_KEY = 'c'
VERSE_KEY = 'v'
TEXT_KEY = 't'
TESTAMENT_KEY = 't'
GENRE_KEY = 'g'
NAME_KEY = 'n'
DATASET_KEY = 'dataset'
ID_KEY = 'id'

VerseIdentifier = namedtuple('VerseIdentifier', ['book', 'chaper', 'verse'])

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

def get_bible_verses(bible_version: dict) -> {VerseIdentifier: str}:
	"""
	This returns a dictionary where each key is the verse identifier (namedtuple, see below example),
	and each value is the verse text, for a given bible version.

	Arguments:
		bible_version {dict} -- the bible version object, as returned by get_bible_versions

	Example return:
		{
			VerseIdentifier(book=1, chaper=1, verse=1): 'In the beginning God created the heavens and the earth.',
			VerseIdentifier(book=1, chaper=1, verse=2): 'And the earth was waste and void; and darkness was upon the face of the deep: and the Spirit of God moved upon the face of the waters.',
			...
			VerseIdentifier(book=66, chaper=22, verse=21): 'The grace of the Lord Jesus be with the saints. Amen.'
		}
	"""
	table_path = TABLE_DIRECTORY / TABLE_NAME_FORMAT.format(table = bible_version['table'])

	with open(table_path, 'r', encoding='latin-1') as csvfile:
		reader = csv.reader(csvfile)

		headers = next(reader)
		book_index = headers.index(BOOK_KEY)
		chaper_index = headers.index(CHAPTER_KEY)
		verse_index = headers.index(VERSE_KEY)
		text_index = headers.index(TEXT_KEY)

		return { VerseIdentifier(int(verse[book_index]), int(verse[chaper_index]), int(verse[verse_index])): verse[text_index] for verse in reader }

def get_shared_bible_verses(bible_versions: [dict]) -> {VerseIdentifier: [str]}:
	"""
	Returns the verses that are shared between all the bible versions in
	the argument. The verses are returned as a dict where the key is the verse
	index, and the value is a list of the translations in the same order as
	the bible_versions argument.

	Arguments:
		bible_versions {[dict]} -- list of bible version objects, as returned by get_bible_versions

	Example return:
		{
			VerseIdentifier(book=1, chaper=1, verse=1): [
				'In the beginning God created the heavens and the earth.',
				'At the first God made the heaven and the earth.',
				...
			],
			VerseIdentifier(book=1, chaper=1, verse=2): [
				'And the earth was waste and void; and darkness was upon the face of the deep: and the Spirit of God moved upon the face of the waters.',
				'And the earth was waste and without form; and it was dark on the face of the deep: and the Spirit of God was moving on the face of the waters.',
				...
			],
			...
		}
	"""
	all_verses = defaultdict(list)

	for version in bible_versions:
		for (verse_id, verse) in get_bible_verses(version).items():
			all_verses[verse_id].append(verse)

	return dict(filter(
		lambda kv: len(kv[1]) == len(bible_versions),
		all_verses.items()
	))

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

	with open(table_path, 'r', encoding='latin-1') as csvfile:
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
