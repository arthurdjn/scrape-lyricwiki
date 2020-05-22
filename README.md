[![](https://img.shields.io/readthedocs/lyricsfandom)](https://lyricsfandom.readthedocs.io/en/latest/index.html)
[![](https://img.shields.io/pypi/v/lyricsfandom)](https://pypi.org/project/lyricsfandom/)
![](https://img.shields.io/pypi/status/lyricsfandom)


# lyricsfandom
Scrape music data from LyricsWiki (https://lyrics.fandom.com). Artists, Albums, Songs can be extracted.

*Project made during a Deep Learning project for music generation using GPT2 model.*


# Installation

Install *lyricsfandom* package from *PyPi*:

```
pip install lyricsfandom
```

Or from *GitHub*:

```
git clone https://github.com/arthurdjn/scrape-lyricwiki
cd scrape-lyricwiki
pip install .
```

# Getting Started

## LyricsFandom API

You can search for ``Artist``, ``Album`` or ``Song`` from the API:

```python
from lyricsfandom import LyricWiki

# Connect to the API
wiki = LyricWiki()

# Search for an artist. `LyricsFandom` is not case sensitive.
artist = wiki.search_artist('london grammar')
# Search for an album
album = wiki.search_album('london grammar', 'if you wait')
# ...Or a song
song = wiki.search_song('london grammar', 'strong')
# And retrieve its lyrics
lyrics = song.get_lyrics()
```

## Structure

The package is divided as follows:

* ArtistMeta
* AlbumMeta, inherits from ArtistMeta
* SongMeta, inherits from AlbumMeta

<p align="center">
<img src="img/lyricsfandom.png" height="600"/>
</p>

## Retrieve data


Once you have one of these objects, you can also access data directly through their methods:

```python
artist = wiki.search_artist('london grammar')
albums = artist.get_albums()
songs = artist.get_songs()

# Idem from an album
album = wiki.search_album('london grammar', 'if you wait')
songs = album.get_songs()
```

In addition, you can retrieve parent objects from children:

```python
artist = wiki.search_artist('london grammar')
song = artist.search_song('strong')

# Access to parent classes
album = song.get_album()
artist = song.get_artist()
```

You can scrape for description, links and other details information:

```python
artist = wiki.search_artist('london grammar')
info = artist.get_info()  # description of the artist (band members, genres, labels etc.)
links = artist.get_links()  # links where to buy the artist's music.
```

## Save and export

You can save data in a JSON format (and encode it to ASCII if you want).

```python
artist = wiki.search_artist('london grammar')
artist_data = artist.to_json(encode='ascii')
# Idem for Album and Song
```

# Efficiency

This package can make a lot of connections while scraping data.
Here is a small comparison of different packages, made on scraping 10 songs from an album.
*pylyrics3* is the fastest to retrieve data, but it only return lyrics on a JSON format (and not OOP).
*lyricsfandom* have similar results, but *lyricsmaster* is 10 times slower.

![img](img/comparison.png)
