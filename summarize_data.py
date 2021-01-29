from data_manager import get_bible_versions, get_versions_missing_books, get_bible_book_genres, get_bible_books
from data_manager import TESTAMENT_NAMES

# Additional libraries (pip install ...)
import texttable

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

def _get_genre_dataset_split(genre_id: int, dataset: str) -> int:
    return len(list(filter(lambda book: book['genre_id'] == genre_id and book['dataset'] == dataset, get_bible_books().values())))

def _print_genre_data_split_table():
    genres = get_bible_book_genres()

    rows = [(
        genre,
        f"{_get_genre_dataset_split(genre_id, 'train')} / {_get_genre_dataset_split(genre_id, 'test')}"
    ) for (genre_id, genre) in sorted(genres.items())]

    _print_table(
        title = "Bible Genre Data Split Table",
        headers = ['genre', 'train / test split'],
        rows = rows,
        align = ['l', 'c']
    )

def _get_testament_dataset_split(testament: str, dataset: str) -> int:
    return len(list(filter(lambda book: book['testament'] == testament and book['dataset'] == dataset, get_bible_books().values())))

def _print_testament_data_split_table():
    books = get_bible_books()
    testament_labels = [book['testament'] for book in books.values()]

    rows = [(
        TESTAMENT_NAMES[testament_label],
        f"{_get_testament_dataset_split(testament_label, 'train')} / {_get_testament_dataset_split(testament_label, 'test')}"
    ) for testament_label in sorted(set(testament_labels))]

    _print_table(
        title = "Bible Testament Data Split Table",
        headers = ['testament', 'train / test split'],
        rows = rows,
        align = ['l', 'c']
    )

def _print_summary_tables():
    _print_version_table()
    print()
    _print_genre_table()
    print()
    _print_testament_table()
    print()
    _print_genre_data_split_table()
    print()
    _print_testament_data_split_table()
    print()

if __name__ == '__main__':
    _print_summary_tables()
