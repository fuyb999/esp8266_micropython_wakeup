from todo import Todo
import utils
import webrepl
import network
import time

if __name__ == "__main__":
    try:
        utils.do_quick_reset()
        wlan_ap = network.WLAN(network.AP_IF)
        wlan_ap.active(False)
        if utils.try_connect_internet():
            webrepl.stop()
            wlan_ap.active(False)
            time.sleep(0.3)

            target = Todo()
            target.run()

            # 业务逻辑执行成功,主板灯闪烁3次
            utils.flash_board_led(3)
        else:
            wlan_ap.active(True)
            webrepl.start()

            # 如果网络未连接，主板灯常亮
            utils.flash_board_led(off_time=-1)

    except KeyboardInterrupt:
        print("\nPress CTRL+D to reset device.")
