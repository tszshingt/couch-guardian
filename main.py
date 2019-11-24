'''
***To install IBM Watson IoT Platform:
sudo apt-get update
sudo apt-get install python-dev python-pip
sudo pip3 install wiotp-sdk psutil
wget https://github.com/ibm-watson-iot/iot-python/archive/master.zip
unzip master.zip
cd iot-python-master/samples/psutil/src

***To test IBM Watson IoT connections:
python3 iotpsutil.py --quickstart

***To install Cloudant:
pip3 install cloudant

***To install Bson and Pmongo (to serialize datetime):
pip3 install bson
pip3 install pymongo

***To install PIL (for motion detection with picam):
sudo apt-get install python-imaging-tk

***To install pygame:
(check online if not already installed)

'''

from gpiozero import LED, Button
from picamera import PiCamera
from time import sleep
import random
from pygame import mixer
import threading
from pkg.credentials import *
from pkg.IBMWatsonIoT import *
from pkg.IBMDatabase import *
from pkg.picamMotionDetect import *
from pkg.petDetection import *

# Function wrapper to run data upload to cloud in separate thread
def uploadWrapper (db):
    db.addData(msg)
    sendSignalToWatsonIoT(orgId,typeId,deviceId,token,msg[1])

'''
camera = PiCamera()
camera.rotation = 180
camera.start_preview()
for effect in camera.IMAGE_EFFECTS:
    camera.image_effect = effect
    sleep(3)
    camera.capture('/home/pi/CouchG/testpy_%s.jpg' % effect)
camera.stop_preview()

'''

# IBM credentials
# Please see credentials.py

# Global variable
isMotion=[False,'imagePath']

# Pi hardware initialization:
button = Button(17)
led = LED(21)

# mixer settings
audioFile = 'res/sample.mp3'

# General settings
lastClassifyTime = 0
lastActivatedTime = 0
lastUploadTime = 0
minWaitingTime = 10
minClassifyTime = 5

petClass = ['Non-Pet','Cat','Dog']
msg=['Yes',petClass[0]]

# IBM Cloudant config:
dbName= "cgdb"

#### Main code starts here ####

# Initialize mixer
mixer.init()
mixer.music.load(audioFile)

# IBM Cloudant connection
db=IBMDatabase(deviceID,username,apikey)
db.connect()
db.createDatabase(dbName)
db.disconnect()

# Start motion detection in new thread
thrMotion=threading.Thread(target=detectMotion,args=(isMotion,))
thrMotion.start()

# Seed random number
#random.seed()

while True:
    #if motion is detected:
    if isMotion[0]:
        led.on()
        
        # if more than minClassifyTime beyond last pet classification time,
        # then classify and check for pet time
        if (time.time() - lastClassifyTime) > minClassifyTime:
            imagePath = isMotion[1]
            petType = classifyPet(imagePath)
            msg[1]=petClass[petType]
            lastClassifyTime = time.time()
    
        # if more than minWaitingTime beyond last activation,
        # then activate deterrent if pet is detected        
        if (time.time() - lastActivatedTime) > minWaitingTime:         
            if (petType > 0):
                mixer.music.play()            
                lastActivatedTime = time.time()
                
        # if more than minWaitingTime beyong last motion detection,
        # then upload data to IBM Cloudant and send signal to WatsonIoT
        # in new threads
        if (time.time() - lastUploadTime) > minWaitingTime:
            thrUpload=threading.Thread(target=uploadWrapper,args=(db,))
            thrUpload.start()
            lastUploadTime = time.time()    
    else:
        led.off()
        # audio plays for at least minWaitingTime seconds
        if (time.time() - lastActivatedTime) > minWaitingTime:            
            mixer.music.stop()
