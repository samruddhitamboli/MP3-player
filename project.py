import pygame     #sound 
import tkinter as tkr #gui
import os # change directry,to give path 
import time #for all time relater function
import threading #multiple programming
import speech_recognition as sr #convert speech to text
from mutagen.mp3 import MP3  #handle mp3 file, load ,play,total time

player=tkr.Tk() 
player.title("MP3 Player")
player.geometry('480x620+450+40')

os.chdir("./Music")
songlist=os.listdir() #like a ls command

for i in songlist:
    if not i.endswith(".mp3"):
        songlist.remove(i)

curlist = songlist  

scrollbar=tkr.Scrollbar(player)
scrollbar.pack(side=tkr.RIGHT,fill=tkr.Y)

playlist=tkr.Listbox(player,width=500,height=300,highlightcolor="blue",selectmode=tkr.SINGLE,yscrollcommand=scrollbar.set) #cointainer 
#to select one at the time
pos=0
for song in songlist:
    playlist.insert(pos, song)
    pos=pos+1

try:
    F = open(".fav", "r+") #w+ ka nai: original file wala data udun jato 
except FileNotFoundError:
    F = open(".fav", "w+")
finally:
    favlist = [s[:-1] for s in F.readlines()] #/n nai paije 

songlength=tkr.Label(player,text="Total Time= _ _ : _ _")
currenttime=tkr.Label(player,text="Current Time= _ _ : _ _")

global paused
paused=False      

pygame.init()     #graphics initialization
pygame.mixer.init() #speaker initialize

def showdetails():
    audio=MP3(playlist.get(tkr.ACTIVE)) #je mouse ni select kela 
    total_length=audio.info.length 
    mins,secs=divmod(total_length,60) 
    mins=round(mins)
    secs=round(secs)
    timeformat="{:02d}:{:02d}".format(mins,secs) #round off upto two decimal point
    songlength["text"]="Total Length= "+timeformat       
    thread1=threading.Thread(target=start_count,args=(total_length,)) 
    thread1.start()


def start_count(t):
    t1=0
    while t1!=t and pygame.mixer.music.get_busy():  #check if music stream is playing or not 
        if paused:
            continue
        else:
            mins, secs = divmod(t1, 60)
            mins = round(mins)
            secs = round(secs)
            timeformat = "{:02d}:{:02d}".format(mins, secs)
            currenttime["text"] = "Current time= " + timeformat
            time.sleep(1)
            t1 += 1 


def play():
    global paused
    if pygame.mixer.music.get_busy():
        stop()
        time.sleep(1)
    paused=False
    pygame.mixer.music.load(playlist.get(tkr.ACTIVE))
    var.set(playlist.get(tkr.ACTIVE))    #song name to put on window
    pygame.mixer.music.set_volume(volumeLevel.get()/100)     #volume 0 to 1 madhe asto
    pygame.mixer.music.play()
    showdetails()


def stop():
    pygame.mixer.music.stop()
    currenttime["text"] = "Current Time= _ _ : _ _"
    songlength["text"]="Total time= _ _ : _ _"


def pause():
    global paused
    paused=True
    pygame.mixer.music.pause()


def resume():
    global paused
    paused=False
    pygame.mixer.music.unpause()


def setvol(val):
    volume=int(val)/100
    pygame.mixer.music.set_volume(volume)


def search_song():
    global playlist, ent_bx, curlist
    findsong = ent_bx.get()      #search madhe taklay te get
    playlist.delete(0, 'end') 
    p = 0
    if findsong != "":
        for cursong in curlist:
            if str(findsong).lower() in str(cursong).lower():
                playlist.insert(p, cursong)
                p += 1 
    else:
        for cursong in curlist:
            playlist.insert(p, cursong)
            p += 1


def refresh_songs():        
    playlist.delete(0, 'end')
    p = 0
    for i in songlist:
        playlist.insert(p, i)
        p += 1


def show_all_songs():
    global curlist, songlist
    songlist = curlist
    refresh_songs()

def show_favorites():
    global songlist, favlist, playlist
    songlist = favlist
    refresh_songs()

def add_to_fav(): 
    global playlist, F
    songtoadd = playlist.get(tkr.ACTIVE)
    if songtoadd not in favlist:
        F.write("%s\n" %songtoadd)
        favlist.append(songtoadd)
        refresh_songs()

def remove_song():
    global playlist, F
    songtorem = playlist.get(tkr.ACTIVE)
    try:
        favlist.remove(songtorem)
    except:
        return
    F.close()              
    F = open(".fav", "w+")          #try catch GUI warun song remove hota , actual file madhun ya code ni hota
    for i in favlist:             #fav list parat lihili , madhlich line kadhu nai shakat mhanun purn fav list parat lihili
        F.write("%s\n" %i)              
    refresh_songs()


def listencommand():
    r = sr.Recognizer()              
    with sr.Microphone() as source:  #microphone object return karta
        r.adjust_for_ambient_noise(source, duration=3)         #
        r.energy_threshold = 4000
        r.dynamic_energy_threshold = True
        print("Say command:")
        audio = r.listen(source)
    try:
        cmd = r.recognize_google(audio)   #net nasel tr erroe yeil mg except block
        cmd = str(cmd).lower()
    except sr.UnknownValueError:
        voicecommand()
    return cmd


def voicecommand():
    while True:
        time.sleep(3)
        vcmd = listencommand()
        print(vcmd)

        if 'play' in vcmd:
            indexplaylist = 0
            foundsong = False
            vcmd = str(vcmd).partition(' ',)[2]      #play kadhun taka 
            playlistsize = playlist.size()
            while indexplaylist != playlistsize:
                playlistsong = playlist.get(indexplaylist)
                if vcmd in str(playlistsong).lower():
                    print("found song", playlist.get(indexplaylist))
                    playlist.activate(indexplaylist)
                    #tkr.ACTIVE = indexplaylist
                    foundsong = True
                    break
                indexplaylist = indexplaylist + 1
            if foundsong == True:
                play()
            else:
                print("Song not found ", indexplaylist)

        elif 'stop' in vcmd:
            stop()
        elif 'pause' in vcmd:
            pause()
        elif 'resume' in vcmd:
            resume()
        else:
            print ("Unrecognized Command")


f = tkr.Frame(player, background = "#EEE", height = 60)    
s_label = tkr.Label(f, text = "search")
ent_bx = tkr.Entry(f)                                    
search_button = tkr.Button(f, text = "go!", command = search_song, background = "#55F")  #a=11f=15
s_label.grid(row = 0, column = 0, padx = 10)
ent_bx.grid(row = 0, column = 1, padx = 10, pady = 10)
search_button.grid(row = 0, column = 2, padx = 10)
f.pack()

volumeLevel=tkr.Scale(player,from_=0,to_=100,orient=tkr.HORIZONTAL,resolution=1,command=setvol)
volumeLevel.set(7)
Button1=tkr.Button(player,width=5,height=3,text="PLAY",command=play)
Button2=tkr.Button(player,width=5,height=3,text="STOP",command=stop)
Button3=tkr.Button(player,width=5,height=3,text="PAUSE",command=pause)
Button4=tkr.Button(player,width=5,height=3,text="RESUME",command=resume)

f2 = tkr.Frame(player)
allsongbtn = tkr.Button(f2, text = "All Songs\n", command = show_all_songs, background = "black", foreground = "white") 
addfav = tkr.Button(f2, text = "Add to \nFavorites", command = add_to_fav, background = "#F66", foreground = "white")
favbtn = tkr.Button(f2, text = "Favorites\n", command = show_favorites, background = "#E55")
allsongbtn.grid(row = 0, column = 0, padx = 10)
favbtn.grid(row = 0, column = 1, padx = 10)
remfromfav = tkr.Button(f2, text = "Remove from\nFavorites", command = remove_song, background = "black", foreground = "red")
addfav.grid(row = 0, column = 2, padx = 10)
remfromfav.grid(row = 0, column = 3, padx = 10)

var=tkr.StringVar()   
songtitle=tkr.Label(player,textvariable=var)

Button1.pack(fill="x")     
Button2.pack(fill="x")
Button3.pack(fill="x")
Button4.pack(fill="x")
songtitle.pack(fill="x")
songlength.pack(fill="x")
currenttime.pack(fill="x")
volumeLevel.pack(fill="x",pady = 5)  
f2.pack(pady = 3)     

playlist.pack() #nusta create kela ki disat nai pack karav lagta
scrollbar.config(command=playlist.yview) #sagla mplayer nai only songs khaliwr 


class listener(threading.Thread):        #thread pasun inherit kela class
    def __init__(self):        #method create karaychi asel tr ,init is constructor
        super(listener, self).__init__()        
        self.setDaemon(True)         

    def run(self):
        voicecommand()


objlistener = listener()
objlistener.start()

player.mainloop()
pygame.mixer.music.stop()
F.close()

