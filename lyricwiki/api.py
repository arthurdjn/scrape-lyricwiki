"""
API and other classes to connect on Lyrics Wiki.
"""

import warnings
import bs4
import urllib.request
import time
from abc import ABC, abstractmethod

from pyscrape import set_verbose, set_user, set_sleep
from .meta import LyricWikiMeta
from lyricwiki import Artist, Album, Song


class LyricWiki(LyricWikiMeta):
    """Main API for ``Lyric Wiki`` scrapping.

    It basically wraps ``Artist``, ``Album`` and ``Song`` classes.

    """
    def __init__(self, verbose=False, sleep=0, user=None):
        super().__init__()
        self.set_user(user)
        self.set_verbose(verbose)
        self.set_sleep(sleep)

    def set_user(self, user):
        """Change the user agent used to connect on internet.

        Args:
            user (string): user agent to use with urllib.request.

        """
        set_user(user)

    def set_verbose(self, verbose):
        """Change the log / display while surfing on internet.

        Args:
            verbose (bool): if ``True`` will display a log message each time it is connected to a page.

        """
        set_verbose(verbose)

    def set_sleep(self, sleep):
        """Time before connecting again to a new page.

        Args:
            sleep (float): seconds to wait.

        """
        set_sleep(sleep)

    def search_artist(self, artist_name, cover=False, other=False):
        """Search an artist from ``Lyric Wiki`` server.

        Args:
            artist_name (string): name of the artist to get.
            cover (bool): if ``True`` scrape featuring or covers songs.
            other (bool): if ``True`` scrape remixes or compilation albums.

        Returns:
            Artist

        """
        artist = Artist(artist_name)
        artist.get_albums(cover=cover, other=other)
        artist.get_songs(cover=cover, other=other)
        return artist

    def search_album(self, artist_name, album_name):
        """Search an album from ``Lyric Wiki``server.

        Args:
            artist_name (string): name of the artist who made the album.
            album_name (string): name of the album.

        Returns:
            Album

        """
        artist = Artist(artist_name)
        return artist.search_album(album_name)

    def search_song(self, artist_name, song_name):
        """Search a song from ``Lyric Wiki`` server.

        Args:
            artist_name (string): name of the artist who made the song.
            song_name (string): name of the song.

        Returns:

        """
        return Song(artist_name, song_name)

    def search_query(self, query):
        pass