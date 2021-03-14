# CS 175 - Ælfric to Albert

Ælfric to Albert is a NLP project that attempts to translate between Modern, Middle, and Old
English using theological texts.
This project utilized Google Colab as the primary development environment.

See `Demo.ipynb` for project showcase.

Table of Contents
=================
  * [Setup](#setup)
  * [Structure](#structure)
  * [Issues](#issues)
  * [Contributing](#contributing)

## Setup
Requires:
- Python >= 3.7

Install package dependencies:
```bash
pip install -r requirements.txt
```

## Structure
Project directory structure.

    .
    ├── data/                 # corpora for training and testing models
    ├── src/                  # project source code
        ├── data_manager.py     # functions to generating train/test split and transformations
        ├── paths.py            # global filepaths for data
        └── utils.py            # utility functions
    ├── character_lstm.py       # character level lstm encoder decoder
    ├── create_datasets.py      # user input wrapper to generate dataset splits
    ├── Demo.ipynb              # Jupyter Notebook showcasing trained models
    ├── modifiedPytorch.ipynb   # word-level lstm encoder decoder
    ├── EncDecRNN.ipynb         # Training notebook for encoder decoder rnn model
    ├── process_corpus.py       # formating raw data into machine-readable format
    ├── requirements.txt        # project dependencies
    ├── summarize_data.py       # summarizes data using texttable
    ├── web_scrape.py           # scrapes online corpora.
    └── README.md

## Issues
If running on OS other than linux, the package `pyonmttok` will not find a distribution for
`python 3.8` because wheel has yet to be built for it
(see [issue](https://github.com/OpenNMT/Tokenizer/issues/136)).

Your best option is to run the notebooks using Google Colab or a remote Linux environment.
For local development on Windows, we recommend *Window Subsystem for Linux* ([how to install](https://docs.microsoft.com/en-us/windows/wsl/install-win10)).

## Contributing
* Ofek Gila
* Darin Kuo
* Maya Schwarz