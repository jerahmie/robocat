# Single Color Code Tracking Example
#
# This example shows off single color code tracking using the OpenMV Cam.
#
# A color code is a blob composed of two or more colors. The example below will
# only track colored objects which have both the colors below in them.

import sensor, image, time, math
import time
from pyb import RTC
from pyb import I2C
from pyb import SPI


# SPI setup
spi = SPI(2, SPI.MASTER, baudrate=int(1000000/66), polarity=0, phase=0)


# i2c setup
i2c_addr = 0x70

i2c = I2C(2, I2C.MASTER) # The i2c bus must always be 2.
i2c.init(I2C.MASTER)

# real time clock setup
rtc = RTC()
t0 = time.localtime() # use current time
rtc.datetime((2022, 9, 3, 7, 19, 4, 0, 0 ))

# seven segment display

# map integer to ssd value
i2ssd = dict()
i2ssd[0] = 0x3f
i2ssd[1] = 0x06
i2ssd[2] = 0x5b
i2ssd[3] = 0x4f
i2ssd[4] = 0x66
i2ssd[5] = 0x6d
i2ssd[6] = 0x7d
i2ssd[7] = 0x07
i2ssd[8] = 0x7f
i2ssd[9] = 0x6f

def disp_blank(disp_addr = i2c_addr):
    """ blank the display
    """
    ba = bytearray([0 for _ in range(17)])
    i2c.mem_write(ba, disp_addr, 0)


def disp_beef(disp_addr = i2c_addr):
    """ display "bEEF" (an inside joke)
    """
    beef = bytearray([0x7c, 0x7c, 0x79, 0x79, 0x79, 0x79, 0x79, 0x79, 0x71, 0x71])
    i2c.mem_write(beef, i2c_addr, 0)

def hours2disp(hours: int) -> list:
    """genrate the byte array for hours display
    12 - hour display
    do not display preceding zero if time < 10:00
    returns list of ssd values corresponting to number
    """
    hours = hours%12
    if hours == 0:
        hours = 12

    if hours < 10:
        return [0x00, i2ssd[hours]]
    else:
        return [i2ssd[1], i2ssd[hours - 10]]

def mins2disp(mins: int) -> list:
    """ Set the minutes display
    """
    mins = mins%60   # make sure the minutes map to 0 to 59
    m1 = mins // 10  # first minute digit
    m2 = mins % 10   # second minute digit
    return [i2ssd[m1], i2ssd[m2]]


def init_display(disp_addr = i2c_addr):
    """ Initialize the seven-segment display
    """
    i2c.send(0x21, disp_addr)
    i2c.send(0xa0, disp_addr)
    disp_blank()
    i2c.send(0x81, disp_addr)
    time.sleep_ms(500)
    disp_beef()
    time.sleep_ms(500)
    disp_blank()

def update_display(disp_addr = i2c_addr):
    """ update the display using rtc time: hh:mm
    """
    datetime = rtc.datetime()
    hours =  datetime[4]
    minutes = datetime[5]
    #print("hours: ", hours, " minutes: ", minutes)
    ssd_hours = hours2disp(hours)
    ssd_mins = mins2disp(minutes)
    ssd_disp = bytearray([ssd_hours[0], ssd_hours[0], ssd_hours[1], ssd_hours[1], 0xff, 0xff, ssd_mins[0], ssd_mins[0], ssd_mins[1], ssd_mins[1]])
    i2c.mem_write(ssd_disp, i2c_addr, 0)


def send_motor_update(md_left, ms_left, md_right, ms_right):
    """ send command to adjust motor positions
    md_left: left motor direction
    ms_lest: left motor speed
    md_right: right motor direction
    ms_right: right motor speed
    """
    #buf = bytearray([0x7c, 0x79, 0x79, 0x71])
    #buf = bytearray([0x00, 0x01, 0x02, 0x03])
    if md_left == 0:
        b0 = 0
    else:
        b0 = 1
    if ms_left >= 0 and ms_left < 255:
        b1 = ms_left
    else:
        b1 = 0
    if md_right == 0:
        b2 = 0
    else:
        b2 = 1
    if ms_right >= 0 and ms_right < 255:
        b3 = ms_right
    else:
        b3 = 0
    buf = spi.send_recv(bytearray([b0, b1, b2, b3]))
    print("tick")

# Color Tracking Thresholds (L Min, L Max, A Min, A Max, B Min, B Max)
# The below thresholds track in general red/green things. You may wish to tune them...
#thresholds = [(30, 100, 15, 127, 15, 127), # generic_red_thresholds -> index is 0 so code == (1 << 0)
#              (30, 100, -64, -8, -32, 32)] # generic_green_thresholds -> index is 1 so code == (1 << 1)
# Codes are or'ed together when "merge=True" for "find_blobs".
#thresholds = [(100, 100, -10, 10, -10, 10)]
thresholds=[(94, 100, -128, 12, -16, 5)]
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()

# Only blobs that with more pixels than "pixel_threshold" and more area than "area_threshold" are
# returned by "find_blobs" below. Change "pixels_threshold" and "area_threshold" if you change the
# camera resolution. "merge=True" must be set to merge overlapping color blobs for color codes.
init_display()
loop_count = 0

# motor direction and speeds
mdl = 0
mdr = 0
msl = 0
msr = 0

while(True):
    clock.tick()
    img = sensor.snapshot()
    for blob in img.find_blobs(thresholds, pixels_threshold=10, area_threshold=10, merge=True):
    #for blob in img.find_circles(threshold=200):
        if blob.code(): # r/g code == (1 << 1) | (1 << 0)
            # These values depend on the blob not being circular - otherwise they will be shaky.
            #if blob.elongation() > 0.5:
            #    img.draw_edges(blob.min_corners(), color=(255,0,0))
            #    img.draw_line(blob.major_axis_line(), color=(0,255,0))
            #    img.draw_line(blob.minor_axis_line(), color=(0,0,255))
            # These values are stable all the time.
            #img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())
            # Note - the blob rotation is unique to 0-180 only.
            img.draw_keypoints([(blob.cx(), blob.cy(), int(math.degrees(blob.rotation())))], size=20)

    blobs = img.find_blobs(thresholds, pixels_threshold=10, area_threshold=10, merge=True)
    if len(blobs) >= 1:
        print(blobs[0].cx(), blobs[0].cy())
        if blobs[0].cy() < 200:
            mdl = 0
            mdr = 0
            msl = 100
            msr = 100
        elif blobs[0].cy() >= 200 and blobs[0].cx() < 120:
            mdl = 0
            mdr = 1
            msl = 100
            msr = 100
        elif blobs[0].cy() >= 200 and blobs[0].cx() > 136:
            mdl = 1
            mdr = 0
            msl = 100
            msr = 100
        else:
            mdl = 0
            mdr = 0
            msr = 0
            msl = 0
    else:
        mdl = 0
        mdr = 0
        msr = 0
        msl = 0
    #print("blobs: ", len(blobs))
    #centroid = (blob.cx(), blob.cy(), blob.cz())
    #print("centroid: ", centroid)

    # loop update
    if loop_count % 100 == 0:
        update_display()

    # motor update
    if loop_count % 11 == 0:
        send_motor_update(mdl, msl, mdr, msr)

    loop_count += 1

