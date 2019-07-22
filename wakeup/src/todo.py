from mqtt import Mqtt
import gc


class Todo:
    def __init__(self):
        self.mqtt = Mqtt()
        self.mqtt.set_on_message(self._on_message)

    def _on_message(self, mqtt, topic, msg):
        if msg == b'on':
            import wakeup
            wakeup.send()
        elif msg == b'off':
            pass
        else:
            pass

        gc.collect()

    def run(self):
        self.mqtt.start()


if __name__ == "__main__":
    pass
