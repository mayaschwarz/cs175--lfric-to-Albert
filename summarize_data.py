from data_manager import get_bible_versions, get_versions_missing_books, get_bible_book_genres, get_bible_books
from data_manager import TESTAMENT_NAMES

# Additional libraries (pip install ...)
import texttable

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
		'contains all books' if len(missing_books[version['id']]) == 0 else ', '.join(missing_books[version['id']])
	) for version in bible_versions]

	_print_table(
		title = "Bible Version Table",
		headers = ['id', 'abbr', 'version', 'missing books'],
		rows = rows
	)

def _print_genre_table():
	genres = get_bible_book_genres()
	books = get_bible_books().values()
	datasets = sorted({book['dataset'] for book in books})

	rows = [
		[
			genre_id,
			genre,
			len(list(filter(lambda book: book['genre_id'] == genre_id, books)))
		]
		+
		[
			len(list(filter(lambda book: book['genre_id'] == genre_id and book['dataset'] == dataset, books)))
			for dataset in datasets
		] for (genre_id, genre) in sorted(genres.items())
	]


	_print_table(
		title = "Bible Genre Table",
		headers = ['id', 'name', 'total # books'] + [f'# {dataset} books' for dataset in datasets],
		rows = rows
	)

def _print_testament_table():
	books = get_bible_books().values()
	datasets = sorted({book['dataset'] for book in books})
	testament_labels = [book['testament'] for book in books]

	rows = [
		[
			testament_label,
			TESTAMENT_NAMES[testament_label],
			len(list(filter(lambda book: book['testament'] == testament_label, books)))
		]
		+
		[
			len(list(filter(lambda book: book['testament'] == testament_label and book['dataset'] == dataset, books)))
			for dataset in datasets
		] for testament_label in sorted(set(testament_labels))
	]

	_print_table(
		title = "Bible Testament Table",
		headers = ['label', 'name', 'total # books'] + [f'# {dataset} books' for dataset in datasets],
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
