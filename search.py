import wx
import os
import random
from threading import Thread

from yandex_music import Client
import settings
import nvda
from player import Player
from sound_device import SoundDevice
import albums
import artists
import playlists
import podcasts
import user
import url_manager

class SearchWindow(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title = title, size = (300,250))
		panel = wx.Panel(self, wx.ID_ANY)
		self.Show(True)

		url_manager.resource = self
		self.mpv = Player()
		self.stream = True
		self.playing_type = ''
		self.selected_track=0
		self.playing_track=0
		self.selected_album=0
		self.selected_artist=0
		self.selected_playlist=0
		self.tracks_page=0
		self.albums_page=0
		self.artists_page=0
		self.playlist_page=0
		self.podcasts_page = 0
		self.podcast_episodes_page = 0
		self.mpv.music.event_callback('end_file')(self.next)
		self.search_cash=os.path.join(settings.cash_folder, 'search.mp3')
		self.search_result= ''
		self.tracks_results = ''
		self.alboms_results=''
		self.artists_results=''
		self.playlists_results=''
		self.podcasts_results = ''
		self.podcast_episodes_results = ''
		self.tracks_list = []

		self.url_type = None
		self.url_track_id = None
		self.url_album_id = None
		self.url_artist_id = None
		self.url_user_uid = None
		self.url_playlist_kind = None

		self.selection_label = wx.StaticText(panel, label='select which list will be shown.')
		self.checksBox = wx.ListCtrl(panel, -1, (0, 0), (10, 20), wx.LC_SINGLE_SEL|wx.LC_REPORT)
		self.checksBox.InsertColumn(0, 'selection')
		self.checksBox.EnableCheckBoxes(True)
		self.checksBox.InsertItem(0, 'tracks')
		self.checksBox.InsertItem(1, 'albums')
		self.checksBox.InsertItem(2, 'artists')
		self.checksBox.InsertItem(3, 'playlists')
		self.checksBox.InsertItem(4, 'podcasts')
		self.checksBox.InsertItem(5, 'podcast_episodes')

		self.text_label = wx.StaticText(panel, label='search')
		self.search_text = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
		self.search_text.SetFocus()
		self.search_text.Bind(wx.EVT_TEXT_ENTER, self.onSearch)
		btn = wx.Button(panel, label="Search")
		btn.Bind(wx.EVT_BUTTON, self.onSearch)
		close_btn = wx.Button(panel, label="Close")
		close_btn.Bind(wx.EVT_BUTTON, self.onClose)

		self.tracks_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.tracks_label = wx.StaticText(panel, label='tracks')
		self.trecks = wx.ListCtrl(panel, -1, (20, 20), (80, 120), wx.LC_SINGLE_SEL|wx.LC_REPORT)
		self.tracks_sizer.Add(self.tracks_label, 0, wx.ALL, 5)
		self.tracks_sizer.Add(self.trecks, 0, wx.ALL, 5)
		self.tracks_sizer.ShowItems(False)

		self.albums_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.albums_label = wx.StaticText(panel, label='albums')
		self.alboms = wx.ListCtrl(panel, -1, (20, 20), (80, 120), wx.LC_SINGLE_SEL|wx.LC_REPORT)
		self.albums_sizer.Add(self.alboms, 0, wx.ALL, 5)
		self.albums_sizer.ShowItems(False)

		self.artists_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.artists_label = wx.StaticText(panel, label='artists')
		self.artists = wx.ListCtrl(panel, -1, (160, 210), (210, 290), wx.LC_SINGLE_SEL|wx.LC_REPORT)
		self.artists_sizer.Add(self.artists, 0, wx.ALL, 5)
		self.artists_sizer.ShowItems(False)

		self.playlists_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.playlistss_label = wx.StaticText(panel, label='playlists')
		self.playlists = wx.ListCtrl(panel, -1, (160, 210), (210, 290), wx.LC_SINGLE_SEL|wx.LC_REPORT)
		self.playlists_sizer.Add(self.playlists, 0, wx.ALL, 5)
		self.playlists_sizer.ShowItems(False)

		self.podcasts_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.podcasts_label = wx.StaticText(panel, label='podcasts')
		self.podcasts = wx.ListCtrl(panel, -1, (160, 210), (210, 290), wx.LC_SINGLE_SEL|wx.LC_REPORT)
		self.podcasts_sizer.Add(self.podcasts, 0, wx.ALL, 5)
		self.podcasts_sizer.ShowItems(False)

		self.podcast_episodes_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.podcast_episodes_label = wx.StaticText(panel, label='podcast episodes')
		self.podcast_episodes = wx.ListCtrl(panel, -1, (160, 210), (210, 290), wx.LC_SINGLE_SEL|wx.LC_REPORT)
		self.podcast_episodes_sizer.Add(self.podcast_episodes, 0, wx.ALL, 5)
		self.podcast_episodes_sizer.ShowItems(False)

		self.devices = []
		self.index_dev = 0
		self.devices_label = wx.StaticText(panel, label='output devices')
		self.list_devices = wx.ListCtrl(panel, -1, (40, 40), (140, 200), wx.LC_REPORT|wx.LC_SINGLE_SEL)
		self.list_devices.InsertColumn(0, 'devices')
		for device in self.mpv.music.audio_device_list:
			self.devices.append(SoundDevice(device["description"], device["name"]))

		for device in self.devices:
			self.list_devices.InsertItem(self.index_dev, device.name)
			self.index_dev += 1

		self.trecks.InsertColumn(0, 'tracks')
		self.alboms.InsertColumn(0, 'albums')
		self.artists.InsertColumn(0, 'artists')
		self.playlists.InsertColumn(0, 'playlists')
		self.podcasts.InsertColumn(0, 'podcasts')
		self.podcast_episodes.InsertColumn(0, 'podcast episodes')

		self.Bind(wx.EVT_CLOSE, self.onClose)

		self.trecks.Bind(wx.EVT_CHAR, self.onKeyPressTrecks)
		self.trecks.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelectTracks, id=wx.ID_ANY)
		self.trecks.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate_track, id=wx.ID_ANY)

		self.alboms.Bind(wx.EVT_CHAR, self.onKeyPressAlbums)
		self.alboms.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelectAlbums, id=wx.ID_ANY)
		self.alboms.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate_album, id=wx.ID_ANY)

		self.artists.Bind(wx.EVT_CHAR, self.onKeyPressArtists)
		self.artists.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelectArtists, id=wx.ID_ANY)
		self.artists.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate_artists, id=wx.ID_ANY)

		self.playlists.Bind(wx.EVT_CHAR, self.onKeyPressPlaylists)
		self.playlists.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelectPlaylists, id=wx.ID_ANY)
		self.playlists.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate_playlists, id=wx.ID_ANY)

		self.podcasts.Bind(wx.EVT_CHAR, self.onKeyPressPodcasts)
		self.podcasts.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelectPodcasts, id=wx.ID_ANY)
		self.podcasts.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate_podcast, id=wx.ID_ANY)

		self.podcast_episodes.Bind(wx.EVT_CHAR, self.onKeyPressPodcast_episodes)
		self.podcast_episodes.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelectPodcast_episodes, id=wx.ID_ANY)
		self.podcast_episodes.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate_podcast_episode, id=wx.ID_ANY)

		self.checksBox.Bind(wx.EVT_LIST_ITEM_CHECKED, self.on_check, id=wx.ID_ANY)
		self.checksBox.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.on_check, id=wx.ID_ANY)

		self.list_devices.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_devices_activated)

	def onClose(self, e):
		self.mpv.music.terminate()
		childrens = self.GetChildren()
		for children in childrens:
			if children.Name == 'panel':
				continue
			children.onClose(wx.CloseEvent)
		self.Destroy()

	def on_devices_activated(self, e):
		self.mpv.music.audio_device = self.devices[self.list_devices.GetFocusedItem()].id

	def on_check(self, e):
		if self.checksBox.IsItemChecked(0) == True:
			self.tracks_sizer.ShowItems(True)
		else:
			self.tracks_sizer.ShowItems(False)
		if self.checksBox.IsItemChecked(1) == True:
			self.albums_sizer.ShowItems(True)
		else:
			self.albums_sizer.ShowItems(False)
		if self.checksBox.IsItemChecked(2) == True:
			self.artists_sizer.ShowItems(True)
		else:
			self.artists_sizer.ShowItems(False)
		if self.checksBox.IsItemChecked(3) == True:
			self.playlists_sizer.ShowItems(True)
		else:
			self.playlists_sizer.ShowItems(False)
		if self.checksBox.IsItemChecked(4) == True:
			self.podcasts_sizer.ShowItems(True)
		else:
			self.podcasts_sizer.ShowItems(False)
		if self.checksBox.IsItemChecked(5) == True:
			self.podcast_episodes_sizer.ShowItems(True)
		else:
			self.podcast_episodes_sizer.ShowItems(False)

	def onSelectTracks(self, e):
		print(self.trecks.GetFocusedItem())
		self.selected_track=self.trecks.GetFocusedItem()

	def on_activate_track(self, e):
		print(self.tracks_results[self.selected_track].title)
		self.playing_type = 'track'
		self.playing_track=self.selected_track
		if self.stream == False:
			self.tracks_results[self.selected_track].download(self.search_cash)
			self.mpv.play(self.search_cash)
		else:
			self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)

	def onSelectPodcast_episodes(self, e):
		print(self.podcast_episodes.GetFocusedItem())
		self.selected_podcast_episode=self.podcast_episodes.GetFocusedItem()

	def on_activate_podcast_episode(self, e):
		print(self.podcast_episodes_results[self.selected_podcast_episode].title)
		self.playing_type = 'podcast'
		self.playing_podcast_episode=self.selected_podcast_episode
		if self.stream == False:
			self.podcast_episodes_results[self.selected_podcast_episode].download(self.search_cash)
			self.mpv.play(self.search_cash)
		else:
			self.mpv.play(self.podcast_episodes_results[self.selected_podcast_episode].get_download_info(get_direct_links=True)[0].direct_link)

	def onSelectAlbums(self, e):
		print(self.alboms.GetFocusedItem())
		self.selected_album=self.alboms.GetFocusedItem()

	def on_activate_album(self, e):
		print(self.alboms_results[self.selected_album].title)
		Album = albums.Album(parent=self, title=self.alboms_results[self.selected_album].title, album_id=self.alboms_results[self.selected_album].id)
		Album.Show(True)

	def onSelectPodcasts(self, e):
		print(self.podcasts.GetFocusedItem())
		self.selected_podcast=self.podcasts.GetFocusedItem()

	def on_activate_podcast(self, e):
		print(self.podcasts_results[self.selected_podcast].title)
		Podcast = podcasts.Podcast(parent=self, title=self.podcasts_results[self.selected_podcast].title, podcast_id=self.podcasts_results[self.selected_podcast].id)
		Podcast.Show(True)

	def onSelectArtists(self, e):
		print(self.artists.GetFocusedItem())
		self.selected_artist=self.artists.GetFocusedItem()

	def on_activate_artists(self, e):
		print(self.artists_results[self.selected_artist].name)
		artist=artists.Artist(self, title=self.artists_results[self.selected_artist].name, artist_id=self.artists_results[self.selected_artist].id)
		artist.Show(True)

	def onSelectPlaylists(self, e):
		print(self.playlists.GetFocusedItem())
		self.selected_playlist = self.playlists.GetFocusedItem()

	def on_activate_playlists(self, e):
		print(self.playlists_results[self.selected_playlist].title)
		pl=playlists.Playlist(self, title=self.playlists_results[self.selected_playlist].title, user_id=self.playlists_results[self.selected_playlist].uid, kind=self.playlists_results[self.selected_playlist].kind)
		pl.Show(True)

	def onKeyPressAlbums(self, e):
		if e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_L:
			like=False
			for album in settings.client.users_likes_albums():
				if str(album.id) == str(self.alboms_results[self.selected_album].id):
					like=True
					break
			if like==False:
				nvda.say('album liked')
				settings.client.users_likes_albums_add(self.alboms_results[self.selected_album].id)
			elif like==True:
				nvda.say('albumnot liked')
				settings.client.users_likes_albums_remove(self.alboms_results[self.selected_album].id)
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_C:
			url_manager.copy(type='album', id=self.alboms_results[self.selected_album].id)
		elif e.GetKeyCode() == wx.WXK_F1:
			like=False
			for album in settings.client.users_likes_albums():
				if str(self.alboms_results[self.selected_album].id) == str(album.id):
					nvda.say('album is liked')
					like=True
					break
			if like==False:
				nvda.say('album is not liked')
		elif e.GetKeyCode() == wx.WXK_PAGEDOWN:
			self.alboms.DeleteAllItems()
			self.index=0
			self.albums_page+=1
			self.search_result = settings.client.search(text=self.search_text.GetValue(), page=self.albums_page)
			self.alboms_results= self.search_result.albums.results
			for album in self.alboms_results:
				albom_name=[]
				for artist in album.artists:
					albom_name.append(artist.name)
					albom_name.append(',')
				if len(albom_name)>0:
					albom_name.pop()
				else:
					albom_name.append('unnown')
				albom_name.append('-')
				albom_name.append(album.title)
				albom_name.append('-')
				albom_name.append(str(album.likes_count))
				albom_name.append('likes')
				albom_name.append(str(album.year))
				albom_name.append('-')
				albom_name.append(str(album.track_count))
				albom_name.append('tracks')
				albom_name=' '.join(albom_name)
				self.alboms.InsertItem(self.index, albom_name)
				self.index+=1
		elif e.GetKeyCode() == wx.WXK_PAGEUP:
			self.alboms.DeleteAllItems()
			self.index=0
			self.albums_page-=1
			self.search_result = settings.client.search(text=self.search_text.GetValue(), page=self.albums_page)
			self.alboms_results= self.search_result.albums.results
			for album in self.alboms_results:
				albom_name=[]
				for artist in album.artists:
					albom_name.append(artist.name)
					albom_name.append(',')
				if len(albom_name)>0:
					albom_name.pop()
				else:
					albom_name.append('unnown')
				albom_name.append('-')
				albom_name.append(album.title)
				albom_name.append('-')
				albom_name.append(str(album.likes_count))
				albom_name.append('likes')
				albom_name.append(str(album.year))
				albom_name.append('-')
				albom_name.append(str(album.track_count))
				albom_name.append('tracks')
				albom_name=' '.join(albom_name)
				self.alboms.InsertItem(self.index, albom_name)
				self.index+=1
		e.Skip()

	def onKeyPressPodcasts(self, e):
		if e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_L:
			like=False
			for album in settings.client.users_likes_albums():
				if str(album.id) == str(self.podcasts_results[self.selected_podcasts].id):
					like=True
					break
			if like==False:
				nvda.say('podcast liked')
				settings.client.users_likes_albums_add(self.podcasts_results[self.selected_podcast].id)
			elif like==True:
				nvda.say('podcast not liked')
				settings.client.users_likes_albums_remove(self.podcasts_results[self.selected_podcast].id)
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_C:
			url_manager.copy(type='album', id=self.podcasts_results[self.selected_podcast].id)
		elif e.GetKeyCode() == wx.WXK_F1:
			like=False
			for album in settings.client.users_likes_albums():
				if str(self.podcasts_results[self.selected_podcast].id) == str(album.id):
					nvda.say('podcast is liked')
					like=True
					break
			if like==False:
				nvda.say('podcast is not liked')
		elif e.GetKeyCode() == wx.WXK_PAGEDOWN:
			self.podcasts.DeleteAllItems()
			self.index=0
			self.podcasts_page+=1
			self.podcasts_results = settings.client.search(text=self.search_text.GetValue(), page=self.podcasts_page, type_='podcast').podcasts.results
			for album in self.podcasts_results:
				albom_name=[]
				for artist in album.artists:
					albom_name.append(artist.name)
					albom_name.append(',')
				if len(albom_name)>0:
					albom_name.pop()
				else:
					albom_name.append('unnown')
				albom_name.append('-')
				albom_name.append(album.title)
				albom_name.append('-')
				albom_name.append(str(album.year))
				albom_name.append('-')
				albom_name.append(str(album.track_count))
				albom_name.append('episodes')
				albom_name=' '.join(albom_name)
				self.podcasts.InsertItem(self.index, albom_name)
				self.index+=1
		elif e.GetKeyCode() == wx.WXK_PAGEUP:
			self.podcasts.DeleteAllItems()
			self.index=0
			self.podcasts_page-=1
			self.podcasts_results = settings.client.search(text=self.search_text.GetValue(), page=self.podcasts_page, type_='podcast').podcasts.results
			for album in self.podcasts_results:
				albom_name=[]
				for artist in album.artists:
					albom_name.append(artist.name)
					albom_name.append(',')
				if len(albom_name)>0:
					albom_name.pop()
				else:
					albom_name.append('unnown')
				albom_name.append('-')
				albom_name.append(album.title)
				albom_name.append('-')
				albom_name.append(str(album.year))
				albom_name.append('-')
				albom_name.append(str(album.track_count))
				albom_name.append('episodes')
				albom_name=' '.join(albom_name)
				self.podcasts.InsertItem(self.index, albom_name)
				self.index+=1
		e.Skip()

	def onKeyPressArtists(self, e):
		if e.GetKeyCode() == wx.WXK_CONTROL_L:
			like=False
			for artist in settings.client.users_likes_artists():
				if str(artist.artist.id) == str(self.artists_results[self.selected_artist].id):
					like=True
					break
			if like==False:
				nvda.say('artist liked')
				settings.client.users_likes_artists_add(self.artists_results[self.selected_artist].id)
			elif like==True:
				nvda.say('artist not liked')
				settings.client.users_likes_artists_remove(self.artists_results[self.selected_artist].id)
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_C:
			url_manager.copy(type='artist', id=self.artists_results[self.selected_artist].id)
		elif e.GetKeyCode() == wx.WXK_F1:
			like=False
			for artist in settings.client.users_likes_artists():
				if str(self.artists_results[self.selected_artist].id) == str(artist.artist.id):
					nvda.say('artist is liked')
					like=True
					break
			if like==False:
				nvda.say('artist is not liked')
		elif e.GetKeyCode() == wx.WXK_PAGEDOWN:
			self.artists.DeleteAllItems()
			index=0
			self.artists_page+=1
			self.search_result = settings.client.search(text=self.search_text.GetValue(), page=self.artists_page)
			self.artists_results= self.search_result.artists.results
			for artist in self.artists_results:
				artist_name=[]
				artist_name.append(artist.name)
				artist_name.append('-')
				artist_name.append(str(artist.counts.direct_albums))
				artist_name.append('albums')
				artist_name.append('-')
				artist_name.append(str(artist.counts.tracks))
				artist_name.append('tracks')
				artist_name=' '.join(artist_name)
				self.artists.InsertItem(index, artist_name)
			index+=1
		elif e.GetKeyCode() == wx.WXK_PAGEUP:
			self.artists.DeleteAllItems()
			self.artists_page-=1
			index=0
			self.search_result = settings.client.search(text=self.search_text.GetValue(), page=self.artists_page)
			self.artists_results= self.search_result.artists.results
			for artist in self.artists_results:
				artist_name=[]
				artist_name.append(artist.name)
				artist_name.append('-')
				artist_name.append(str(artist.counts.direct_albums))
				artist_name.append('albums')
				artist_name.append('-')
				artist_name.append(str(artist.counts.tracks))
				artist_name.append('tracks')
				artist_name=' '.join(artist_name)
			self.artists.InsertItem(index, artist_name)
			index+=1
		e.Skip()

	def onKeyPressPlaylists(self, e):
		if e.GetKeyCode() == wx.WXK_CONTROL_L:
			like=False
			pl_id=f'{self.playlists_results[self.selected_playlist].kind}:{self.playlists_results[self.selected_playlist].uid}'
			for pl in settings.client.users_likes_playlists():
				if str(f'{pl.playlist.kind}:{pl.playlist.uid}') == str(f'{self.playlists_results[self.selected_playlist].kind}:{self.playlists_results[self.selected_playlist].uid}'):
					like=True
					break
			if like==False:
				nvda.say('playlist liked')
				settings.client.users_likes_playlists_add(playlist_ids=f'{self.playlists_results[self.selected_playlist].uid}:{self.playlists_results[self.selected_playlist].kind}', user_id=settings.client.me.account.uid)
			elif like==True:
				self.playlists_results[self.selected_playlist].dislike()
				nvda.say('playlistnot liked')
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_C:
			url_manager.copy(type='playlist', id=self.playlists_results[self.selected_playlist].kind, id2=self.playlists_results[self.selected_playlist].owner.login)
		elif e.GetKeyCode() == wx.WXK_F1:
			like=False
			pl_id=f'{self.playlists_results[self.selected_playlist].kind}:{self.playlists_results[self.selected_playlist].uid}'
			for pl in settings.client.users_likes_playlists():
				if str(f'{pl.playlist.kind}:{pl.playlist.uid}') == str(f'{self.playlists_results[self.selected_playlist].kind}:{self.playlists_results[self.selected_playlist].uid}'):
					nvda.say('playlist is liked')
					like=True
					break
			if like==False:
				nvda.say('playlist is not liked')
		elif e.GetKeyCode() == wx.WXK_PAGEDOWN:
			self.playlists.DeleteAllItems()
			index=0
			self.playlist_page+=1
			self.search_result = settings.client.search(text=self.search_text.GetValue(), page=self.playlist_page)
			self.playlists_results= self.search_result.playlists.results
			for pl in self.playlists_results:
				pl_name=[]
				pl_name.append(pl.title)
				pl_name.append('-')
				pl_name.append(pl.owner.name)
				pl_name.append('-')
				pl_name.append(str(pl.likes_count))
				pl_name.append('likes')
				pl_name.append('-')
				pl_name.append(str(pl.track_count))
				pl_name.append('tracks')
				pl_name=' '.join(pl_name)
				self.playlists.InsertItem(index, pl_name)
				index+=1
		elif e.GetKeyCode() == wx.WXK_PAGEUP:
			self.playlists.DeleteAllItems()
			index=0
			self.playlist_page-=1
			self.search_result = settings.client.search(text=self.search_text.GetValue(), page=self.playlist_page)
			self.playlists_results= self.search_result.playlists.results
			for pl in self.playlists_results:
				pl_name=[]
				pl_name.append(pl.title)
				pl_name.append('-')
				pl_name.append(pl.owner.name)
				pl_name.append('-')
				pl_name.append(str(pl.likes_count))
				pl_name.append('likes')
				pl_name.append('-')
				pl_name.append(str(pl.track_count))
				pl_name.append('tracks')
				pl_name=' '.join(pl_name)
				self.playlists.InsertItem(index, pl_name)
				index+=1
		e.Skip()

	def onKeyPressTrecks(self, e):
		if e.GetKeyCode() == wx.WXK_ESCAPE:
			self.mpv.pause()
			if self.mpv.music_pause == False:
				self.playing_type = 'track'
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F1:
			self.mpv.change_mode()
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F2:
			self.mpv.change_volume_mode()
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F3:
			self.mpv.change_random_mode()
			index=0
			self.trecks.DeleteAllItems()
			if self.mpv.random_mode== 'random':
				if len(self.tracks_results)>0:
					self.tracks_list = self.tracks_results.copy()
					random.shuffle(self.tracks_results)
				for track in self.tracks_results:
					if track.available == False:
						continue
					track_name= []
					for artist in track.artists:
						track_name.append(artist.name)
						track_name.append(',')
					if len(track_name)>0:
						track_name.pop()
					else:
						track_name.append('unnown')
					track_name.append('-')
					track_name.append(track.title)
					track_name = ' '.join(track_name)
					self.trecks.InsertItem(index, track_name)
					index+=1
			elif self.mpv.random_mode == 'list':
				print(len(self.tracks_list))
				self.tracks_results = self.tracks_list.copy()
				for track in self.tracks_results:
					if track.available == False:
						continue
					track_name= []
					for artist in track.artists:
						track_name.append(artist.name)
						track_name.append(',')
					if len(track_name)>0:
						track_name.pop()
					else:
						track_name.append('unnown')
					track_name.append('-')
					track_name.append(track.title)
					track_name = ' '.join(track_name)
					self.trecks.InsertItem(index, track_name)
					index+=1
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F5:
			if self.stream == True:
				self.stream = False
				nvda.say('.now the music is downloaded to your computer.')
			else:
				self.stream = True
				nvda.say('now the music is played directly.')
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_C:
			url_manager.copy(type='track', id=self.tracks_results[self.selected_track].id, id2=self.tracks_results[self.selected_track].albums[0].id)
		elif e.ShiftDown() == True and e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_L:
			like=False
			for track in settings.client.users_likes_tracks():
				if str(track.id) == str(self.tracks_results[self.playing_track].id):
					like=True
					break
			if like==False:
				nvda.say('track liked')
				settings.client.users_likes_tracks_add(self.tracks_results[self.playing_track].id)
			elif like==True:
				nvda.say('track not liked')
				settings.client.users_likes_tracks_remove(self.tracks_results[self.playing_track].id)
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_D:
			dislike=False
			for track in settings.client.users_dislikes_tracks():
				if str(track.id) == str(self.tracks_results[self.playing_track].id):
					dislike=True
					break
			if dislike==False:
				nvda.say('track disliked')
				settings.client.users_dislikes_tracks_add(self.tracks_results[self.playing_track].id)
				self.next_track()
			elif dislike==True:
				nvda.say('track not disliked')
				settings.client.users_dislikes_tracks_remove(self.tracks_results[self.playing_track].id)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_UP:
			self.mpv.change_volume(+5)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_DOWN:
			self.mpv.change_volume(-5)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_RIGHT:
			self.mpv.seek(2)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_LEFT:
			self.mpv.seek(-2)
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_L:
			like=False
			for track in settings.client.users_likes_tracks():
				if str(track.id) == str(self.tracks_results[self.selected_track].id):
					like=True
					break
			if like==False:
				nvda.say('track liked')
				settings.client.users_likes_tracks_add(self.tracks_results[self.selected_track].id)
			elif like==True:
				nvda.say('track not liked')
				settings.client.users_likes_tracks_remove(self.tracks_results[self.selected_track].id)
		elif e.GetKeyCode() == wx.WXK_F5:
			dislike=False
			for track in settings.client.users_dislikes_tracks():
				if str(self.tracks_results[self.selected_track].id) == str(track.id):
					nvda.say('track is disliked')
					dislike=True
					break
			if dislike==False:
				nvda.say('track is not disliked')
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_SPACE:
			download_all_thread= Thread(target=self.download_all)
			download_all_thread.start()
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_SPACE:
			print(self.trecks.GetItemText(self.selected_track))
			download_name=self.trecks.GetItemText(self.selected_track)
			download_name+='.mp3'
			if "?" in download_name:
				download_name = download_name.replace('?', '')
			if ':' in download_name:
				download_name = download_name.replace(':', '')
			if '*' in download_name:
				download_name = download_name.replace('*', '')
			if '<' in download_name:
				download_name = download_name.replace('<', '')
			if '>' in download_name:
				download_name = download_name.replace('>', '')
			if '/' in download_name:
				download_name = download_name.replace('/', '')
			if '\\' in download_name:
				download_name = download_name.replace('\\', '')
			if '|' in download_name:
				download_name = download_name.replace('|', '')
			if '"' in download_name:
				download_name = download_name.replace('"', '')
			print(download_name)
			download_path=os.path.join(settings.download_path, download_name)
			self.tracks_results[self.selected_track].download(download_path)
			info=[]
			info.append('track : ')
			info.append(download_name)
			info.append('is downloaded')
			info= ' '.join(info)
			wx.MessageBox(info, 'info', wx.OK| wx.ICON_INFORMATION)
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_LEFT:
				self.trecks.Focus(self.playing_track-1)
				self.selected_track=self.trecks.GetFocusedItem()
				print(self.tracks_results[self.selected_track].title)
				self.playing_track=self.selected_track
				if self.stream == False:
					self.tracks_results[self.selected_track].download(self.search_cash)
					self.mpv.play(self.search_cash)
				else:
					self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_RIGHT:
				self.trecks.Focus(self.playing_track+1)
				self.selected_track=self.trecks.GetFocusedItem()
				print(self.tracks_results[self.selected_track].title)
				self.playing_track=self.selected_track
				if self.stream == False:
					self.tracks_results[self.selected_track].download(self.search_cash)
					self.mpv.play(self.search_cash)
				else:
					self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)
		elif e.GetKeyCode() == wx.WXK_F1:
			nvda.say(self.tracks_results[self.playing_track].title)
		elif e.GetKeyCode() == wx.WXK_F2:
			self.mpv.position()
		elif e.GetKeyCode() == wx.WXK_F3:
			self.mpv.volume()
		elif e.GetKeyCode() == wx.WXK_F4:
			like=False
			for track in settings.client.users_likes_tracks():
				if str(self.tracks_results[self.playing_track].id) == str(track.id):
					nvda.say('track is liked')
					like=True
					break
			if like==False:
				nvda.say('track is not liked')
		elif e.GetKeyCode() == wx.WXK_PAGEDOWN:
			self.trecks.DeleteAllItems()
			self.playing_track=0
			index=0
			self.tracks_page+=1
			self.search_result = settings.client.search(text=self.search_text.GetValue(), page=self.tracks_page)
			self.tracks_results= self.search_result.tracks.results
			if self.mpv.random_mode=='random':
				self.tracks_list = self.tracks_results.copy()
				random.shuffle(self.tracks_results)
			for track in self.tracks_results:
				track_name= []
				for artist in track.artists:
					track_name.append(artist.name)
					track_name.append(',')
				if len(track_name)>0:
					track_name.pop()
				else:
					track_name.append('unnown')
				track_name.append('-')
				track_name.append(track.title)
				track_name = ' '.join(track_name)
				self.trecks.InsertItem(index, track_name)
				index+=1
		elif e.GetKeyCode() == wx.WXK_PAGEUP:
			self.trecks.DeleteAllItems()
			self.playing_track=0
			index=0
			self.tracks_page-=1
			self.search_result = settings.client.search(text=self.search_text.GetValue(), page=self.tracks_page)
			self.tracks_results= self.search_result.tracks.results
			if self.mpv.random_mode=='random':
				self.tracks_list = self.tracks_results.copy()
				random.shuffle(self.tracks_results)
			for track in self.tracks_results:
				track_name= []
				for artist in track.artists:
					track_name.append(artist.name)
					track_name.append(',')
				if len(track_name)>0:
					track_name.pop()
				else:
					track_name.append('unnown')
				track_name.append('-')
				track_name.append(track.title)
				track_name = ' '.join(track_name)
				self.trecks.InsertItem(index, track_name)
				index+=1
		e.Skip()

	def onKeyPressPodcast_episodes(self, e):
		if e.GetKeyCode() == wx.WXK_ESCAPE:
			self.mpv.pause()
			if self.mpv.music_pause == False:
				self.playing_type = 'podcast'
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F1:
			self.mpv.change_mode()
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F2:
			self.mpv.change_volume_mode()
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_C:
			url_manager.copy(type='track', id=self.podcast_episodes_results[self.selected_podcast_episode].id, id2=self.podcast_episodes_results[self.selected_podcast_episode].albums[0].id)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F5:
			if self.stream == True:
				self.stream = False
				nvda.say('.now the music is downloaded to your computer.')
			else:
				self.stream = True
				nvda.say('now the music is played directly.')
		elif e.ShiftDown() == True and e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_L:
			like=False
			for track in settings.client.users_likes_tracks():
				if str(track.id) == str(self.podcast_episodes_results[self.playing_podcast_episode].id):
					like=True
					break
			if like==False:
				nvda.say('podcast episode liked')
				settings.client.users_likes_tracks_add(self.podcast_episodes_results[self.playing_podcast_episode].id)
			elif like==True:
				nvda.say('podcast episode not liked')
				settings.client.users_likes_tracks_remove(self.podcast_episodes_results[self.playing_podcast_episode].id)
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_D:
			dislike=False
			for track in settings.client.users_dislikes_tracks():
				if str(track.id) == str(self.podcast_episodes_results[self.playing_podcast_episode].id):
					dislike=True
					break
			if dislike==False:
				nvda.say('podcast episode disliked')
				settings.client.users_dislikes_tracks_add(self.podcast_episodes_results[self.playing_podcast_episode].id)
				self.next_podcast()
			elif dislike==True:
				nvda.say('podcast episode not disliked')
				settings.client.users_dislikes_tracks_remove(self.podcast_episodes_results[self.playing_podcast_episode].id)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_UP:
			self.mpv.change_volume(+5)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_DOWN:
			self.mpv.change_volume(-5)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_RIGHT:
			self.mpv.seek(2)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_LEFT:
			self.mpv.seek(-2)
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_L:
			like=False
			for track in settings.client.users_likes_tracks():
				if str(track.id) == str(self.podcast_episodes_results[self.selected_podcast_episode].id):
					like=True
					break
			if like==False:
				nvda.say('podcast episode liked')
				settings.client.users_likes_tracks_add(self.podcast_episodes_results[self.selected_podcast_episode].id)
			elif like==True:
				nvda.say('podcast episode not liked')
				settings.client.users_likes_tracks_remove(self.podcast_episodes_results[self.selected_podcast_episode].id)
		elif e.GetKeyCode() == wx.WXK_F5:
			dislike=False
			for track in settings.client.users_dislikes_tracks():
				if str(self.podcast_episodes_results[self.selected_podcast_episode].id) == str(track.id):
					nvda.say('podcast episode is disliked')
					dislike=True
					break
			if dislike==False:
				nvda.say('podcast episode is not disliked')
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_SPACE:
			download_all_thread= Thread(target=self.download_all_podcast_episodes)
			download_all_thread.start()
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_SPACE:
			print(self.podcast_episodes.GetItemText(self.selected_podcast_episode))
			download_name=self.podcast_episodes.GetItemText(self.selected_podcast_episode)
			download_name+='.mp3'
			if "?" in download_name:
				download_name = download_name.replace('?', '')
			if ':' in download_name:
				download_name = download_name.replace(':', '')
			if '*' in download_name:
				download_name = download_name.replace('*', '')
			if '<' in download_name:
				download_name = download_name.replace('<', '')
			if '>' in download_name:
				download_name = download_name.replace('>', '')
			if '/' in download_name:
				download_name = download_name.replace('/', '')
			if '\\' in download_name:
				download_name = download_name.replace('\\', '')
			if '|' in download_name:
				download_name = download_name.replace('|', '')
			if '"' in download_name:
				download_name = download_name.replace('"', '')
			print(download_name)
			download_path=os.path.join(settings.download_path, download_name)
			self.podcast_episodes_results[self.selected_podcast_episode].download(download_path)
			info=[]
			info.append('podcast episode : ')
			info.append(download_name)
			info.append('is downloaded')
			info= ' '.join(info)
			wx.MessageBox(info, 'info', wx.OK| wx.ICON_INFORMATION)
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_LEFT:
				self.podcast_episodes.Focus(self.playing_podcast_episode-1)
				self.selected_podcast_episode=self.podcast_episodes.GetFocusedItem()
				print(self.podcast_episodes_results[self.selected_podcast_episode].title)
				self.playing_podcast_episode=self.selected_podcast_episode
				if self.stream == False:
					self.podcast_episodes_results[self.selected_podcast_episode].download(self.search_cash)
					self.mpv.play(self.search_cash)
				else:
					self.mpv.play(self.podcast_episodes_results[self.selected_podcast_episode].get_download_info(get_direct_links=True)[0].direct_link)
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_RIGHT:
				self.podcast_episodes.Focus(self.playing_podcast_episode+1)
				self.selected_podcast_episode=self.podcast_episodes.GetFocusedItem()
				print(self.podcast_episodes_results[self.selected_podcast_episode].title)
				self.playing_podcast_episode=self.selected_podcast_episode
				if self.stream == False:
					self.podcast_episodes_results[self.selected_podcast_episode].download(self.search_cash)
					self.mpv.play(self.search_cash)
				else:
					self.mpv.play(self.podcast_episodes_results[self.selected_podcast_episode].get_download_info(get_direct_links=True)[0].direct_link)
		elif e.GetKeyCode() == wx.WXK_F1:
			nvda.say(self.podcast_episodes_results[self.playing_podcast_episode].title)
		elif e.GetKeyCode() == wx.WXK_F2:
			self.mpv.position()
		elif e.GetKeyCode() == wx.WXK_F3:
			self.mpv.volume()
		elif e.GetKeyCode() == wx.WXK_F4:
			like=False
			for track in settings.client.users_likes_tracks():
				if str(self.podcast_episodes_results[self.playing_podcast_episode].id) == str(track.id):
					nvda.say('podcast episode is liked')
					like=True
					break
			if like==False:
				nvda.say('podcast episode is not liked')
		elif e.GetKeyCode() == wx.WXK_PAGEDOWN:
			self.podcast_episodes.DeleteAllItems()
			self.playing_podcast_episode=0
			index=0
			self.podcast_episode_page+=1
			self.podcast_episodes_results = settings.client.search(text=self.search_text.GetValue(), page=self.podcast_episodes_page, type_='podcast_episode').podcast_episodes.results
			for track in self.podcast_episodes_results:
				track_name= []
				for artist in track.artists:
					track_name.append(artist.name)
					track_name.append(',')
				if len(track_name)>0:
					track_name.pop()
				else:
					track_name.append('unnown')
				track_name.append('-')
				track_name.append(track.title)
				track_name = ' '.join(track_name)
				self.podcast_episodes.InsertItem(index, track_name)
				index+=1
		elif e.GetKeyCode() == wx.WXK_PAGEUP:
			self.podcast_episodes.DeleteAllItems()
			self.playing_podcast_episode=0
			index=0
			self.podcast_episodes_page-=1
			self.podcast_episodes_results = settings.client.search(text=self.search_text.GetValue(), page=self.podcast_episodes_page, type_='podcast_episode').podcast_episodes.results
			for track in self.podcast_episodes_results:
				track_name= []
				for artist in track.artists:
					track_name.append(artist.name)
					track_name.append(',')
				if len(track_name)>0:
					track_name.pop()
				else:
					track_name.append('unnown')
				track_name.append('-')
				track_name.append(track.title)
				track_name = ' '.join(track_name)
				self.podcast_episodes.InsertItem(index, track_name)
				index+=1
		e.Skip()

	def onSearch(self, e):
		self.playing_track=0
		self.playing_poe=0
		self.trecks.DeleteAllItems()
		self.alboms.DeleteAllItems()
		self.artists.DeleteAllItems()
		self.playlists.DeleteAllItems()
		self.podcasts.DeleteAllItems()
		self.podcast_episodes.DeleteAllItems()

		index_tre=0
		index_alb=0
		index_art=0
		index_pla=0
		index_pod=0
		index_poe=0

		text = self.search_text.GetValue()
		if 'music.yandex.ru' in text:
			url_manager.parser(text)
			if self.url_type == 'track':
				url_track = settings.client.tracks(self.url_track_id)
				self.tracks_results = url_track
			elif self.url_type == 'album':
				self.alboms_results = settings.client.albums(album_ids=self.url_album_id)
			elif self.url_type == 'artist':
				self.artists_results = settings.client.artists(self.url_artist_id)
			elif self.url_type == 'playlist':
				self.playlists_results = [settings.client.users_playlists(self.url_playlist_kind, self.url_user_uid)]
			elif self.url_type == 'user':
				userwindow = user.User(self, title=self.url_user_uid, user_id=self.url_user_uid)
				userwindow.Show(True)
		else:
			self.search_result = settings.client.search(text=self.search_text.GetValue())
			try:
				self.podcasts_results = settings.client.search(text=self.search_text.GetValue(), type_='podcast').podcasts.results
			except Exception as e:
				print(e)
			try:
				self.podcast_episodes_results = settings.client.search(text=self.search_text.GetValue(), type_='podcast_episode').podcast_episodes.results
			except Exception as e:
				print(e)
			print(self.podcasts_results)
			try:
				self.tracks_results= self.search_result.tracks.results
			except Exception as e:
				print(e)
			try:
				self.alboms_results= self.search_result.albums.results
			except Exception as e:
				print(e)
			try:
				self.artists_results= self.search_result.artists.results
			except Exception as e:
				print(e)
			try:
				self.playlists_results= self.search_result.playlists.results
			except Exception as e:
				print(e)
		url_manager.clear()

		if self.mpv.random_mode=='random':
			self.tracks_list = self.tracks_results.copy()
			random.shuffle(self.tracks_results)
		for track in self.tracks_results:
			if track.available == False:
				continue
			track_name= []
			for artist in track.artists:
				track_name.append(artist.name)
				track_name.append(',')
			if len(track_name)>0:
				track_name.pop()
			else:
				track_name.append('unnown')
			track_name.append('-')
			track_name.append(track.title)
			track_name = ' '.join(track_name)
			self.trecks.InsertItem(index_tre, track_name)
			index_tre+=1

		for poe in self.podcast_episodes_results:
			print(poe.title)
			if poe.available == False:
				continue
			poe_name= []
			for artist in poe.artists:
				poe_name.append(artist.name)
				poe_name.append(',')
			if len(poe_name)>0:
				poe_name.pop()
			else:
				poe_name.append('unnown')
			poe_name.append('-')
			poe_name.append(poe.title)
			poe_name = ' '.join(poe_name)
			self.podcast_episodes.InsertItem(index_poe, poe_name)
			index_poe+=1

		for album in self.alboms_results:
			albom_name=[]
			for artist in album.artists:
				albom_name.append(artist.name)
				albom_name.append(',')
			if len(albom_name)>0:
				albom_name.pop()
			else:
				albom_name.append('unnown')
			albom_name.append('-')
			albom_name.append(album.title)
			albom_name.append('-')
			albom_name.append(str(album.likes_count))
			albom_name.append('likes')
			albom_name.append(str(album.year))
			albom_name.append('-')
			albom_name.append(str(album.track_count))
			albom_name.append('tracks')
			albom_name=' '.join(albom_name)
			self.alboms.InsertItem(index_alb, albom_name)
			index_alb+=1

		for podcast in self.podcasts_results:
			podcast_name=[]
			for artist in podcast.artists:
				podcast_name.append(artist.name)
				podcast_name.append(',')
			if len(podcast_name)>0:
				podcast_name.pop()
			else:
				podcast_name.append('unnown')
			podcast_name.append('-')
			podcast_name.append(podcast.title)
			podcast_name.append('-')
			podcast_name.append(str(podcast.year))
			podcast_name.append('-')
			podcast_name.append(str(podcast.track_count))
			podcast_name.append('episodes')
			podcast_name=' '.join(podcast_name)
			self.podcasts.InsertItem(index_pod, podcast_name)
			index_pod+=1

		for artist in self.artists_results:
			artist_name=[]
			artist_name.append(artist.name)
			artist_name.append('-')
			artist_name.append(str(artist.counts.direct_albums))
			artist_name.append('albums')
			artist_name.append('-')
			artist_name.append(str(artist.counts.tracks))
			artist_name.append('tracks')
			artist_name=' '.join(artist_name)
			self.artists.InsertItem(index_art, artist_name)
			index_art+=1

		for pl in self.playlists_results:
			pl_name=[]
			pl_name.append(pl.title)
			pl_name.append('-')
			pl_name.append(pl.owner.name)
			pl_name.append('-')
			pl_name.append(str(pl.likes_count))
			pl_name.append('likes')
			pl_name.append('-')
			pl_name.append(str(pl.track_count))
			pl_name.append('tracks')
			pl_name=' '.join(pl_name)
			self.playlists.InsertItem(index_pla, pl_name)
			index_pla+=1

	def next(self, event):
		if self.playing_type == 'track':
			if self.mpv.music.idle_active:
				if self.mpv.mode=='track_list':
					self.trecks.Focus(self.playing_track+1)
					self.selected_track=self.trecks.GetFocusedItem()
					print(self.tracks_results[self.selected_track].title)
					self.playing_track=self.selected_track
					if self.stream == False:
						self.tracks_results[self.selected_track].download(self.search_cash)
						self.mpv.play(self.search_cash)
					else:
						self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)
				elif self.mpv.mode=='repeat_track':
					print(self.tracks_results[self.playing_track].title)
					if self.stream == False:
						self.mpv.play(self.search_cash)
					else:
						self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)
		elif self.playing_type == 'podcast':
			if self.mpv.music.idle_active:
				if self.mpv.mode=='track_list':
					self.podcast_episodes.Focus(self.playing_podcast_episode+1)
					self.selected_podcast_episode=self.podcast_episodes.GetFocusedItem()
					print(self.podcast_episodes_results[self.selected_podcast_episode].title)
					self.playing_podcast_episode=self.selected_podcast_episode
					if self.stream == False:
						self.podcast_episodes_results[self.selected_podcast_episode].download(self.search_cash)
						self.mpv.play(self.search_cash)
					else:
						self.mpv.play(self.podcast_episodes_results[self.selected_podcast_episode].get_download_info(get_direct_links=True)[0].direct_link)
				elif self.mpv.mode=='repeat_track':
					print(self.podcast_episodes_results[self.playing_podcast_episode].title)
					if self.stream == False:
						self.mpv.play(self.search_cash)
					else:
						self.mpv.play(self.podcast_episodes_results[self.selected_podcast_episode].get_download_info(get_direct_links=True)[0].direct_link)

	def next_track(self):
		self.trecks.Focus(self.playing_track+1)
		self.selected_track=self.trecks.GetFocusedItem()
		print(self.tracks_results[self.selected_track].title)
		self.playing_track=self.selected_track
		if self.stream == False:
			self.tracks_results[self.selected_track].download(self.search_cash)
			self.mpv.play(self.search_cash)
		else:
			self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)

	def next_podcast_episode(self):
		self.podcast_episodes.Focus(self.playing_podcast_episode+1)
		self.selected_podcast_episode=self.trecks.GetFocusedItem()
		print(self.podcast_episodes_results[self.selected_podcast_episode].title)
		self.playing_podcast_episode=self.selected_podcast_episode
		if self.stream == False:
			self.podcast_episodes_results[self.selected_podcast_episode].download(self.search_cash)
			self.mpv.play(self.search_cash)
		else:
			self.mpv.play(self.podcast_episodes_results[self.selected_podcast_episode].get_download_info(get_direct_links=True)[0].direct_link)

	def download_all(self):
		for track in self.tracks_results:
			track_name= []
			for artist in track.artists:
				track_name.append(artist.name)
				track_name.append(',')
			if len(track_name)>0:
				track_name.pop()
			else:
				track_name.append('unnown')
			track_name.append('-')
			track_name.append(track.title)
			track_name = ' '.join(track_name)
			track_name+='.mp3'
			download_name = track_name
			if "?" in download_name:
				download_name = download_name.replace('?', '')
			if ':' in download_name:
				download_name = download_name.replace(':', '')
			if '*' in download_name:
				download_name = download_name.replace('*', '')
			if '<' in download_name:
				download_name = download_name.replace('<', '')
			if '>' in download_name:
				download_name = download_name.replace('>', '')
			if '/' in download_name:
				download_name = download_name.replace('/', '')
			if '\\' in download_name:
				download_name = download_name.replace('\\', '')
			if '|' in download_name:
				download_name = download_name.replace('|', '')
			if '"' in download_name:
				download_name = download_name.replace('"', '')
			print(download_name)
			download_path=os.path.join(settings.download_path, track_name)
			track.download(download_path)
		wx.MessageBox('all tracks is downloaded', 'info', wx.OK| wx.ICON_INFORMATION)

	def download_all_podcast_episodes(self):
		for track in self.podcast_episodes_results:
			track_name= []
			for artist in track.artists:
				track_name.append(artist.name)
				track_name.append(',')
			if len(track_name)>0:
				track_name.pop()
			else:
				track_name.append('unnown')
			track_name.append('-')
			track_name.append(track.title)
			track_name = ' '.join(track_name)
			track_name+='.mp3'
			download_name = track_name
			if "?" in download_name:
				download_name = download_name.replace('?', '')
			if ':' in download_name:
				download_name = download_name.replace(':', '')
			if '*' in download_name:
				download_name = download_name.replace('*', '')
			if '<' in download_name:
				download_name = download_name.replace('<', '')
			if '>' in download_name:
				download_name = download_name.replace('>', '')
			if '/' in download_name:
				download_name = download_name.replace('/', '')
			if '\\' in download_name:
				download_name = download_name.replace('\\', '')
			if '|' in download_name:
				download_name = download_name.replace('|', '')
			if '"' in download_name:
				download_name = download_name.replace('"', '')
			print(download_name)
			download_path=os.path.join(settings.download_path, track_name)
			track.download(download_path)
		wx.MessageBox('all podcast episodes is downloaded', 'info', wx.OK| wx.ICON_INFORMATION)
