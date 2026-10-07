from urllib.parse import urlparse
import pyperclip

resource = None

def parser(url):
	global resource
	path = urlparse(url).path
	if '/album/' in path and '/track/' in path:
		spath = path.split('/')
		real_id = spath[4] + ':' + spath[2]
		resource.url_type = 'track'
		resource.url_track_id = real_id
	elif '/album/' in path:
		album_id = path.split('/')[2]
		resource.url_type = 'album'
		resource.url_album_id = album_id
	elif '/artist/' in path:
		artist_id = path.split('/')[2]
		resource.url_type = 'artist'
		resource.url_artist_id = artist_id
	elif '/users/' in path and len(path.split('/')) == 5:
		user_uid = path.split('/')[2]
		playlist_kind = path.split('/')[4]
		resource.url_type = 'playlist'
		resource.url_user_uid = user_uid
		resource.url_playlist_kind = playlist_kind
	elif '/users/' in path:
		user_uid = path.split('/')[2]
		resource.url_type = 'user'
		resource.url_user_uid = user_uid

def clear():
	global resource
	resource.url_type = None
	resource.url_track_id = None
	resource.url_album_id = None
	resource.url_artist_id = None
	resource.url_user_uid = None
	resource.url_playlist_kind = None

def copy(type, id, id2=None):
	if type == 'track':
		url = 'https://music.yandex.ru/album/' + str(id2) + '/track/' + str(id)
		pyperclip.copy(url)
	elif type == 'album':
		url = 'https://music.yandex.ru/' + 'album/' + str(id)
		pyperclip.copy(url)
	elif type == 'artist':
		url = 'https://music.yandex.ru/' + 'artist/' + str(id)
		pyperclip.copy(url)
	elif type == 'playlist':
		url = 'https://music.yandex.ru/' + 'users/' + str(id2) + '/playlists/' + str(id)
		pyperclip.copy(url)
	elif type == 'user':
		url = 'https://music.yandex.ru/' + '/users/' + str(id)
		pyperclip.copy(url)
