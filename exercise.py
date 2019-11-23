from gpiozero import LED, Button
from picamera import PiCamera
from time import sleep
import random
from pygame import mixer
from pkg.IBMDatabase import *

'''
(Desirable) Log activities in dashboard. The device should log device activities in
a database stored in the device. The logged data should include date and time of motion
detection, entity type, whether the entity is a valid entity, date and time of deterrent
activation, activated deterrent type(s), and errors. The database should be retrievable
from a third-party system connected to the same local area network, and the content of
the database should be summarized and visually displayed in a dashboard format.
'''


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
# initialization:
button = Button(17)
led = LED(21)
# IBM Cloudant IAM credentials:
deviceID = "pi4"
username = "52ce675d-4e87-4b97-8553-c623c54be742-bluemix"
apikey = "fZsK3HT2Xeb8BeKlvXfbSr_xwP98bGpkPBhKdT6ItmDp"
dbName= "temp3"
msg=[["yes","n/a"],["yes",'cat']]
mixer.init()
mixer.music.load('res/sample.mp3')
mixer.music.play()

# main code:

db=IBMDatabase(deviceID,username,apikey)
db.connect()
db.createDatabase(dbName)
db.disconnect()
random.seed()
while True:
    selector=random.randint(0,1)
    if button.is_pressed:
        led.on()
        db.addData(msg[selector])
    else:
        led.off()
