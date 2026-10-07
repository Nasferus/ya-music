from yandex_music import Client
try:
	client = Client.from_credentials('den-dekanov2002', '132daqdaq')
except Exception as e:
	print(e)