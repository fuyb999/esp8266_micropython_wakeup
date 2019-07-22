from umqtt.simple import MQTTClient
from machine import Timer
from machine import Pin
import machine
import utils
import time
from cfg import Config
import gc


class Mqtt:
    def __init__(self, check_msg_period=10):

        '''
         self._led = led
         if self._led is None:
            self._led = Pin(2, Pin.OUT, value=1)
        '''

        self.on_connect = None
        self.on_message = None
        self.on_check_message = None
        self.on_keep_connect = None

        self._last_message = 0
        self._message_interval = 30
        self._publish_counter = 0
        self._check_message_timer = Timer(0)
        self._period = check_msg_period

        # keepalive --> fix [Errno 103] ECONNABORTED //socket: Software caused connection abort
        self.client = MQTTClient(
            Config.MQTT_CLIENT_ID,
            Config.MQTT_HOST,
            port=Config.MQTT_HOST_PORT,
            user=Config.MQTT_USERNAME,
            password=Config.MQTT_PASSWORD,
            keepalive=Config.MQTT_KEEP_ALIVE
        )

    def _client_topic_cb(self, topic, msg):
        print("\n- received topic: %s\n- message: %s" % (topic, msg))
        if self.on_message is not None:
            self.on_message(self, topic, msg)

        gc.collect()

    def _check_message_cb(self, timer):
        try:
            self.client.check_msg()
            # keep connecting
            if (time.time() - self._last_message) > self._message_interval:
                msg = b'Hello #%d' % self._publish_counter
                self.client.publish(Config.MQTT_TOPIC_PUB, msg)
                self._last_message = time.time()
                self._publish_counter += 1
                if self._publish_counter > 19911229:
                    self._publish_counter = 0
                if self.on_keep_connect is not None:
                    self.on_keep_connect(self, timer)
                print(msg)

            if self.on_check_message is not None:
                self.on_check_message(self, timer)

        except OSError as e:
            print(e)
            try:
                self.client.disconnect()
            finally:
                print("Reconnecting MQTT broker")
                self._check_message_timer.deinit()
                self.start()
                time.sleep(0.6)

        gc.collect()

    def publish(self, msg):
        self.client.publish(Config.MQTT_TOPIC_PUB, msg)

    def set_on_connect(self, f):
        self.on_connect = f

    def set_on_message(self, f):
        self.on_message = f

    def set_on_check_message(self, f):
        self.on_check_message = f

    def set_on_keep_connect(self, f):
        self.on_keep_connect = f

    def start(self):
        time.sleep(1)
        # retry connect mqtt
        retry = 1 * 60 * 30  # 30 mins
        for i in range(retry):
            print('try connect {} {}'.format(Config.MQTT_HOST, i + 1))
            if i == retry:
                machine.reset()
            try:
                self.client.set_callback(self._client_topic_cb)
                self.client.connect()
                self.client.subscribe(Config.MQTT_TOPIC_SUB)
                break
            except Exception as e:
                print(e)
                # 连接mqtt失败,主板灯闪烁2次
                utils.flash_board_led(2)
                gc.collect()
            time.sleep(1)
        # assert self.self.on_connect is not None, "connect callback is not set"
        if self.on_connect is not None:
            self.on_connect(self)
        print("Connected to %s\nSubscribed topic %s\n" % (Config.MQTT_HOST, Config.MQTT_TOPIC_SUB))

        self._check_message_timer.init(
            mode=Timer.PERIODIC,
            period=self._period,
            callback=self._check_message_cb
        )

        gc.collect()
