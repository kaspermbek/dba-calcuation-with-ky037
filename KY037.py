from umachine import ADC
import time
from math import log10, sqrt
from collections import deque

#########################################################################
# Initialize Microphone on GP28 (ADC0)
##########################################################################
mic = ADC(28)

##########################################################################
# State variables
##########################################################################
# print("Calibrating silence... Keep the room quiet.")
roundingList = []
samples = deque([0]*800, 800)

##########################################################################
# Functions
##########################################################################
##########################################################################
# Get samples for every 125 micro second
# Append sample to list until 800 samples
##########################################################################
def getSamples():
    global samples
    # start = time.ticks_us() # For printing time
    for i in range(100):
        ready = time.ticks_us()
        samples.append(mic.read_u16())
        while time.ticks_us() < ready + 107:
            pass
    # end = time.ticks_us() # For printing time

    # print(f"\nTIME - {(end-start) / 800} micro sec pr. sample")
    return samples

"""def getSamples():
    global samples
    # start = time.ticks_us() # For printing time
    for i in range(800):
        ready = time.ticks_us()
        samples.append(mic.read_u16())
        while time.ticks_us() < ready + 107:
            pass
    # end = time.ticks_us() # For printing time

    # print(f"\nTIME - {(end-start) / 800} micro sec pr. sample")
    # print(samples)
    return samples"""


##########################################################################
# Raw loudness registation
# Calc RMS
##########################################################################
def get_loudness(samples):
    sample_max = 0
    sample_min = 65535
    rmsCounts = 0
    squareRMS = 0
    for sample in samples:
        # Peak to peak, used for comparison of data
        if sample > sample_max: sample_max = sample
        if sample < sample_min: sample_min = sample

        # Calculate RMS
        center = sum(samples) / len(samples)
        center_sample = abs(sample - center)  # center hardcode = 32768
        squareRMS += center_sample ** 2
        rmsCounts += 1

    rms = sqrt(squareRMS / rmsCounts)
    return rms


###################################################################
# dBFS calculation
###################################################################
def dBFS_calc(rms):
    rmsReferance = 150  # Lowest RMS value
    offset = 34
    scale_factor = 7  # software amplifier

    dBFS = 20 * log10(rms / rmsReferance)
    dBFS_A = round((dBFS * scale_factor) + offset)
    return dBFS_A


##########################################################################
# Calculation for data send to MQTT
##########################################################################
def median_calc(dBFS):
    roundingList.append(dBFS)

    if len(roundingList) == 9:
        roundingList.sort()
        median = roundingList[4]
        roundingList[:] = roundingList[3:6]  # List sliced to the 3 middle values in the list

        print(f"{median} Median")
        return median