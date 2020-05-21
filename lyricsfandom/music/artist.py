"""
Defines an artist from ``LyricWiki`` server.
Extract albums and songs from ``https://lyrics.fandom.com/Artist_Name`` page.

Examples::
    >>> # Note that names are not case sensible
    >>> artist = Artist('daughter')
    >>> artist
        Artist: Daughter

    >>> # Get all albums (compilation, covers etc. included)
    >>> artist.get_albums()
        [Daughter: EP "His Young Heart" (2011), Songs: 4,
         Daughter: EP "The Wild Youth" (2011), Songs: 4,
         Daughter: Album "If You Leave" (2013), Songs: 12,
         Daughter: Album "Not To Disappear" (2016), Songs: 11,
         Daughter: Album "Music From Before The Storm" (2017), Songs: 13,
         Daughter: "Songs On Compilations", Songs: 2,
         Daughter: Single "Other Songs", Songs: 1]

    >>> # Only look for albums / singles released by the artist
    >>> artist.get_albums(cover=False, other=False)
        [Daughter: EP "His Young Heart" (2011), Songs: 4,
         Daughter: EP "The Wild Youth" (2011), Songs: 4,
         Daughter: Album "If You Leave" (2013), Songs: 12,
         Daughter: Album "Not To Disappear" (2016), Songs: 11,
         Daughter: Album "Music From Before The Storm" (2017), Songs: 13,
         Daughter: Single "Other Songs", Songs: 1]

    >>> # Idem for get_songs()

     >>> # Look for an album / song from the artist
     >>> song = artist.search_song('candles')
     >>> lyrics = song.get_lyrics()
     >>> print(lyrics)
         That boy, take me away, into the night
        Out of the hum of the street lights and into a forest
        I'll do whatever you say to me in the dark
        Scared I'll be torn apart by a wolf in mask of a familiar name on a birthday card

        Blow out all the candles, blow out all the candles
        "You're too old to be so shy," he says to me so I stay the night
        Just a young heart confusing my mind, but we're both in silence
        Wide-eyed, both in silence
        Wide-eyed, like we're in a crime scene
        etc. ...

    >>> # Retrieve the artist from a song / album object
    >>> song.get_artist()
        Artist: Daughter

    >>> # Get additional information from the artist
    >>> artist.get_info()
        {'Years Active': '2010 - present',
         'Band Members': ['Elena Tonra', 'Igor Haefeli', 'Remi Aguilella'],
         'Genres': ['Indie Folk', 'Folk Rock'],
         'Record Labels': ['4AD']}

     >>> # Get merchandise links
     >>> artist.get_links()
        {'Amazon': ['https://www.amazon.com/exec/obidos/redirect?link_code=ur2&tag=wikia-20&camp=1789&creative=9325&path=https%3A%2F%2Fwww.amazon.com%2F-%2Fe%2FB001LHN42M'],
         'iTunes': ['https://itunes.apple.com/us/artist/469701923'],
         'AllMusic': ['https://www.allmusic.com/artist/mn0003013627'],
         'Discogs': ['http://www.discogs.com/artist/2218596'],
         'MusicBrainz': ['https://musicbrainz.org/artist/a1ced3e5-476c-4046-bd74-d428f419989b'],
         'Spotify': ['https://open.spotify.com/artist/46CitWgnWrvF9t70C2p1Me'],
         'Bandcamp': ['https://ohdaughter.bandcamp.com/']}

    >>> # Convert the data to JSON
    >>> data = artist.to_json(encode='ascii', nested=False)


These are the most common functions, but others can be used to modify the data.

"""

import warnings
import urllib.parse

from lyricsfandom.utils import *
from lyricsfandom import scrape
from lyricsfandom.meta import ArtistMeta
import lyricsfandom.music as wiki


class Artist(ArtistMeta):
    """Defines an Artist / Band from ``https://lyrics.fandom.com/wiki/``.

    * :attr:`artist_name`: name of the artist.

    * :attr:`base`: base page of Lyric Wiki.

    * :attr:`href`: href link of the artist.

    * :attr:`url`: url page of the artist.

    """

    def __init__(self, artist_name):
        super().__init__(artist_name)
        self._info = None

    def get_info(self):
        """Retrieve additional information of an Artist (like band members, labels, genres etc.).

        Returns:
            dict

        Examples::
            >>> artist = Artist('Daughter')
            >>> artist.get_info()
                {'Years Active': '2010 - present',
                 'Band Members': ['Elena Tonra', 'Igor Haefeli', 'Remi Aguilella'],
                 'Genres': ['Indie Folk', 'Folk Rock'],
                 'Record Labels': ['4AD']}

        """
        if not self._info and self.href:
            info = {}
            soup = self.connect()
            if soup:
                info = scrape.get_artist_info(soup)
            self._info = info
        return self._info

    def set_info(self, value):
        self._info = value

    # TODO: deprecate this
    @classmethod
    def from_url(cls, url):
        """Construct an Artist from an url.

        Args:
            url (string): url.

        Returns:
            Artist

        Examples::
            >>> artist = Artist.from_url('https://lyrics.fandom.com/wiki/Daughter')
            >>> artist
                Artist: Daughter

        """
        # Return nothing if the connection is incorrect
        pass

    def items(self, cover=True, other=True):
        """Connect to ``LyricWiki`` server and scrape albums / songs.
        Keywords arguments can be provided to scrape only from released albums, and reject covers, remix, compilation etc.

        Args:
            cover (bool): if ``True`` scrape featuring or covers songs.
            other (bool): if ``True`` scrape remixes or compilation albums.

        Returns:
            yield Album

        """
        self._items = []
        # Return nothing if the connection is incorrect
        soup = self.connect()
        if not soup:
            return None

        # Scrape songs on different tags.
        # 'ol' --> released albums
        # 'ul' --> compilation
        li_tag = ['ol', 'ul'] if other else 'ol'
        for album_span in scrape.scrape_albums(soup):
            album_title = album_span.text.strip()
            album_name, album_year = parse_album_header(album_title)
            album = wiki.Album(self.artist_name,
                               album_name,
                               album_year=album_year)
            album.register_artist(self)
            album_h2 = album_span.parent

            # Count the number of songs. Will be used to avoid returning empty albums.
            num_songs = 0
            for song_a in scrape.scrape_songs(album_h2, li_tag=li_tag):
                song_title = song_a.get('title').strip()
                # Check if the song was made by the artist or is a featuring / cover
                artist_name_song, song_name = parse_song_title(song_title, artist_name=self.artist_name)
                if not cover and self.artist_name.lower() not in artist_name_song.lower():
                    continue
                song = wiki.Song(artist_name_song,
                                 song_name,
                                 album_name=album_name,
                                 album_year=album_year)
                song.href = song_a.get('href')
                album.add_song(song)
                num_songs += 1

            # Yield only albums that contain songs
            if num_songs > 0:
                if song_a.parent.parent.parent.name == 'ol':
                    album.set_album_type()
                self.add_album(album)
                yield album

    def add_album(self, album, force=None):
        """Add an album to the artist.
        When adding a new argument, the album artist's name can be changed to match the parent artist,
        using ``force=True``.
        If the provided album is the name of an album, it will automatically create an (empty) album and
        add it to the artist.

        Args:
            album (Album or string): album (or album name) to add to the current artist.
            force (bool): if ``True``, change the album's ``artist_name`` attribute to match the artist's name.

        Examples::
            >>> artist = Artist('daughter')
            >>> album = Album('daugghter', 'the wild youth')
            >>> artist.add_album(album)
            >>> artist.get_albums()
                [Daugghter: "The Wild Youth", Songs: 0]

            >>> artist = Artist('daughter')
            >>> album = Album('daugghter', 'the wild youth')
            >>> artist.add_album(album, force=True)
            >>> artist.get_albums()
                [Daughter: "The Wild Youth", Songs: 0]

        """
        if isinstance(album, wiki.Album):
            if name_to_wiki_id(album.artist_name) != name_to_wiki_id(self.artist_name):
                if force is None:
                    warn_msg = f'\nInvalid Name: Artist name from "{album.artist_name}" does not match ' \
                               f'parent artist {self.artist_name}. The album has been added, but you can change ' \
                               f'this behavior by setting the parameter `force=True` to update ' \
                               f'album\'s information to its parent.'
                    warnings.warn(warn_msg, RuntimeWarning)
                elif force:
                    album.artist_name = self.artist_name

            album.register_artist(self)
            self._items.append(album)
        elif isinstance(album, str):
            new_album = wiki.Album(self.artist_name, album)
            new_album.register_artist(self)
            self._items.append(new_album)

    def albums(self, **kwargs):
        """Iterate through all Albums made by the artist.

        Returns:
            yield ALbum

        """
        if len(self._items) >= 1:
            yield from self._items
        else:
            yield from self.items(**kwargs)

    def songs(self, **kwargs):
        """Iterate through all songs made by the artist.

        Returns:
            yield Song

        """
        for album in self.albums(**kwargs):
            for song in album.songs():
                yield song

    def get_albums(self, cover=False, other=False):
        """Get a list of all albums made by the artist.
        Keywords arguments can be provided to scrape only from released albums, and reject covers, remix, compilation etc.

        Args:
            cover (bool): if ``True`` scrape featuring or covers songs.
            other (bool): if ``True`` scrape remixes or compilation albums.

        Returns:
            list

        """
        albums = []
        for album in self.albums(cover=cover, other=other):
            albums.append(album)
        return albums

    def get_songs(self, cover=False, other=False):
        """Get a list of all songs made by the artist.
        Keywords arguments can be provided to scrape only from songs made by the artist, and reject covers etc.

        Args:
            cover (bool): if ``True`` scrape featuring or covers songs.
            other (bool): if ``True`` scrape remixes or compilation albums.

        Returns:
            list

        """
        songs = []
        for song in self.songs():
            songs.append(song)
        return songs

    def search_album(self, album_name):
        """Search an album from an artist's discography.

        Args:
            album_name (string): name of the album to look for.

        Returns:
            Album

        """
        for album in self.albums():
            if name_to_wiki_id(album_name) == name_to_wiki_id(album.album_name):
                return album

        # WARNING: no album found
        warn_msg = f'\nNot Found: No albums named "{album_name}" found in "{artist.artist_name}" discography. ' \
                   f'`None` was returned.'
        warnings.warn(warn_msg, RuntimeWarning)
        return None

    def search_song(self, song_name):
        """Search a song from an artist's playlist.

        Args:
            song_name (string): name of the song to look for

        Returns:
            Song

        """
        for album in self.albums():
            for song in album:
                if name_to_wiki_id(song_name) == name_to_wiki_id(song.song_name):
                    return song

        # WARNING: no song found
        warn_msg = f'\nNot Found: No songs named "{song_name}" found in "{self.artist_name}" discography. ' \
                   f'`None` was returned.'
        warnings.warn(warn_msg, RuntimeWarning)
        return None

    def to_json(self, encode=None):
        """Get the discography of an artist.

        Returns:
            list

        """
        data = {
            'artist': self.artist_name,
            'info': self.get_info(),
            'url': self.url,
            'links': self.get_links(),
            'albums': []
        }
        for album in self.albums():
            data['albums'].append(album.to_json())

        if encode is None:
            return data
        else:
            return serialize_dict(data)
