from src.data_manager import get_bible_versions, get_versions_missing_books, get_bible_book_genres, get_bible_books, get_book_mapping
from src.data_manager import TESTAMENT_NAMES

# Additional libraries (pip install ...)
import texttable

DEFAULT_BIBLE_TABLE = 't_kjv'

def _print_table(title: str, headers: [str], rows: [int or str], align: [str] or None = None):
    """
    Helper function to print an ASCII table

    Arguments:
        title {str} -- table title
        headers {[str]} -- list of table headers
        rows {[int or str]} -- list of table rows

    Keyword Arguments:
        align: {[str] or None} -- how to align the columns (default: {None})
    """
    table = texttable.Texttable()
    table.header(headers)
    table.add_rows(rows, header = False)
    align and table.set_cols_align(align)

    print(title)
    print(table.draw())

def print_version_table():
    """
    Prints a table summarizing the different versions of the Bible and their
    available books.
    """
    bible_versions = get_bible_versions()
    missing_books = get_versions_missing_books(bible_versions)

    rows = [(
        version['id'],
        version['abbreviation'],
        version['version'],
        'contains all books' if len(missing_books[version['id']]) == 0 else ', '.join((str(book_id) for book_id in missing_books[version['id']]))
    ) for version in bible_versions]

    _print_table(
        title = 'Bible Version Table',
        headers = ['id', 'abbr', 'version', 'missing books'],
        rows = rows
    )

def _get_num_verses_in_book(book_mapping_book: {int: {int: str}}) -> int:
    return sum(len(chapter) for chapter in book_mapping_book.values())

def print_genre_table(table: str = DEFAULT_BIBLE_TABLE):
    """
    Prints a breakdown of the different bible genres for a given version table name,
    i.e., the number of books and verses each genre has.

    Keyword Arguments:
        table {str} -- the bible version table name (default: {DEFAULT_BIBLE_TABLE})
    """
    books = get_bible_books()
    genres = get_bible_book_genres()
    version = next(filter(lambda v: v['table'] == table, get_bible_versions()))
    book_mapping = get_book_mapping(version)
    books = dict(filter(lambda kv: kv[0] in book_mapping, books.items()))
    book_genres = [book['genre_id'] for (book_id, book) in books.items()]

    rows = [(
        genre_id,
        genre,
        book_genres.count(genre_id),
        f"{sum((_get_num_verses_in_book(book_mapping[book_id]) for (book_id, book) in books.items() if book['genre_id'] == genre_id)):,d}"
    ) for (genre_id, genre) in sorted(genres.items())]

    _print_table(
        title = f"Bible Genre Table – {version['version']}",
        headers = ['id', 'name', '# books', '# verses'],
        rows = rows,
        align = ['l', 'l', 'r', 'r']
    )

def print_testament_table(table: str = DEFAULT_BIBLE_TABLE):
    """
    Prints a breakdown of the different bible testaments for a given version table name,
    i.e., the number of books and verses each testament type (OT vs. NT) has.

    Keyword Arguments:
        table {str} -- the bible version table name (default: {DEFAULT_BIBLE_TABLE})
    """
    books = get_bible_books()
    all_testament_labels = {book['testament'] for book in books.values()}
    version = next(filter(lambda v: v['table'] == table, get_bible_versions()))
    book_mapping = get_book_mapping(version)
    books = dict(filter(lambda kv: kv[0] in book_mapping, books.items()))
    testament_labels = [book['testament'] for (book_id, book) in books.items()]

    rows = [(
        testament_label,
        TESTAMENT_NAMES[testament_label],
        testament_labels.count(testament_label),
        f"{sum((_get_num_verses_in_book(book_mapping[book_id]) for (book_id, book) in books.items() if book['testament'] == testament_label)):,d}"
    ) for testament_label in sorted(all_testament_labels, reverse = True)]

    _print_table(
        title = f"Bible Testament Table – {version['version']}",
        headers = ['label', 'name', '# books', '# verses'],
        rows = rows,
        align = ['l', 'l', 'r', 'r']
    )

def _get_genre_dataset_split(genre_id: int, dataset: str) -> int:
    return len(list(filter(lambda book: book['genre_id'] == genre_id and book['dataset'] == dataset, get_bible_books().values())))

def print_genre_data_split_table():
    """
    Prints a breakdown of the different bible genres training / test split, specifically
    the number of books for each.
    """
    genres = get_bible_book_genres()

    rows = [(
        genre,
        f"{_get_genre_dataset_split(genre_id, 'train')} / {_get_genre_dataset_split(genre_id, 'test')}"
    ) for (genre_id, genre) in sorted(genres.items())]

    _print_table(
        title = 'Bible Genre Data Split Table',
        headers = ['genre', 'train / test split'],
        rows = rows,
        align = ['l', 'c']
    )

def _get_testament_dataset_split(testament: str, dataset: str) -> int:
    return len(list(filter(lambda book: book['testament'] == testament and book['dataset'] == dataset, get_bible_books().values())))

def print_testament_data_split_table():
    """
    Prints a breakdown of the different bible testament training / test split, specifically
    the number of books for each.
    """
    books = get_bible_books()
    testament_labels = [book['testament'] for book in books.values()]

    rows = [(
        TESTAMENT_NAMES[testament_label],
        f"{_get_testament_dataset_split(testament_label, 'train')} / {_get_testament_dataset_split(testament_label, 'test')}"
    ) for testament_label in sorted(set(testament_labels), reverse = True)]

    _print_table(
        title = 'Bible Testament Data Split Table',
        headers = ['testament', 'train / test split'],
        rows = rows,
        align = ['l', 'c']
    )

def _print_summary_tables():
    print_version_table()
    print()
    print_genre_table()
    print()
    print_testament_table()
    print()
    print_genre_data_split_table()
    print()
    print_testament_data_split_table()
    print()

if __name__ == '__main__':
    _print_summary_tables()
