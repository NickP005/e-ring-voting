##WARNING: UNFINISHED AND UNTESTED##
##this code might not be functional, so dont use any of it in your code yet, ill finish it soon##
##Like i havent even run this once, im programming this through github so it probably wont work##
##Also havent checkedd any of this very much lol##

import asyncio
from pynput import keyboard

global listening
currentConsoleStrData = []
ableToType = True ##To stop characters from being spammed.
functionKeys = {"enter":"dataInputted", "backspace":"eraseChar"} ##Key:functionToCall
consoleFlags = {"dataInputted":False, "currentConsoleOutput":""}

def dataInputted():
  for char in currentConsoleStrData:
    consoleFlags["currentConsoleOutput"] += char
  consoleFlags["dataInputted"] = True

def eraseChar():
  currentConsoleStrData.pop(len(currentConsoleStrData)-1) ##Pops the last index.
  
  

def keyDown(key):
  if ableToType == True:
    if key not in functionKeys:
      currentConsoleStrData.append(key) ##Might need to use key.char incase this doesnt work.
    
    else:
      try:
        globals()[functionKeys[key]]() ##This is a way of calling a function from its string name.
        
      except:
        pass ##Add exceptions another time.
      
      
    ableToType = False
  
def keyUp(key):
  ableToType = True


def listenThread():
  with keyboard.Listener(on_press = keyDown, on_release = keyUp) as listener:
    listener.join()
  

##When thread is created, this returns to calling function.
async def createListenThread():
  LT = threading.Thread(target=listenThread)
  LT.start()

async def getInputtedData():
  if consoleFlags["dataInputted"] != False:
    return consoleFlags["currentConsoleOutput"]
  return None
