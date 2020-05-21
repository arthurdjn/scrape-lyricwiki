"""
Extract lyrics and songs from ``https://lyrics.fandom.com/`` website.
"""

import warnings
import urllib.parse

from lyricwiki.utils import serialize_dict, serialize_list
from lyricwiki import scrape
from lyricwiki.meta import SongMeta
from .artist import Artist


class Song(SongMeta):
    """Defines a Song from ``https://lyrics.fandom.com/``.

    * :attr:`song_name`: name of the song.

    * :attr:`song_id`: id of the song.

    * :attr:`url`: url of the song.

    """

    def __init__(self, artist_name, song_name, album_name=None, album_type=None, album_year=None):
        super().__init__(artist_name, song_name, album_name=album_name, album_type=album_type, album_year=album_year)

    # TODO: deprecate this
    @classmethod
    def from_url(cls, url):
        # Return nothing if the url is incorrect
        soup = self.connect()
        if soup is None:
            return None

        header = scrape.get_header_from_url(soup=soup)
        artist_name, song_name = split_song_header(header)
        artist = Artist.from_wiki(artist_name)
        return artist.search_song(song_name)

    @classmethod
    def from_artist(cls, artist, song_name):
        """Construct a Song from an artist.

        Args:
            artist (Artist): artist to extract the song from.
            song_name (string): name of the song.

        Returns:
            Song

        """
        for song in artist.songs():
            if name_to_wiki_id(song_name) == song.song_id:
                return song

        warn_msg = f'\nNot Found: No songs named "{song_name}" found in "{artist.artist_name}" playlist. ' \
                   f'`None` was returned.'
        warnings.warn(warn_msg, RuntimeWarning)
        return None

    @classmethod
    def from_album(cls, album, song_name):
        """Construct a Song from an Album.

        Args:
            album (Album): album to extract the song from.
            song_name (string): name of the song.

        Returns:
            Song

        """
        for song in album.songs():
            if name_to_wiki_id(song_name) == song.song_id:
                return song

        warn_msg = f'\nNot Found: No songs named "{song_name}" found in "{album.album_name}" playlist. ' \
                   f'`None` was returned.'
        warnings.warn(warn_msg, RuntimeWarning)
        return None

    def items(self):
        """Iterate through items (usually it's empty).

        Returns:
            None

        """
        yield from self._items

    def get_lyrics(self):
        """Get lyrics from an URL address.

        Returns:
            string

        """
        if not self._lyrics and self.href:
            soup = self.connect()
            if not soup:
                return ''
            self._lyrics = scrape.get_lyrics(soup)
        return self._lyrics

    def to_json(self, encode='ascii'):
        """Encode a song in a JSON format, with full description.

        Args:
            encode (string): format style. Recommended: ``ASCII``.

        Returns:
            dict

        """
        data = {
            'artist': self.artist_name,
            'album': self.album_name,
            'year': self.album_year,
            'song': self.song_name,
            'lyrics': self.get_lyrics(),
            'url': self.url,
            'links': self.get_links(),
        }

        if encode is None:
            return data
        else:
            return serialize_dict(data)
