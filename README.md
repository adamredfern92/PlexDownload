# PlexDownload

A quick script to download tv shows and movies from a local Plex server. Useful if you want to quickly get some stuff on a laptop if your traveling.

### Requirements

Requires progressbar

```
	pip install progressbar2
```

### Config

Three variables need to be changed in the config file:
* `plexUrl` - the url to your plex server
* `plexToken` - the authentification [token](https://support.plex.tv/hc/en-us/articles/204059436-Finding-an-authentication-token-X-Plex-Token) for plex
* `libraryPath` - save location for the files

### Usage

``` 
	python PlexDownload.py 
```

Just follow instructions. At anytime type `exit` to quit or `back` to go back a step.

If you have selected a show or a season you can type `all` to download every episode or `unwatched` to just get unwatched.