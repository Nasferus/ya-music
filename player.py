import os

import mpv
import nvda

class Player():
	def __init__(self, file_path=None, volume=50):
		self.file_path = file_path
		self.music = mpv.MPV()
		self.music_pause=False
		self.music.volume=volume
		self.mode='track_list'
		self.random_mode='list'
		self.max_volume=True

	def play(self, file_path):
		self.music_pause=False
		self.music.pause=False
		self.music.play(file_path)

	def pause(self):
		if self.music_pause == True:
			print(self.music_pause)
			self.music_pause=False
			self.music.pause= False
		else:
			print(self.music_pause)
			self.music_pause=True
			self.music.pause=True

	def change_volume(self, volume_step):
		if self.max_volume==False:
			self.music.volume+=volume_step
		elif self.max_volume==True:
			if (self.music.volume >= 100) and (volume_step >0):
				nvda.say('max volume')
			elif (self.music.volume <=0) and (volume_step <0):
				nvda.say('min volume')
			else:
				self.music.volume+=volume_step

	def seek(self, amount):
		self.music.seek(amount)

	def change_mode(self):
		if self.mode=='track_list':
			nvda.say('repeat track')
			self.mode='repeat_track'
		elif self.mode=='repeat_track':
			nvda.say('track list')
			self.mode='track_list'

	def current_position(self):
		result=int(self.music.time_pos//1)
		nvda.say(result)

	def duration(self):
		result=int(self.music.duration//1)
		nvda.say(result)

	def volume(self):
		nvda.say(self.music.volume)

	def position(self):
		list=[]
		list.append(str(int(self.music.time_pos//1)))
		list.append('/')
		list.append(str(int(self.music.duration//1)))
		list = ' '.join(list)
		nvda.say(list)

	def change_volume_mode(self):
		if self.max_volume==True:
			self.max_volume=False
			nvda.say('max volume is now disabled')
		elif self.max_volume==False:
			self.max_volume=True
			nvda.say('max volume is now  100')

	def change_random_mode(self):
		if self.random_mode=='list':
			self.random_mode='random'
			nvda.say('tracks shuffled')
		elif self.random_mode == 'random':
			self.random_mode = 'list'
			nvda.say('tracks restored to default positions')

	def replay(self):
		self.music.request_event(playback_restart)
