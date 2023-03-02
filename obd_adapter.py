import sys
import ac
import acsys
import math
import time
from emulator import FreematicsEmulator

PID_RPM = 0x0C
PID_SPEED = 0x0D
PID_THROTTLE = 0x11
PID_TORQUE = 0x62

rpm_label=0
speed_label=0
throttle_label=0
brake_label=0
torque_label=0
rpm_value=0
speed_value=0
throttle_value=0
brake_value=0
torque_value=0

obd_emulator_status_label=0
is_OBD_emu_connected=False
is_procol_set=False
obd_emu = FreematicsEmulator()

def acMain(ac_version):
    global rpm_label, speed_label, throttle_label, brake_label, torque_label, obd_emulator_status_label

    #Initializing in-game Window
    appWindow = ac.newApp("obd_adapter")
    ac.setSize(appWindow, 200, 200)

    #Initializing Labels
    rpm_label = ac.addLabel(appWindow, "RPM: 0")
    speed_label = ac.addLabel(appWindow, "Speed: 0 kmh")
    throttle_label = ac.addLabel(appWindow, "Throttle: 0%")
    brake_label = ac.addLabel(appWindow, "Brake: 0%")
    torque_label = ac.addLabel(appWindow, "Torque: 0.00Nm")
    obd_emulator_status_label = ac.addLabel(appWindow, "OBD Emulator: NO")

    #Setting Labels position
    ac.setPosition(rpm_label, 3, 30)
    ac.setPosition(speed_label, 3, 50)
    ac.setPosition(throttle_label, 3, 70)
    ac.setPosition(brake_label, 3, 90)
    ac.setPosition(torque_label, 3, 110)
    ac.setPosition(obd_emulator_status_label, 3, 140)

    return "obd_adapter"

def acUpdate(deltaT):
    global rpm_label, speed_label, throttle_label, brake_label, rpm_value, speed_value, throttle_value, brake_value, torque_label, torque_value, obd_emulator_status_label, is_OBD_emu_connected, obd_emu

    rpm = ac.getCarState(0, acsys.CS.RPM)
    speed = ac.getCarState(0, acsys.CS.SpeedKMH)
    throttle = ac.getCarState(0, acsys.CS.Gas)
    brake = ac.getCarState(0, acsys.CS.Brake)
    torque = ac.ext_getCurrentTorque() # Only works with CSP 0.1.79 (or higher) installed, third party pack for Assetto Corsa

    #Setup OBD-II Emulator Connection
    if not is_OBD_emu_connected:
        ac.setText(obd_emulator_status_label, "OBD Emulator: CONNECTING")
        obd_emu.connect()
        time.sleep(0.5)
        #obd_emu.reinitialize()
        #time.sleep(0.5)

        obd_emu.clear_dtc()
        obd_emu.enable_vin()
        if obd_emu.set_vin("4" * 17) == "OK":
            is_OBD_emu_connected=True
            ac.setText(obd_emulator_status_label, "OBD Emulator: OK")

    if not is_procol_set:
        if (obd_emu.set_protocol("ISO9141_2") == "OK"):
            is_procol_set=True

    #Values update in the in-game app and in the OBD-II Emulator
    link_error=False
    if rpm != rpm_value:
        rpm_value = rpm
        toSend = math.trunc(rpm_value)
        ac.setText(rpm_label, "RPM: {}".format(toSend))
        if (is_OBD_emu_connected and is_procol_set):    
            if obd_emu.set_pid(PID_RPM, toSend) == "ERROR":
                link_error=True

    if speed != speed_value:
        speed_value = speed
        toSend = math.trunc(speed_value)
        ac.setText(speed_label, "Speed: {} kmh".format(toSend))
        if (is_OBD_emu_connected and is_procol_set): 
            if obd_emu.set_pid(PID_SPEED, toSend) == "ERROR":
                link_error=True

    if throttle != throttle_value:
        throttle_value = throttle
        toSend = math.trunc(throttle_value*100)
        ac.setText(throttle_label, "Throttle: {}%".format(toSend))
        if (is_OBD_emu_connected and is_procol_set): 
            if obd_emu.set_pid(PID_THROTTLE, toSend) == "ERROR":
                link_error=True

    if brake != brake_value:
        brake_value = brake
        toSend = math.trunc(brake_value*100)
        ac.setText(brake_label, "Brake: {}%".format(toSend))
        #BRAKE Percent is NOT being sent

    if torque != torque_value:
        torque_value = torque
        toSend = math.trunc(torque_value)
        ac.setText(torque_label, "Torque: {}Nm".format(toSend))
        if (is_OBD_emu_connected and is_procol_set): 
            if obd_emu.set_pid(PID_TORQUE, toSend) == "ERROR":
                link_error=True

    if link_error:
        ac.setText(obd_emulator_status_label, "OBD Emulator: RESTARTING")
        obd_emu.reinitialize()
        time.sleep(0.25)

def acShutdown():
    global obd_emu
    obd_emu.close()
    return



    

    
