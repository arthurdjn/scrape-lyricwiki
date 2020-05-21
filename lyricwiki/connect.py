"""
A scrapper is used to connect to a website and extract data.
"""

# import libraries
import warnings
import bs4
import urllib.request
import time

# Global variables
SLEEP = 0
VERBOSE = False
USER = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'


def set_sleep(value):
    global SLEEP
    SLEEP = value


def set_verbose(value):
    global VERBOSE
    VERBOSE = value


def set_user(user):
    if user:
        global USER
        USER = user


def connect(url):
    """Connect to an URL.

    Args:
        url (string): url path
        sleep (float): number of seconds to sleep before connection.
        verbose (bool): print the url if ``True``.

    Returns:
        soup

    """
    # Slow down the script to bypass bot detections
    time.sleep(SLEEP)

    # Prevent ERROR: 403 - Forbidden
    # user_agent = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    # user_agent = 'Mozilla/5.0'
    headers = {'User-Agent': USER}

    try:
        req = urllib.request.Request(url, headers=headers)
        page = urllib.request.urlopen(req)
        soup = bs4.BeautifulSoup(page, 'lxml')
        if VERBOSE:
            print(f"Successfully connected to {url}")

    except urllib.error.HTTPError as e:
        warn_msg = f'\n{e}. Failed to connect to {url}.\n' \
                   f'Please verify the spelling or make sure that this page exists. `None` was returned.'
        warnings.warn(warn_msg, RuntimeWarning)
        soup = None

    return soup
