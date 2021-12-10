import asyncio
import keyboard
from datetime import datetime

now = datetime.now()
current_time = now.strftime("%H:%M:%S")

##Colours codes: https://ozzmaker.com/add-colour-to-text-in-python/
##Feel free to add others :)
colours = {
	"green":"\033[0;32;47m",
	"blue":"\033[1;34;40m",
	"white":"\033[1;37;40m",
	"red":"\033[1;31;40m",
	"yellow":"\033[1;33;40m",
	"green":"\033[1;32;40m"
}

async def log(logType, message, extraData=[], colour="white"):
	print(f"[{colours['green']}TIME: {colours['white']}{current_time}] [{colours[colour]}Type: {colours['white']}{logType}]: {message}")
	
	if extraData != []:
		extraDataIncrimentor = 1
		for data in extraData:
			print(f"{colours['blue']}^{colours['white']}"*extraDataIncrimentor, " "*(len(extraData)-extraDataIncrimentor), f": {data}")
			extraDataIncrimentor += 1


##How to use:
##log("Log Type", "Log Message",  ["Extra data example 1", "bruh aaa", "hi nick", "add as many as you want", "nick sucks lol"], "red")

