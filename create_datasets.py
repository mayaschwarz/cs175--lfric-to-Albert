from src.paths import DATA_SPLIT_PATH
from src.data_manager import create_datasets, get_bible_versions
from src.utils import prompt_boolean, prompt_int

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
