"""
Generic utility functions not specific to our project
"""

from typing import Callable
from time import time
from pathlib import Path
import requests, re, tarfile

# additional libraries (pip install ...)
from bs4 import BeautifulSoup

def make_tarball(output_filename: Path, source_dir: Path) -> None:
    """
    Generates a tarball (tar.gz) of a source directory at the location "output_filename"

    Arguments:
        output_filename {Path} -- file path of tarball (should include file extension)
        source_dir {Path} -- directory that comprises the tarball

    Returns:
        None
    """
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=source_dir.stem)

def beautify(url: str, parser: str = "html.parser", session: requests.Session or None = None) -> BeautifulSoup or None:
    """
    Returns BeautifulSoup object of url or None

    If timeout occurs, will prompt the user to either re-attempt download or not
    raises RequestException if catastrophic error

    Args:
        url {str} -- path to object
        parser{str} -- parser type, default is html.parser
        session {Session} -- Session is being maintained over connection

    Returns:
        success -- BeautifulSoup
        failure -- None
    """
    while True:
        try:
            response = requests.get(url) if session is None else session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, parser)
        except requests.exceptions.HTTPError as e:
            if prompt_boolean('Timeout Error Occurred: Re-attempt download?', default = True):
                continue
            else:
                return
        except requests.exceptions.RequestException as e:
            raise e

def get_links(document: BeautifulSoup, href_startswith: str) -> [(str, str)]:
    """
    Extracts <a> tags whose href tags begin with "href_startswith" from document. Returns list of tuple containing
    href value and <a> tag text

    Args:
        document {BeautifulSoup} = html document to extract from
        href_startswith {str} -- beginning of url string

    Returns:
        [(str, str)] -- list of (href value, text)
    """
    tags = document.find_all('a', attrs={"href": re.compile(f'^{href_startswith}')})
    return [(a['href'], a.text) for a in tags]

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
