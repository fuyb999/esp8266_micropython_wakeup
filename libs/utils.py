import time
from time import sleep
import network
import machine
import ubinascii
import gc
from configparser import Configparser


def connect_to_internet(ssid=None, password=None):
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(False)
    sta_if.active(True)
    print("\nConnecting to internet...")

    store = Configparser()
    if ssid is None:
        ssid = store.get("ssid")
    if password is None:
        password = store.get("password")
    if store is None or password is None:
        return -1

    sta_if.connect(ssid, password)

    while not sta_if.isconnected():
        result_code = sta_if.status()
        if result_code == network.STAT_IDLE:
            print("network idle")
            break
        elif result_code == network.STAT_CONNECT_FAIL:
            print("network connect failed")
            break
        elif result_code == network.STAT_CONNECTING:
            pass
        elif result_code == network.STAT_GOT_IP:
            break
        elif result_code == network.STAT_NO_AP_FOUND:
            print("cannot found ap")
            break
        elif result_code == network.STAT_WRONG_PASSWORD:
            print("wrong password given")
            break

        sleep(0.5)

    result_code = sta_if.status()
    if result_code == network.STAT_GOT_IP:
        print("- network config:", sta_if.ifconfig(), end='\n\n')
        return 1

    return 0


def try_connect_internet():
    i = 0
    while True:
        state = connect_to_internet()
        if state == -1:
            return False
        if state == 1:
            # 联网成功,主板灯闪烁2次
            flash_board_led(2)
            return True
        sleep(1.6)
        print("try connect internet {}".format(i))
        i += 1

        gc.collect()


def chip_id():
    return ubinascii.hexlify(machine.unique_id()).decode("utf-8")


def flash_board_led(count=1, off_time=0.1):
    from machine import Pin
    led = Pin(2, Pin.OUT, value=1)
    for i in range(count):
        led.value(0)  # on
        if off_time is None or off_time < 0:
            break
        sleep(off_time)
        led.value(1)  # off
        sleep(0.6)


def do_quick_reset():
    time.sleep(1)
    store = Configparser()
    quick_reset = store.get("quick_reset", 0)
    quick_reset = int(quick_reset)
    quick_reset += 1
    store.set("quick_reset", quick_reset)
    time.sleep(0.6)
    print("quick_reset={}".format(quick_reset))

    if quick_reset >= 4:
        import os
        from configparser import STORE_FILE
        os.remove(STORE_FILE)

    flash_board_led(off_time=1.2)

    store.set("quick_reset", 0)
