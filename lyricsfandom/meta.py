"""
Base classes. They are optional and can be removed for simplicity.
However, they provides a better API and sperates Artist / Album / Song in a better way.
"""

from abc import ABC, abstractmethod

from .connect import connect
import lyricsfandom.scrape as F
from .utils import name_to_wiki_id, name_to_wiki


class LyricWikiMeta(ABC):
    """
    The ``LyricWikiMeta`` is an abstract class that all object pointing to `Lyric Wiki` web site should inherits.
    It provide basic set-up to connect and access to `Lyric Wiki` website.

    """

    def __init__(self):
        self.base = f'https://lyrics.fandom.com'
        self.href = '/'

    @property
    def url(self):
        if self.href:
            return self.base + self.href
        return None

    @url.setter
    def url(self, value):
        raise AttributeError('Cannot modify an URL directly. Please modify it through `base` and `href` attributes.')

    def connect(self):
        return connect(self.url)


class ArtistMeta(LyricWikiMeta):
    """Defines an Abstract Artist / Band from ``https://lyrics.fandom.com/wiki/``.

    * :attr:`artist_name`: name of the artist.

    * :attr:`artist_id`: id of the artist.

    * :attr:`base`: base page of the artist.

    * :attr:`href`: href page of the artist.

    * :attr:`url`: url page of the artist.

    """

    def __init__(self, artist_name):
        super().__init__()
        self.artist_name = name_to_wiki(artist_name)
        self.href = f'/wiki/{name_to_wiki_id(self.artist_name)}' if self.artist_name else None
        self._links = None
        self._items = []

    @classmethod
    @abstractmethod
    def from_url(cls, url):
        """Construct an Artist from an url.

        Args:
            url (string): url of the artist page.

        """
        raise NotImplementedError

    def get_links(self):
        """Retrieve merchandise links from a `Lyric Wiki` page.
        If the page (and links) exists, it will save it in a private attribute, to avoid loading again and again
        the same links if the method is called multiple times.

        Returns:
            dict

        """
        if not self._links and self.href:
            soup = self.connect()
            self._links = F.get_external_links(soup)
        return self._links

    def set_links(self, value):
        """Set manually the ``links`` attribute.

        Args:
            value (dict): links to change.

        """
        self._links = value

    def items(self):
        """Basic Set-up to iterate through items (albums, songs...).

        Returns:
            Album or Song

        """
        for item in self._items:
            yield item

    @abstractmethod
    def to_json(self, encode=None):
        """Retrieve the full discography from an artist; in a JSON format.

        Returns:
            dict
        """
        raise NotImplementedError

    def __repr__(self):
        return f"Artist: {self.artist_name}"


class AlbumMeta(ArtistMeta):
    """Defines an Abstract Album from ``https://lyrics.fandom.com/wiki/``.

    * :attr:`album_name`: album of the artist.

    * :attr:`album_type`: type of album.

    * :attr:`album_year`: released of the album.

    """

    def __init__(self, artist_name, album_name, album_year=None, album_type=None):
        super().__init__(artist_name)
        self.album_name = name_to_wiki(album_name) if album_name else ''
        # self.album_id = name_to_wiki_id(self.album_name)
        self.album_year = album_year
        self.album_type = album_type
        href = None
        if self.artist_name and self.album_name and self.album_year:
            href = f'/wiki/{name_to_wiki_id(self.artist_name)}:{name_to_wiki_id(self.album_name)}_({self.album_year})'
        self.href = href
        self._artist = None

    def get_artist(self):
        """Retrieve the artist class linked to the album (if it exists).
        It is usually called when an album has been searched from an ``Artist`` class.
        Then, using this function will point to the same ``Artist`` object.

        Returns:
            Artist

        """
        return self._artist

    def register_artist(self, artist):
        """Manually set the pointer to an ``Artist``.

        Args:
            artist (Artist): artist related to the album.

        """
        self._artist = artist

    def unregister(self):
        """Unlink the album to its artist."""
        self._artist = None

    @classmethod
    @abstractmethod
    def from_url(cls, url):
        """Construct an Album from an url.

        Args:
            url (string): url of the album page.

        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_artist(cls, artist, album_name):
        """Construct an Artist from an url.

        Args:
            artist (Artist): artist to extract the album from.
            album_name (string): album name.

        """
        raise NotImplementedError

    @abstractmethod
    def to_json(self, encode=None):
        """Retrieve the full playlist from an album; in a JSON format.

        Returns:
            dict
        """
        raise NotImplementedError

    def __repr__(self):
        rep_type = f' {self.album_type}' if self.album_type else ''
        rep_year = f' ({self.album_year})' if self.album_year else ''
        rep_songs = f', Songs: {len(self._items)}' if len(self._items) > 0 else ''
        rep = f'{self.artist_name}:{rep_type} "{self.album_name}"{rep_year}' \
              f'{rep_songs}'
        return rep


class SongMeta(AlbumMeta):
    """Defines an Abstract Song from ``https://lyrics.fandom.com/``.

    * :attr:`song_name`: name of the song.

    * :attr:`song_id`: id of the song.

    * :attr:`lyrics`: lyrics of the song.

    """

    def __init__(self, artist_name, song_name, album_name=None, album_year=None, album_type=None):
        super().__init__(artist_name, album_name, album_year=album_year, album_type=album_type)
        self.song_name = name_to_wiki(song_name)
        # self.song_id = name_to_wiki_id(song_name)
        href = None
        if name_to_wiki_id(self.artist_name) and self.song_name:
            href = f"/wiki/{name_to_wiki_id(self.artist_name)}:{name_to_wiki_id(self.song_name)}"
        self.href = href
        self._album = None
        self._lyrics = None

    def set_lyrics(self, value):
        """Manually set the lyrics of the current song.

        Args:
            value (string): new lyrics.

        """
        self._lyrics = value

    def get_album(self):
        """Get the parent album pointing to the song, if it exists.

        Returns:
            Album

        """
        return self._album

    def register_album(self, album):
        """Link the song to a parent album.

        Args:
            album (Album): album to link to the song.

        """
        self._album = album

    def unregister(self):
        """Unlink the song to both artist and album."""
        self._artist = None
        self._album = None

    @classmethod
    @abstractmethod
    def from_url(cls, url):
        """Construct a Song from an url.

        Args:
            url (string): url of the lyrics song page.

        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_album(cls, album, song_name):
        """Construct a Song from an url.

        Args:
            album (Album): album to extract the song from.
            song_name (string): song name.

        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_artist(cls, artist, song_name):
        """Construct an Artist from an url.

        Args:
            artist (Artist): artist to extract the album from.
            song_name (string): song name.

        """
        raise NotImplementedError

    @abstractmethod
    def to_json(self, encode=None):
        """Retrieve the full information / lyrics from a song; in a JSON format.

        Returns:
            dict

        """
        raise NotImplementedError

    def __repr__(self):
        rep_year = f' ({self.album_year})' if self.album_year else ''
        rep_type = f' {self.album_type}' if self.album_type else ''
        rep_album = f', from{rep_type} "{self.album_name}"' if self.album_name else ''
        return f'{self.artist_name}: "{self.song_name}"{rep_album}{rep_year}'
