import player
from yandex_music import Client
try:
	client = Client('AQAAAAAOlg9NAAG8Xr6wuV5ukEZ6mI8oDXLCnKc')
except Exception as e:
	print(e)
mpv = player.Player()
print(client.genre)
input()
mpv.play('https://www.youtube.com/watch?v=2jiVz3sf7Vc')
with requests.get(res.podcast_episodes.results[1].get_download_info(get_direct_links=True)[0].direct_link, stream=True) as r:
	with open('d:\\file.cash', "wb") as f:
		shutil.copyfileobj(r.raw, f)
		player.Player().play('d:\\file.cash')
