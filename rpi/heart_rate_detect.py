import RPi.GPIO as GPIO
import time

def handle_heartrate(chl):
    global channel
    global count
    global doCounting
    global startTime
    global currentTime

    channel = chl
    count = count + 1
    
    if not doCounting:
        if count == 10:
            print('Starting actual counting...')
            startTime = time.time()
            count = 0
            doCounting = True                
        
    if doCounting:
        currentTime = time.time()
        if currentTime - startTime > 15:
            if count > 0:
                print('Heart rate is {}'.format(str(count * 4)))
            startTime = time.time()
            count = 0

# Pin definition
channel = 0
heartPin = 16
ledPin = 40
butPin = 38
count = 0
doCounting = False
startTime = time.time()  # ??? startTime ??????
currentTime = 0.0
doMeasureHeartRate = False

# Pin setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(heartPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(butPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print('Program running... Press Ctrl+C to exit')

try:
    GPIO.output(ledPin, False)        
    
    while True:
        if not GPIO.input(butPin):
            if not doMeasureHeartRate:
                print('Measuring heart rate...')
                doMeasureHeartRate = True
                GPIO.output(ledPin, True)
                count = 0
                doCounting = False
                startTime = time.time()  # ????? startTime ??????
                currentTime = 0.0
                GPIO.add_event_detect(heartPin, GPIO.RISING, callback=handle_heartrate)
            else:
                print('Stopped...')
                doMeasureHeartRate = False
                GPIO.output(ledPin, False)
                GPIO.remove_event_detect(heartPin)
            time.sleep(0.2)
        
        if doMeasureHeartRate:
            currentTime = time.time()
            if currentTime - startTime > 20:
                print('Still waiting for heart beat...')
                startTime = time.time()
                count = 0
                doCounting = False
    
except KeyboardInterrupt:
    print('Program terminated!')
    
except OSError as err:
    print('An error has occurred: {}'.format(err))

finally:
    GPIO.cleanup()
