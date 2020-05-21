"""
Extract lyrics and songs from ``https://lyrics.fandom.com/`` website.

Examples:

    .. code-block:: python

        # 1. Generate an album from scratch
        album = Album('Bon Iver', 'For Emma, Forever Ago')
        # Scrape songs.
        songs = album.get_songs()
        # Be careful as this album was created from scratch it is not linked to any ``Artist`` instance.
        # However, there is still the artist's name saved.
        album.get_artist()  # None
        album.artist_name  # 'Bon Iver'

        # 2. Use an album from an artist
        artist = Artist('Bon Iver')
        album = Album.from_artist(artist, 'For Emmma, Forever Ago')
        album.get_artist()  # Artist: 'Bon Iver'
        # Or search it from the artist class.
        album = artist.search_album('For Emma, Forever Ago')

"""

import warnings

from lyricsfandom.utils import *
from lyricsfandom import scrape
from lyricsfandom.meta import AlbumMeta
from .song import Song
from .artist import Artist


class Album(AlbumMeta):
    """Defines an Album from ``https://lyrics.fandom.com/wiki/``.

    * :attr:`album_name`: album of the artist.

    * :attr:`album_type`: type of album.

    * :attr:`album_year`: released of the album.

    * :attr:`songs`: songs of the album.

    """

    def __init__(self, artist_name, album_name, album_type=None, album_year=None):
        super().__init__(artist_name, album_name, album_type=album_type, album_year=album_year)

    # TODO: deprecate this
    @classmethod
    def from_url(cls, url):
        """Construct an Album from an url.

        Args:
            url (string): url.

        Returns:
            Album

        Examples::
            >>> album = Album.from_url('https://lyrics.fandom.com/wiki/Daughter:His_Young_Heart_(2011)')
            >>> album

        """
        # Return nothing if the connection is incorrect
        pass

    @classmethod
    def from_artist(cls, artist, album_name):
        """Construct an Album from an Artist.

        Args:
            artist (Artist): Artist to extract the album from.
            album_name (string): name of the album.

        Returns:
            Album

        """
        for album in artist.albums():
            if name_to_wiki_id(album_name) == name_to_wiki_id(album.album_name):
                return album

        warn_msg = f'\nNot Found: No albums named "{album_name}" found in "{artist.artist_name}" discography. ' \
                   f'`None` was returned.'
        warnings.warn(warn_msg, RuntimeWarning)
        return None

    def items(self):
        """Connect to ``LyricWiki`` server and scrape songs.

        Returns:
            yield Song

        """
        # TODO: get the album from the album page
        album = Artist(self.artist_name).search_album(self.album_name)
        for song in album.songs():
            song.unregister()
            self.add_song(song)
            yield song

    def add_song(self, song, force=None):
        """Add a song to the album.
        When adding, the song artist's name / album names can be changed to match the parent album,
        using ``force=True``.
        If the provided song is the name of a song (a string), it will automatically create an (empty) song and
        add it to the album.

        Args:
            song (Song or string): song (or song name) to add to the current album.
            force (bool): if ``True``, change the song's ``artist_name, album_name, album_year, album_type``
                attribute to match its parent.

        Examples::
            >>> album = Album('daughter', 'the wild youth')
            >>> song = Song('daughter', 'youth')
            >>> album.add_song(song)
            >>> artist.get_albums()
            >>> album
                Daughter: "The Wild Youth", Songs: 5

        """

        if isinstance(song, Song):
            if name_to_wiki_id(song.album_name) != name_to_wiki_id(self.album_name):
                if force is None:
                    warn_msg = f'\nInvalid Names: Album name from "{song.album_name}" does not match ' \
                               f'parent album {self.album_name}. The song has been added, but you can change ' \
                               f'this behavior by setting the parameter `force=True` to update ' \
                               f'song\'s album information to its parent.'
                    warnings.warn(warn_msg, RuntimeWarning)
                elif force:
                    song.album_name = self.artist_name
                    song.album_type = self.album_type
                    song.album_year = self.album_year

        elif isinstance(song, str):
            song = Song(self.artist_name,
                        song,
                        album_name=self.album_name,
                        album_type=self.album_type,
                        album_year=self.album_year)

        song.register_artist(self.get_artist())
        song.register_album(self)
        self._items.append(song)

    def songs(self):
        """Iterate through all songs within the current album.

        Returns:
            yield Song

        """
        if len(self._items) >= 1:
            yield from self._items
        else:
            yield from self.items()

    def get_songs(self):
        """Get a list of all songs made from an album.

        Returns:
            list

        """
        songs = []
        for song in self.songs():
            songs.append(song)
        return songs

    def search_song(self, song_name):
        """Search a song from an album's playlist.

        Args:
            song_name (string): name of the song to look for

        Returns:
            Song

        """
        for song in self.songs():
            if name_to_wiki_id(song_name) == song.song_id:
                return song

        # WARNING: no song found
        warn_msg = f'\nNot Found: No songs named "{song_name}" found in "{self.album_name}" playlist. ' \
                   f'`None` was returned.'
        warnings.warn(warn_msg, RuntimeWarning)
        return None

    def set_album_type(self):
        """Shortcut to retrieve the type (Single, EP, Album) from an album's playlist."""
        size = len(self._items)
        if size == 1:
            album_type = 'Single'
        elif size < 6:
            album_type = 'EP'
        else:
            album_type = 'Album'
        self.album_type = album_type

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
            'type': self.album_type,
            'year': self.album_year,
            'url': self.url,
            'links': self.get_links(),
            'songs': []
        }
        for song in self.songs():
            data['songs'].append(song.to_json())

        if encode is None:
            return data
        else:
            return serialize_dict(data)

    def __getitem__(self, item):
        return self._items[item]
