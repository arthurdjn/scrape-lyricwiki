========
Examples
========

The requests should be made from the API. Then, you can have access to albums, songs, lyrics.


LyricsFandom API
================

.. code-block:: python

    from lyricsfandom import LyricWiki

    # Connect to the API
    wiki = LyricWiki()
    # Search for an artist. `LyricsFandom` is not case sensitive.
    artist = wiki.search_artist('london grammar')
    album = wiki.search_album('london grammar', 'if you wait')
    song = wiki.search_song('london grammar', 'strong')
    lyrics = song.get_lyrics()


You can have access to their attributes with:

.. code-block:: python

    # From an Artist
    artist_name = artist.artist_name

    # From an Album
    artist_name = album.artist_name
    album_name = album.album_name
    album_typz = album.album_typz
    album_year = album.album_year

    # From a Song
    artist_name = song.artist_name
    artist_name = song.artist_name
    album_name = song.album_name
    album_type = song.album_type
    album_year = song.album_year
    song_name = song.song_name



Access data
===========

Once you have an object instance, you can retrieve data:

.. code-block:: python

    # From an Artist
    artist = wiki.search_artist('london grammar')
    albums = artist.get_albums()
    songs = artist.get_songs()

    # From an Album
    album = wiki.search_album('london grammar', 'if you wait')
    songs = album.get_songs()


Note:

If you want to navigate through albums, songs, you may prefer using ``.songs()`` or ``.albums()`` methods,
which yields items successively and thus are more optimized as all items are not loaded at directly.

.. code-block:: python

    # From and Artist
    artist = wiki.search_artist('london grammar')
    for song in artist.songs():
        lyrics = song.get_lyrics()
        print(lyrics)
        print('\n-----\n')


From children classes (Artist --> Album --> Song), you can retrieve data too:

.. code-block:: python

    # From a Song
    song = wiki.search_song('london grammar', 'strong')
    album = song.get_album()
    artist = song.get_artist()

    # From an Album
    album = wiki.search_album('london grammar', 'if you wait')
    artist = album.get_artist()


Save and export
===============

You can save all classes with the ``.to_json()`` method. The ``'ascii'`` argument will transforms all string to
ASCII format. If you don't want it, just remove it.

.. code-block:: python

    # From an Artist
    artist = wiki.search_artist('london grammar')
    artist_data = artist.to_json(encode='ascii')

    # From an Album
    album = wiki.search_album('london grammar', 'if you wait')
    album_data = album.to_json(encode='ascii')

    # From a Song (contains lyrics)
    song = wiki.search_song('london grammar', 'strong')
    song_data = song.to_json(encode='ascii')


