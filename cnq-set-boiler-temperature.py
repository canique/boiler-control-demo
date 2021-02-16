import asyncio
import sys, socket
import json, time
import gmqtt #code has been tested with python 3.7.3, gmqtt 0.6.9


currentMode = None

def on_connect(client, flags, rc, properties):
    print('Successfully connected to MQTT broker as', client._client_id)
    client.subscribe([gmqtt.Subscription('heating/1/water_temperature', qos=1), gmqtt.Subscription('heating/1/program/mode', qos=1)])


def on_message(client, topic, payload, qos, properties):
    global setPoint, STOP, currentMode

    if not payload:
        return

    if topic == 'heating/1/program/mode':
        currentMode = payload.decode('ascii')
        print("Current Mode:", currentMode)
        
        if currentMode == 'expert':
            sendSetTemperatureRequest(client)
        else: #set heating mode to expert
            client.publish('req/{}/setHeatingMode'.format(client._client_id), "expert", qos=1, message_expiry_interval=60, retain=False)

        return

    if topic == 'heating/1/water_temperature': #here we check whether our request has been fulfilled
        jsonPayload = json.loads(payload)
        currentWaterTemperature = jsonPayload['tmp']

        if properties['retain'] == 1:
            print('Previously set water temperature: {} °C'.format(currentWaterTemperature))

        if currentWaterTemperature == setPoint: #request has been successfully executed
            STOP.set() #signal program to quit
            if properties['retain'] == 1:
                print('Temperature is already @ {} °C.'.format(currentWaterTemperature))
            else:
                print('Temperature has been successfully set to {} °C.'.format(currentWaterTemperature))


def on_disconnect(client, packet, exc=None):
    print('Disconnected')


def sendSetTemperatureRequest(client):
    global setPoint, currentMode

    setTemperatureRequest = {}
    setTemperatureRequest['ts'] = int(round(time.time() * 1000)) # unix timestamp in ms
    setTemperatureRequest['water_tmp'] = int(setPoint)

    setTemperatureRequestJson = json.dumps(setTemperatureRequest)

    #send temperature request
    print('Sending request to set boiler water temperature to {} °C'.format(setPoint))
    client.publish('req/{}/setBoilerTemperature'.format(client._client_id), setTemperatureRequestJson, qos=1, message_expiry_interval=60, retain=False, content_type='cnq/0.1+json')


async def main(broker_host):
    global STOP

    STOP = asyncio.Event()
    client = gmqtt.Client("demo-client-" + socket.gethostname(), clean_session=True)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    try:
        await asyncio.wait_for(client.connect(broker_host, 1883, keepalive=60), timeout=1.0)

        try:
            await asyncio.wait_for(STOP.wait(), timeout=1.0) # wait for temperature request/response
        except asyncio.TimeoutError:
            print("Could not set boiler temperature.")
    except asyncio.TimeoutError:
        print("Timeout while connecting to", broker_host)
    except OSError as e:
        print("Could not connect to", broker_host)

    await client.disconnect()


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print("Usage: democlient.py hostname boilerTemperature")
        exit(1)

    brokerHost = sys.argv[1]
    setPoint = int(sys.argv[2])

    asyncio.run(main(brokerHost))
