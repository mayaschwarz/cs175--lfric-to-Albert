# CS 175 Ælfric to Albert

This project utilized Google Colab as the primary development environment.

## Dependencies
Dependencies are included in the requirements.txt folder and the notebooks.
If running on OS other than linux, the package `pyonmttok` will not find a distribution for
`python 3.8` because wheel has yet to be built for it
(see [issue](https://github.com/OpenNMT/Tokenizer/issues/136)).

Your best option is to run the notebooks using Google Colab or a remote Linux environment.
For local development on Windows, we recommend *Window Subsystem for Linux* ([how to install](https://docs.microsoft.com/en-us/windows/wsl/install-win10)).
```bash
pip install -r requirements.txt
```