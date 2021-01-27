from data_manager import DATA_SPLIT_PATH, SPLIT_DATASET_FORMAT
from data_manager import get_bible_versions, get_shared_bible_verses, get_bible_books
from data_manager import VerseIdentifier

from time import time
import random, shutil, re
from collections import defaultdict
from typing import Callable

def prompt_boolean(prompt: str, default: bool) -> bool:
    """
    Prompts the user for a yes/no answer, given a default value.
    It keeps asking until a valid answer is provided. Valid answers include:
    - {blank}  -> returns default
    - {[yY].*} -> returns True
    - {[nN].*} -> returns false

    Arguments:
        prompt {str} -- the prompt to prompt
        default {bool} -- the default value

    Example output:
        Do you want to shuffle the dataset verses? [Y/n] apples

        Invalid response 'apples', must enter yes or no:
        Do you want to shuffle the dataset verses? [Y/n]
    """
    y = 'Y' if default else 'y'
    n = 'n' if default else 'N'
    full_prompt = f'{prompt} [{y}/{n}] '

    while True:
        response = input(full_prompt).lower().strip()

        if not response:
            # no response was given, use default
            return default

        if response[0] == 'y':
            return True
        elif response[0] == 'n':
            return False

        print(f"\nInvalid response '{response}', must enter yes or no:")

def prompt_int(prompt: str, default: int, min_value: int, max_value: int) -> int:
    """
    Similar to prompt boolean, but for an integer value.

    Arguments:
        prompt {str} -- prompt to prompt
        default {int} -- default integer value
        min_value {int} -- minimum allowed value
        max_value {int} -- maximum allowed value

    Returns:
        int -- value chosen

    Example output:
        What percentage of the data ...? [0-100,default=70] 150

        Response must be between 0 to 100
        What percentage of the data ...? [0-100,default=70]
    """
    full_prompt = f'{prompt} [{min_value}-{max_value},default={default}] '

    while True:
        try:
            response = input(full_prompt).strip()

            if not response:
                return default

            response_int = int(response)

            if response_int < min_value or response_int > max_value:
                print(f'\nResponse must be between {min_value} to {max_value}')
            else:
                return response_int

        except Exception:
            print(f"\nInvalid response '{response}', must enter an integer:")

def time_function(message: str, function: Callable[[], object or None], verbose: bool, num_characters: int = 50) -> object or None:
    """
    Pretty simple/sweet helper function that times and prints the
    execution time of another function. Returns whatever the other
    function returned.

    Arguments:
        message {str} -- description of what the function is doing
        function: {Callable[[], object or None]} -- the function to call and time
        verbose {bool} -- whether or not to print anything

    Keyword Arguments:
        num_characters {int} -- number of characters to pad the message to (for aligning) (default: {50})

    Returns:
        object or None -- whatever the function argument returned

    Example output:
        Finding shared verses between 7 versions...        done in 0.961 seconds
    """
    verbose and print(f'{message:{num_characters}}', end = ' ', flush = True)

    start_time = time()
    response = function()
    end_time = time()

    verbose and print(f'done in {end_time - start_time:.3f} seconds')

    return response

def get_test_bible_book_ids() -> {int}:
    """
    Pretty simple function that gets the id #s of the test bible books.
    Some bible books are allocated as 'test' books, this creates a list of their IDs.

    Returns:
        {1, 5, 13, 15, 16, 18, 19, 21, 25, 30, 36, 37, 42, 43, 45, 50, 51, 52, 53, 55, 57, 60, 62, 66}
    """
    return {book_id for (book_id, book) in get_bible_books().items() if book['dataset'] == 'test' }

def filter_test_verses(verses: {VerseIdentifier: [str]}) -> ({VerseIdentifier: [str], VerseIdentifier: [str]}):
    """
    Given a dictionary of verses (i.e., the return type of get_shared_bible_verses),
    this splits it up into two dictionaries, one of the non-test verses, and another
    of the test verses. The test versions are determined by belonging to a test book,
    see get_test_bible_book_ids.

    Example return:
        (
            {
                VerseIdentifier(book=2, chaper=1, verse=1): [
                    'Now these are the names of the sons of Israel, who came into Egypt (every man and his household came with Jacob):',
                    'Now these are the names of the sons of Israel who came into Egypt; every man and his family came with Jacob.',
                    ...
                ],
                ...
            },
            {
                VerseIdentifier(book=1, chaper=1, verse=1): [
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

def create_datasets(bible_versions: [dict], training_fraction: float, shuffle: bool = True, write_files: bool = False, verbose: bool = True) -> {str: {str: [str]}}:
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

    if len(shared_verses) == 0:
        print(f'WARNING: There were no shared verses between the given versions.')
        return { 'training': [], 'validation': [], 'test': [] }

    training_verses, test_verses = time_function('Separate test verses...',
        lambda: filter_test_verses(shared_verses), verbose)

    training_verses, validation_verses = time_function('Separate validation verses...',
        lambda: filter_validation_verses(training_verses, training_fraction), verbose)

    split_verses = { 'training': training_verses, 'validation': validation_verses, 'test': test_verses }

    zipped_verses = time_function(f'Zip together verses (shuffle = {shuffle})...',
        lambda: zip_split_verses(bible_versions, split_verses, shuffle), verbose)

    if write_files:
        time_function(f'Store datasets to files...',
            lambda: write_zipped_verses(zipped_verses), verbose)

    verbose and print(f'\n# Training Verses:   {len(training_verses):7,d} ({len(training_verses) / len(shared_verses) * 100:.0f}%)\n# Validation Verses: {len(validation_verses):7,d} ({len(validation_verses) / len(shared_verses) * 100:.0f}%)\n# Test Verses:       {len(test_verses):7,d} ({len(test_verses) / len(shared_verses) * 100:.0f}%)')

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

def _prompt_create_datasets():
    if DATA_SPLIT_PATH.exists() and not prompt_boolean('Are you sure you want to overwrite your existing dataset split directory?', default = False):
        print('Aborting.')
        exit(0)

    training_fraction = prompt_int(
        'What percentage of the data should be training data (versus validation data)?',
        default = 70,
        min_value = 0,
        max_value = 100) / 100

    shuffle = prompt_boolean('Do you want to shuffle the dataset verses?', default = True)

    print()

    create_datasets(
        bible_versions = get_bible_versions()[:7],
        training_fraction = training_fraction,
        shuffle = shuffle,
        write_files = True,
        verbose = True
    )


if __name__ == '__main__':
    _prompt_create_datasets()
