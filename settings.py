import os
import sys
import json
from yandex_music import Client

if sys.platform != 'win32':
	raise SystemExit('YaMusic requires Windows: %LOCALAPPDATA% and the NVDA controller client are used directly.')

prg_folder = os.path.join(os.getenv('LOCALAPPDATA'), 'Ya_music')
cash_folder=os.path.join(prg_folder, 'cash')
download_path=os.path.join(os.getcwd(), 'music')
config_path = os.path.join(prg_folder, 'config.json')
def login(token):
	client = Client(token).init()
	return client

def folder_check():
	folder = os.path.join(os.getenv('LOCALAPPDATA'), 'Ya_music')
	if not os.path.isdir(folder):
		os.mkdir(folder)

def cash_check():
	prg_folder = os.path.join(os.getenv('LOCALAPPDATA'), 'Ya_music')
	cash = os.path.join(prg_folder, 'cash')
	if not os.path.isdir(cash):
		os.mkdir(cash)

def music_check():
	folder=os.path.join(os.getcwd(), 'music')
	if not os.path.isdir(folder):
		os.mkdir(folder)

def config_check():
    config = os.path.join(prg_folder, 'config.json')
    data = {
        "general": {
            "user_name": "",
            "password": "",
            "token": ""
        }
    }

    if not os.path.isfile(config):
        with open(config, "w") as write_file:
            json.dump(data, write_file, indent=4)
