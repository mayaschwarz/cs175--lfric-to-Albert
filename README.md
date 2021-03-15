# CS 175 - Ælfric to Albert

Ælfric to Albert is a NLP project that attempts to translate between Modern, Middle, and Old
English using theological texts.

This project utilizes Google Colaboratory as the primary development environment.

See  [`Demo.ipynb`][demo] for the project showcase, and open it using Google Colaboratory.

Table of Contents
=================
<!-- MarkdownTOC autolink="true" -->

- [Project Structure](#project-structure)
- [Project Overview](#project-overview)
- [Setup](#setup)
- [Known Issues](#known-issues)
- [Contributors](#contributors)

<!-- /MarkdownTOC -->

## Project Structure

    .
    ├── data/                 # corpora for training and testing models
    ├── src/                  # project source code
        ├── data_manager.py     # functions to generating train/test split and transformations
        ├── paths.py            # global file paths for data
        └── utils.py            # utility functions
    ├── character_lstm.py       # character level LSTM encoder decoder
    ├── create_datasets.py      # user input wrapper to generate dataset splits
    ├── Demo.ipynb              # Jupyter Notebook showcasing trained models
    ├── modifiedPytorch.ipynb   # word-level LSTM encoder decoder
    ├── EncDecRNN.ipynb         # Training notebook for encoder decoder RNN model
    ├── process_corpus.py       # formating raw data into machine-readable format
    ├── requirements.txt        # project dependencies
    ├── summarize_data.py       # summarizes data using texttable
    ├── web_scrape.py           # scrapes online corpora
    └── README.md

## Project Overview

The best way to see a quick overview of this project is by following along the [`Demo.ipynb`][demo] notebook on Google Colaboratory or some other Linux machine. This notebook will show you how to use the various data management tools included in this project, and will show you the results of an encoder-decoder model and a transformer model on translating between different Bible versions included in [`data/`][data].

For a very quick summary of the data, run:
```bash
python3 summarize_data.py
```

## Setup
Requires:
- Python >= 3.7

In order to use our data management tools, you need to install the python `contractions` and `texttable` modules, i.e.:

```bash
pip install contractions~=0.0.48, texttable~=1.6.3
```

To run our machine learning notebooks, you will also need to install specific versions of various ML libraries, as found in our `requirements.txt`. This includes `contractions` and `texttable`:

```bash
pip install -r requirements.txt
```

## Known Issues
If running on OS other than Linux, the package `pyonmttok` will not find a distribution for
`python 3.8` because wheel has yet to be built for it
(see [issue](https://github.com/OpenNMT/Tokenizer/issues/136)).

Your best option is to run the notebooks using Google Colab or a Linux environment.
For local development on Windows, we recommend *Windows Subsystem for Linux* ([how to install](https://docs.microsoft.com/en-us/windows/wsl/install-win10)).

## Contributors
* Ofek Gila
* Darin Kuo
* Maya Schwarz

[demo]:Demo.ipynb "project showcase notebook"
[data]:data/ "data directory"
