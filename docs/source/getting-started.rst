===============
Getting Started
===============


Installation
============


Install *lyricsfandom* package from *PyPi*:

.. code-block:: pycon

    pip install lyricsfandom


Or from *GitHub*:

.. code-block:: pycon

    git clone https://github.com/arthurdjn/scrape-lyricwiki


Usage
=====

You can use the simplified API to look for lyrics and music.

Example:

.. code-block:: python

    from lyricsfandom import LyricWiki

    # Connect to the API
    wiki = LyricWiki()
    # Search for an artist. `LyricsFandom` is not case sensitive.
    artist = wiki.search_artist('london grammar')
    artist


Output:

.. code-block:: pycon

    Artist: London Grammar


Then, you can search for albums too.

Example:

.. code-block:: python

    # Search for an album
    album = wiki.search_album('london grammar', 'if you wait')
    album


Output:

.. code-block:: pycon

    London Grammar: Album "If You Wait" (2013), Songs: 17


Finally, you can scrape for songs.

Example:

.. code-block:: python

    # Search for an album
    song = wiki.search_song('london grammar', 'strong')
    song


Output:

.. code-block:: pycon

    London Grammar: "Strong" from Album "If You Wait" (2013)


...and scrape lyrics.

Example:

.. code-block:: python

    # Search for an album
    lyrics = song.get_lyrics()
    print(lyrics)


Output:

.. code-block:: pycon

    Excuse me for a while
    While I'm wide eyed
    And I'm so damn caught in the middle
    I've excused you for a while
    While I'm wide eyed
    And I'm so down caught in the middle

    And a lion, a lion roars
    Would you not listen?
    If a child, a child cries
    Would you not forgive them?

    [...]


