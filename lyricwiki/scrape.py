"""
Functions used to connect, extract, and display data from lyrics fandom website.

These functions are used to scrape data from ``HTML`` page connection. They are used inside ``Artist, Album, Song``
classes.

The major part of this functions used a soup parameter, i.e. a ``Beautiful Soup`` ``Tag`` element
on a wab page (usually the whole page, not just a ``<div>`` or other ``HTML`` elements.
"""

import bs4

from pyscrape import connect
from lyricwiki import *


def generate_artist_url(artist_name):
    """Generate a ``LyricWiki`` url of an artist page from its name.

    Args:
        artist_name (string): name of the Artist.

    Returns:
        string

    Examples::
        >>> artist_name = 'london grammar'
        >>> generate_artist_url(artist_name)
            https://lyrics.fandom.com/wiki/London_Grammar

    """
    artist_id = name_to_wiki_id(artist_name)
    return f'https://lyrics.fandom.com/wiki/{artist_id}'


def generate_album_url(artist_name, album_name, album_year):
    """Generate a ``LyricWiki`` url from of an album page from its artist and name / year.

    Args:
        artist_name (string): name of the Artist.
        album_name (string): name of the Album.
        album_year (string): year of an Album.

    Returns:
        string


    Examples::
        >>> artist_name = 'london grammar'
        >>> album_name = 'if you wait'
        >>> album_year = 2013
        >>> generate_album_url(artist_name, album_name, album_year)
            https://lyrics.fandom.com/wiki/London_Grammar:If_You_Wait_(2013)

    """
    artist_id = name_to_wiki_id(artist_name)
    album_id = name_to_wiki_id(album_name)
    return f'https://lyrics.fandom.com/wiki/{artist_id}:{album_id}_({album_year})'


def get_external_links(soup):
    """Retrieve the different links from a ``LyricWiki`` page.
    The links returned can be found in the `External Links` page section,
    and usually references to other platforms (like Last.fm, Amazon, iTunes etc.).

    Args:
        soup (bs4.element.Tag): connection to the ``LyricWiki`` page.

    Returns:
        dict

    Examples::
        >>> # Import packages
        >>> import bs4  # for web scrapping
        >>> import urllib.request  # to connect

        >>> # Set Up: connect to a lyric wiki page
        >>> USER = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        >>> HEADERS = {'User-Agent': USER}
        >>> URL = 'https://lyrics.fandom.com/wiki/London_Grammar:Who_Am_I'
        >>> req = urllib.request.Request(URL, headers=HEADERS)
        >>> page = urllib.request.urlopen(req)
        >>> soup = bs4.BeautifulSoup(page, 'lxml')

        >>> # Retrieve links from the page
        >>> get_external_links(soup)
            {'Amazon': ['https://www.amazon.com/exec/obidos/redirect?link_code=ur2&tag=wikia-20&camp=1789&creative=9325&path=https%3A%2F%2Fwww.amazon.com%2Fdp%2FB00J0QJ84E'],
             'Last.fm': ['https://www.last.fm/music/London+Grammar',
              'https://www.last.fm/music/London+Grammar/If+You+Wait'],
             'iTunes': ['https://itunes.apple.com/us/album/695805771'],
             'AllMusic': ['https://www.allmusic.com/album/mw0002559862'],
             'Discogs': ['http://www.discogs.com/master/595953'],
             'MusicBrainz': ['https://musicbrainz.org/release-group/dbf36a9a-df02-41c4-8fa9-5afe599960b0'],
             'Spotify': ['https://open.spotify.com/album/0YTj3vyjZmlfp16S2XGo50']}

    """
    # Only add links from this set. Other are not relevant.
    links_keys = ['Amazon', 'Last.fm', 'iTunes', 'AllMusic', 'Discogs', 'MusicBrainz', 'Spotify', 'Bandcamp',
                  'Wikipedia', 'Pandora', 'Hype Machine']
    links = {}

    # Scrape links from a page
    for external_tag in scrape_external_links(soup):
        # Get the respective kink / href
        for link_a in external_tag.findAll('a', attrs={'class', 'external text'}):
            # Add it to a dict
            key = external_tag.text.split(':')[0].strip()
            if key in links_keys:
                links.setdefault(key, [])
                links[key].append(link_a.get('href'))
    return links


def scrape_albums(soup):
    """Scrape albums tags, usually from the main artist wiki page.
    This function will successively yield albums.

    .. note::
        The function yield ``<h2>`` tags.

    Args:
        soup (bs4.element.Tag): artist page connection.

    Returns:
        yield bs4.element.Tag: albums tags of an artist page.

    Examples::
        >>> # Import packages
        >>> import bs4  # for web scrapping
        >>> import urllib.request  # to connect

        >>> # Set Up: connect to a lyric wiki page
        >>> USER = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        >>> HEADERS = {'User-Agent': USER}
        >>> URL = 'https://lyrics.fandom.com/wiki/London_Grammar'
        >>> req = urllib.request.Request(URL, headers=HEADERS)
        >>> page = urllib.request.urlopen(req)
        >>> soup = bs4.BeautifulSoup(page, 'lxml')

        >>> # Scrape albums
        >>> for album_tag in scrape_albums(soup):
        ...     print(album_tag.text)
            Strong (2013)
            If You Wait (2013)
            Truth Is a Beautiful Thing (2017)
            Songs on Compilations and Soundtracks
            Additional information
            External links

    """
    yield from soup.select('h2 .mw-headline')


def scrape_songs(album_h2_tag, li_tag='ol'):
    """Scrape songs from an album. This function should be used to scrape on artist's page.
    The optional parameter ``li_tag`` is used to specify whether or not to scrape for released albums (``'ol'`` tags)
    or covers, singles, live etc. (``'ul'`` tags). They can be combined using ``li_tag=['ol', 'ul']``
    to scrape among all songs.

    Args:
        album_h2_tag (bs4.element.Tag): album tag. Only songs under this tag will be yielded.
        li_tag (string or iterable): tags names to scrape songs from.

    Returns:
        yield bs4.element.Tag: yield song tags corresponding to the album tag.

    Examples::
        >>> # Import packages
        >>> import bs4  # for web scrapping
        >>> import urllib.request  # to connect

        >>> # Set Up: connect to a lyric wiki page
        >>> USER = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        >>> HEADERS = {'User-Agent': USER}
        >>> URL = 'https://lyrics.fandom.com/wiki/London_Grammar'
        >>> req = urllib.request.Request(URL, headers=HEADERS)
        >>> page = urllib.request.urlopen(req)
        >>> soup = bs4.BeautifulSoup(page, 'lxml')

        >>> # Scrape songs from the first album,  'Strong (2013)' EP.
        >>> album_h2_tag = soup.select('h2 .mw-headline')[0].parent
        >>> for song_tag in scrape_albums(album_h2_tag):
        ...     print(song_tag.text)
            Strong
            Feelings

        >>> # Scrape all songs from the artist page
        >>> for album_tag in scrape_albums(soup):
        >>>     album_h2_tag = album_tag.parent
        >>>     for song_tag in scrape_songs(album_h2_tag):
        >>>         print(album_h2_tag.text)
        >>>         print(song_tag.text)
        >>>         print('------------')
            Strong (2013)
            Strong
            Feelings
            ------------
            If You Wait (2013)
            Hey Now
            Stay Awake
            Shyer
            Wasting My Young Years
            Sights
            Strong
            etc. ...

    """
    soup = album_h2_tag.next_sibling
    while soup and soup.name != 'h2':
        if soup.name and soup.name in li_tag:
            for song_tag in soup.select('li'):
                yield song_tag.find('a')
        soup = soup.next_sibling


def scrape_external_links(soup):
    external_h2 = soup.select('#External_links')[0].parent
    external_tag = external_h2.next_sibling
    while external_tag and external_tag.name != 'h2':
        if external_tag.name == 'div':
            yield external_tag
        external_tag = external_tag.next_sibling


def get_lyrics(soup):
    """Get lyrics from a ``LyricWiki`` song page.

    Returns:
        string

    Examples::
        >>> # Import packages
        >>> import bs4  # for web scrapping
        >>> import urllib.request  # to connect

        >>> # Set Up: connect to a lyric wiki page
        >>> USER = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        >>> HEADERS = {'User-Agent': USER}
        >>> URL = 'https://lyrics.fandom.com/wiki/London_Grammar:Shyer'
        >>> req = urllib.request.Request(URL, headers=HEADERS)
        >>> page = urllib.request.urlopen(req)
        >>> soup = bs4.BeautifulSoup(page, 'lxml')

        >>> # Scrape the lyrics
        >>> lyrics = get_lyrics(soup)
        >>> print(lyrics)
            I'm feeling shyer and the world gets darker
            Hold yourself a little higher
            Bridge that gap just further
            And all your being
            I'd ask you to give it up
            An ancient feeling love
            So beautifully dressed up

            Feeling shyer, I'm feeling shyer
            I'm feeling shyer

            Maybe you should call her
            Deep in the night for her
            And all your being
            I'd ask you to give it up
            I'd ask you to give it up

    """
    lyrics_container = soup.find("div", {'class': 'lyricbox'})
    lyrics = process_lyrics(str(lyrics_container))
    return lyrics


def get_artist_info(soup):
    """Get additional information about the artist / band.

    Args:
        soup (bs4.element.Tag): connection to a wiki artist page.

    Returns:
        dict

    """
    artist_info_data = {}
    key = 'other'
    artist_info_container = soup.findAll('div', attrs={'class', 'artist-info'})
    for artist_info_table in artist_info_container:
        artist_info_tables = artist_info_table.findAll('div', attrs={'class': 'css-table-cell'})
        for artist_info_cells in artist_info_tables:
            for artist_info_cell in artist_info_cells.children:
                if artist_info_cell.name == 'p':
                    key = artist_info_cell.text.strip().title()
                    key = key[:-1] if key[-1] == ':' else key
                    artist_info_data[key] = None
                elif artist_info_cell.name == 'div':
                    for artist_info_item in artist_info_cell.children:
                        if artist_info_item.name == 'p':
                            artist_info_data[key] = artist_info_item.text.strip()
                        if artist_info_item.name == 'ul':
                            artist_info_data[key] = []
                            artist_info_list = artist_info_item.findAll('a') + artist_info_item.findAll('b')
                            for artist_info_el in artist_info_list:
                                artist_info_data[key].append(artist_info_el.text.strip())
                            artist_info_data[key] = list(set(artist_info_data[key]))

    return artist_info_data
