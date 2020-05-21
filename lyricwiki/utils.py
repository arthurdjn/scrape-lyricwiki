"""
Utilities functions.
"""

import re
import urllib
import unidecode

# Global variables to help to process strings / id.
CHARS = [
    ("`", ''),
    ("’", "'"),
    ('”', '"'),
    ('“', '"'),
    ('#', ''),
    ("'D ", "'d "),
    ("'Ll ", "'ll "),
    ("'S ", "'s "),
    ("'T ", "'t "),
    ("'T ", "'t "),
    ("Ww1", "WW1"),
    ("Ww2", "WW2"),
    ("Ww3", "WW3"),
]

LYRICS = [
    ('<i>', ''),
    ('</i>', ''),
    ('\n', ''),
    ('<br/>', '\n'),
]


def capitalize(string):
    """Capitalize a string, even if it is between quotes like ", '.

    Args:
        string (string): text to capitalize.

    Returns:
        string

    """
    return re.sub(r"\b[\w']", lambda m: m.group().capitalize(), string.lower())


def name_to_wiki(name):
    """Process artist, album and song's name.

    Args:
        name:

    Returns:

    """
    name = name.strip()
    name_wiki = ' '.join([name if name == name.upper() else capitalize(name) for name in name.split(' ')])
    for char in CHARS:
        name_wiki = name_wiki.replace(*char)
    return name_wiki


def name_to_wiki_id(name):
    """Generate a ``LyricWiki`` ID from a name.

    Args:
        name (string): name of an artist / song.

    Returns:
        string

    """
    name_wiki = name_to_wiki(name)
    name_wiki_id = '_'.join(name_wiki.split(' '))
    name_wiki_id = urllib.parse.quote(name_wiki_id, safe=':/._-()%,')
    return name_wiki_id


def parse_song_title(song_title, artist_name=None):
    """Split a song title to retrieve the artist name and song name.
    Additional argument can be added to better retrieve these names.

    Args:
        song_title (string): song header (or title for the ``<a>`` element)
        artist_name (string, optional): name of the artist.

    Returns:
        tuple

    """
    song_title = song_title.replace('(page does not exist)', '').strip()
    song_title = song_title.replace('//', '')
    if artist_name and artist_name in song_title:
        # Handles when the artist name is composed of ':' character (ex: 'Ex:Re')
        # Or when the song does (ex: 'Re: Stacks')
        # Knowing the artist name, find the separator index between the artist name and song
        title_parts = song_title.replace('/wiki/', '').split(':')
        artist_name_parts = artist_name.split(':')
        artist_name_nparts = len(artist_name_parts)
        artist_name_song = ':'.join(title_parts[:artist_name_nparts])
        song_name = ':'.join(title_parts[artist_name_nparts:])
    else:
        artist_name_song = song_title.split(':')[0]
        song_name = song_title.split(':')[1]
    return artist_name_song, song_name


def process_lyrics(lyrics):
    """Process lyrics.

    Args:
        lyrics (string): lyrics to tokenize / modify.

    Returns:
        string

    """
    lyrics_new = str(lyrics).split('<div class="lyricbox">')[-1].split('<div class="lyricsbreak">')[0]
    lyrics_new = lyrics_new.split('<b>')[-1].split('</b>')[0]
    lyrics_new = lyrics_new.replace('Instrumental', '')
    lyrics_new = lyrics_new.encode('utf-8', errors='replace').decode("utf-8")
    for char in LYRICS:
        lyrics_new = lyrics_new.replace(*char)

    return lyrics_new


def parse_album_header(album_header):
    """Split the album title in half, to retrieve its name an year.

    Examples::

        >>> album_title = 'His Young Heart (2011)'
        >>> split_album_title(album_title)
            (His Young Heart, 2011)

    Args:
        album_header (string): album header / title to split

    Returns:
        tuple: album name and year.

    """
    album_parts = album_header.split('(')
    if len(album_parts) > 1:
        album_name = '('.join(album_parts[:-1]).strip()
        album_year = album_parts[-1].replace(')', '').strip()
    else:
        album_name = album_header.strip()
        album_year = None

    return album_name, album_year


def split_song_header(song_header):
    """Split the song title in half, to retrieve its artist an name.

    Examples::

        >>> song_header = 'Daughter:Run Lyrics'
        >>> split_song_header(song_header)
            (Daughter, Run)

    Args:
        song_header (string): song header / title to split

    Returns:
        tuple: artist name and song name.

    """
    song_parts = song_header.split(':')
    artist_name = song_parts[0].strip()
    song_name = song_parts[-1].replace(' Lyrics', '').strip()
    return artist_name, song_name


def split_header(header):
    """Split the header to get the artist name, album, and year.

    Examples::

        >>> album_title = 'Daughter:His Young Heart (2011)'
        >>> split_album_title(album_title)
            (Daughter, His Young Heart, 2011)

    Args:
        header (string): album header / title to split

    Returns:
        tuple: album name and year.

    """
    artist_name = header.split(':')[0].strip()
    album_title = header.split(':')[-1].strip()
    album_name, album_year = parse_album_header(album_title)

    return artist_name, album_name, album_year


import unidecode


def serialize_list(list_raw):
    """Serialize a list in ASCII format, so it can be saved as a JSON.

    Args:
        list_raw (list):

    Returns:
        list

    """
    list_serialized = []
    for value in list_raw:
        if isinstance(value, list):
            list_serialized.append(serialize_list(value))
        elif isinstance(value, dict):
            list_serialized.append(serialize_dict(value))
        else:
            list_serialized.append(unidecode.unidecode(str(value)))
    return list_serialized


def serialize_dict(dict_raw):
    """Serialize a dictionary in ASCII format so it can be saved as a JSON.

    Args:
        dict_raw (dict):

    Returns:
        dict

    """
    dict_serialized = {}
    for (key, value) in dict_raw.items():
        if isinstance(value, list):
            dict_serialized[unidecode.unidecode(str(key))] = serialize_list(value)
        elif isinstance(value, dict):
            dict_serialized[unidecode.unidecode(str(key))] = serialize_dict(value)
        else:
            dict_serialized[unidecode.unidecode(str(key))] = unidecode.unidecode(str(value))
    return dict_serialized
