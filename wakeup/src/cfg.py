class Config:
    # OneNet MQTT Host IP
    MQTT_HOST = "mqtt.heclouds.com"
    MQTT_HOST_PORT = 6002

    # Device ID
    MQTT_CLIENT_ID = "518725880"

    # Product Name
    MQTT_USERNAME = "217551"

    # Authentication Info
    MQTT_PASSWORD = "esp8266wakeup"

    MQTT_TOPIC_SUB = b'ledctl'
    MQTT_TOPIC_PUB = b'hello'

    MQTT_KEEP_ALIVE = 60
