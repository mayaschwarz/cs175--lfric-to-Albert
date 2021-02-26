from src.paths import *
from src.utils import time_function

# Standard libraries
import csv
from collections import defaultdict, namedtuple
import random, shutil, re
from typing import Callable

# additional libraries (pip install ...)
import contractions

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

VerseIdentifier = namedtuple('VerseIdentifier', ['book', 'chapter', 'verse'])

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

def get_bible_versions_by_file_name(tables: [str]) -> [dict]:
    """
    Returns bible versions by table name (file name).

    Arguments:
        tables: {[str]} -- list of table (file) names

    Returns:
        Same as get_bible_versions
    """
    return list(filter(lambda book: book['table'] in tables, get_bible_versions()))

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

def get_bible_book_id_map() -> {str: int}:
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
    return { book['name'].lower(): book_id for (book_id, book) in get_bible_books().items() }

def get_test_bible_book_ids() -> {int}:
    """
    Pretty simple function that gets the id #s of the test bible books.
    Some bible books are allocated as 'test' books, this creates a list of their IDs.

    Returns:
        {1, 5, 13, 15, 16, 18, 19, 21, 25, 30, 36, 37, 42, 43, 45, 50, 51, 52, 53, 55, 57, 60, 62, 66}
    """
    return {book_id for (book_id, book) in get_bible_books().items() if book['dataset'] == 'test' }

def get_bible_verses(bible_version: dict) -> {VerseIdentifier: str}:
    """
    This returns a dictionary where each key is the verse identifier (namedtuple, see below example),
    and each value is the verse text, for a given bible version.

    Arguments:
        bible_version {dict} -- the bible version object, as returned by get_bible_versions

    Example return:
        {
            VerseIdentifier(book=1, chapter=1, verse=1): 'In the beginning God created the heavens and the earth.',
            VerseIdentifier(book=1, chapter=1, verse=2): 'And the earth was waste and void; and darkness was upon the face of the deep: and the Spirit of God moved upon the face of the waters.',
            ...
            VerseIdentifier(book=66, chapter=22, verse=21): 'The grace of the Lord Jesus be with the saints. Amen.'
        }
    """
    table_path = TABLE_DIRECTORY / TABLE_NAME_FORMAT.format(table = bible_version['table'])

    with open(table_path, 'r', encoding='latin-1') as csvfile:
        reader = csv.reader(csvfile)

        headers = next(reader)
        book_index = headers.index(BOOK_KEY)
        chapter_index = headers.index(CHAPTER_KEY)
        verse_index = headers.index(VERSE_KEY)
        text_index = headers.index(TEXT_KEY)

        return { VerseIdentifier(int(verse[book_index]), int(verse[chapter_index]), int(verse[verse_index])): verse[text_index] for verse in reader }

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
            VerseIdentifier(book=1, chapter=1, verse=1): [
                'In the beginning God created the heavens and the earth.',
                'At the first God made the heaven and the earth.',
                ...
            ],
            VerseIdentifier(book=1, chapter=1, verse=2): [
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

    with open(table_path, 'r', encoding='utf-8') as csvfile:
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

def filter_test_verses(verses: {VerseIdentifier: [str]}) -> ({VerseIdentifier: [str], VerseIdentifier: [str]}):
    """
    Given a dictionary of verses (i.e., the return type of get_shared_bible_verses),
    this splits it up into two dictionaries, one of the non-test verses, and another
    of the test verses. The test versions are determined by belonging to a test book,
    see get_test_bible_book_ids.

    Example return:
        (
            {
                VerseIdentifier(book=2, chapter=1, verse=1): [
                    'Now these are the names of the sons of Israel, who came into Egypt (every man and his household came with Jacob):',
                    'Now these are the names of the sons of Israel who came into Egypt; every man and his family came with Jacob.',
                    ...
                ],
                ...
            },
            {
                VerseIdentifier(book=1, chapter=1, verse=1): [
                    'In the beginning God created the heavens and the earth.',
                    'At the first God made the heaven and the earth.',
                    ...
                ],
                ...
            }
        )
    """
    test_book_ids = get_test_bible_book_ids()

    return dict(filter(lambda kv: kv[0].book not in test_book_ids, verses.items())), \
           dict(filter(lambda kv: kv[0].book in     test_book_ids, verses.items()))

def filter_validation_verses(verses: {VerseIdentifier: [str]}, training_fraction: float) -> ({VerseIdentifier: [str], VerseIdentifier: [str]}):
    """
    Same thing as filter_test_verses, but instead of splitting by book,
    it splits by a random sample of data points based on the training
    fraction. This is used to split the non-test verses into a training
    and a validation set.
    """
    num_training_verses = int(len(verses) * training_fraction)
    training_verse_ids = set(random.sample(list(verses), k = num_training_verses))

    return dict(filter(lambda kv: kv[0] in     training_verse_ids, verses.items())), \
           dict(filter(lambda kv: kv[0] not in training_verse_ids, verses.items()))

def zip_verses(bible_versions: [dict], verses: {VerseIdentifier: [str]}, shuffle: bool) -> {str: [str]}:
    """
    Converts the verse-index based dictionary to a bible-version based dictionary.
    In other words, changed from this:
        {
            VerseIdentifier(...): [
                <bible version 1 translation>,
                <bible version 2 translation>,
                <bible version 3 translation>,
                ...
            ],
            VerseIdentifier(...): [
                <bible version 1 translation>,
                ...
            ],
            ...
        }
    To this:
        {
            <bible 1>: [
                <verse 1 translation>,
                <verse 2 translation>,
                ...
            ],
            <bible 2>: [
                <verse 1 translation>,
                <verse 2 translation>,
            ...
            ],
            ...
        }

    And this function can optionally shuffle all the verses as well.

    Example return:
        {
            't_asv': [
                'In the beginning God created the heavens and the earth.',
                'And the earth was waste and void; and darkness was ...',
                ...
            ],
            't_bbe': [
                'At the first God made the heaven and the earth.',
                'And the earth was waste and without form; and it was dark ...',
                ...
            ],
            't_dby': [
                'In the beginning God created the heavens and the earth.',
                'And the earth was waste and empty, and darkness...',
                ...
            ]
        }
    """
    table_names = [version['table'] for version in bible_versions]

    split_verses = defaultdict(list)

    verse_values = list(verses.values())
    if shuffle:
        random.shuffle(verse_values)

    for verse_texts in verse_values:
        for (table_name, text) in zip(table_names, verse_texts):
            split_verses[table_name].append(text)

    return split_verses

def zip_split_verses(bible_versions: [dict], split_verses: {str: {VerseIdentifier: [str]}}, shuffle: bool) -> {str: {str: [str]}}:
    """
    See zip_verses above.

    Returns:
        {
            'training': <zip_verses output on training data>,
            'validation': <zip_verses output on validation data>,
            'test': <zip_verses output on test data>
        }
    """
    return { dataset: zip_verses(bible_versions, verses, shuffle) for (dataset, verses) in split_verses.items() }

def write_zipped_verses(zipped_verses: {str: {str: [str]}}):
    """
    Writes the contents of a  zipped verses object (zip_split_verses return type)
    to many different files under the new data/split directory (more generally, the
    DATA_SPLIT_PATH directory), deleting the previous directory contents. This way
    there are no artifacts from a previous execution.
    """
    shutil.rmtree(DATA_SPLIT_PATH, ignore_errors = True)
    DATA_SPLIT_PATH.mkdir()

    for (dataset, verse_versions) in zipped_verses.items():
        for (table, verses) in verse_versions.items():
            path = DATA_SPLIT_PATH / SPLIT_DATASET_FORMAT.format(dataset = dataset, table = table)

            with open(path, 'w') as file:
                file.write('\n'.join(verses))

def preprocess_filter_num_words(max_num_words: int, min_num_words: int = 1) -> Callable[[dict], dict]:
    """
    A preprocess function for create_datasets.
    Filters verses where a bible version has too many or too few verses.
    Words are split on whitespace.

    Arguments:
        max_num_words {int} -- maximum number of words per verse

    Keyword Arguments:
        min_num_words {int} -- minimum number of words per verse (default: {1})
    """
    return lambda shared_verses: dict(filter(lambda verse: all((min_num_words <= len(text.split()) <= max_num_words for text in verse[1])), shared_verses.items()))

def preprocess_filter_num_sentences(max_num_sentences: int = 1, min_num_sentences: int = 1) -> Callable[[dict], dict]:
    """
    A preprocess function for create_datasets.
    Filters verses where a bible version has too many or too few sentences.
    Sentences are split on .!? followed by a character.

    Keyword Arguments:
        max_num_sentences {int} -- maximum number of sentences per verse (default: {1})
        min_num_sentences {int} -- minimum number of sentences per verse (default: {1})
    """
    delim = re.compile(r'[.!?].')

    return lambda shared_verses: dict(filter(lambda verse: all((min_num_sentences <= len(re.split(delim, text)) <= max_num_sentences for text in verse[1])), shared_verses.items()))


def preprocess_expand_contractions() -> Callable[[dict], dict]:
    """
    A preprocess function for create_datasets.
    Expands contractions in verses, i.e.:
    Why do you reason that it's because you have no bread? -> Why do you reason that it is because you have no bread?
    Warning: This module (contractions) seems to be a simple regex, picking the most common contraction, so it's not perfect.
    Warning 2: This module doesn't preserve case, if that is important for you.
    """
    return lambda shared_verses: dict(map(lambda verse: (verse[0], [contractions.fix(text) for text in verse[1]]), shared_verses.items()))

def run_preprocess_operations(shared_verses: {VerseIdentifier: [str]}, preprocess_operations: [Callable[[dict], dict]]) -> {VerseIdentifier: [str]}:
    """
    Helper function to run preprocess operations on shared verses
    """
    for preprocess_operation in preprocess_operations:
        shared_verses = preprocess_operation(shared_verses)

    return shared_verses

def create_datasets(bible_versions: [dict], training_fraction: float, shuffle: bool = True, write_files: bool = False, verbose: bool = True, preprocess_operations: [Callable[[dict], dict]] = []) -> {str: {str: [str]}}:
    """
    Creates dataset splits from specific bible versions, and returns the split.
    This should take ~1 second or so to execute. If this is too slow for you,
    or if you prefer not to recreate the datasets every time, consider writing
    the results to files, and then reading from those files using the read_datasets
    function.

    By default prints execution status and details, but that can be disabled with
    through the verbose argument.

    Arguments:
        bible_versions {[dict]} -- list of bible version objects, as returned by get_bible_versions
        training_fraction {float} -- fraction of non-test data to be allocated to training

    Keyword Arguments:
        shuffle {bool} -- [whether to shuffle the verses] (default: {True})
        write_files {bool} -- [whether to write to files] (default: {False})
        verbose {bool} -- [whether to print status and details] (default: {True})

    Example return:
        {
            'training': {
                't_asv': [
                    'Then said Achish unto his servants, Lo, ye see the man is mad; wherefore then have ye brought him to me?',
                    'These things did Benaiah the son of Jehoiada, and had a name among the three mighty men.',
                    ...
                ],
                't_bbe': [
                    'Then Achish said to his servants, Look! the man is clearly off his head; why have you let him come before me?',
                    'These were the acts of Benaiah, the son of Jehoiada, who had a great name among the thirty men of war.',
                    ...
                ],
                ...
            },
            'validation': {
                't_asv': [
                    'These are they who make separations, sensual, having not the Spirit.',
                    'And Abimelech dwelt at Arumah: and Zebul drove out Gaal and his brethren, that they should not dwell in Shechem.',
                    ...
                ],
                ...
            },
            'test': {
                ...
            }
        }
    """
    shared_verses = time_function(f'Finding shared verses between {len(bible_versions)} versions...',
        lambda: get_shared_bible_verses(bible_versions), verbose)

    raw_num_verses = len(shared_verses)

    if raw_num_verses == 0:
        print(f'WARNING: There were no shared verses between the given versions.')
        return { 'training': [], 'validation': [], 'test': [] }

    if len(preprocess_operations) > 0:
        shared_verses = time_function(f'Run preprocess operations...',
            lambda: run_preprocess_operations(shared_verses, preprocess_operations), verbose)

        preprocess_num_verses = len(shared_verses)

        if preprocess_num_verses == 0:
            print(f'WARNING: No verses matched preprocessing criteria.')
            return { 'training': [], 'validation': [], 'test': [] }

    training_verses, test_verses = time_function('Separate test verses...',
        lambda: filter_test_verses(shared_verses), verbose)

    training_verses, validation_verses = time_function('Separate validation verses...',
        lambda: filter_validation_verses(training_verses, training_fraction), verbose)

    split_verses = { 'training': training_verses, 'validation': validation_verses, 'test': test_verses }

    zipped_verses = time_function(f'Zip together verses (shuffle = {shuffle})...',
        lambda: zip_split_verses(bible_versions, split_verses, shuffle), verbose)


    write_files and time_function(f'Store datasets to files...',
            lambda: write_zipped_verses(zipped_verses), verbose)

    verbose and len(preprocess_operations) > 0 and print(f'\n# verses before preprocessing: {raw_num_verses:7,d}\n# verses after  preprocessing: {preprocess_num_verses:7,d} ({preprocess_num_verses / raw_num_verses * 100:.0f}%)\n')

    verbose and print(f'\n# training verses:   {len(training_verses):7,d} ({len(training_verses) / len(shared_verses) * 100:.0f}%)\n# validation verses: {len(validation_verses):7,d} ({len(validation_verses) / len(shared_verses) * 100:.0f}%)\n# test verses:       {len(test_verses):7,d} ({len(test_verses) / len(shared_verses) * 100:.0f}%)')

    return zipped_verses

def load_datasets() ->  {str: {str: [str]}}:
    """
    Loads datasets already created through create_datasets. Takes on the order
    of tenths of seconds. Returns the same object that create_datasets returned.
    """
    zipped_verses = defaultdict(lambda: defaultdict(list))

    for path in DATA_SPLIT_PATH.glob('*.txt'):
        table, dataset = re.match(r'^(.+)_(validation|training|test)$', path.stem).groups()

        with open(path, 'r') as file:
            zipped_verses[dataset][table] = file.read().splitlines()

    return zipped_verses

def get_unique_verses(version1: [str], version2: [str]) -> ((str,), (str,)):
    """
    Given verses of two datasets, returns list of verse pairs with identical verses removed.

    Arguments:
        version1 [str] -- list of bible verses for version1
        version2 [str] -- list of bible verses for version2

    Example return:
        unique_verses(t_bbe, t_kjv)
            ((But Jesus, answering, said, Put up with this, at least. And touching his ear, he made it well., ... ),
            (And Jesus answered and said, Suffer ye thus far. And he touched his ear, and healed him., ...))
    """
    return zip(*((v1, v2) for v1, v2 in zip(version1, version2) if v1 != v2))
