import ctypes, platform
clientLib =ctypes.windll.LoadLibrary('./nvdaControllerClient64.dll')

def say(msg):
    clientLib.nvdaController_speakText(str(msg))

def close_speech():
    clientLib.nvdaController_cancelSpeech()