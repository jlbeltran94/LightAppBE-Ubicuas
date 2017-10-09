from flask import Flask, render_template, request, redirect, url_for, jsonify
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json
import time
app = Flask(__name__)
red = 0
green = 0
blue = 0
white = 0
brightness = 0
status = 0

def on_message(client, userdata, message):    
    global red, green, blue, white, status, brightness
    if message.topic == '/unicauca/light/D0/color':
        print("color")
        line = str(message.payload.decode("utf-8"))
        a = [line[i:i+2] for i in range(1, len(line), 2)]        
        red = int(a[0],16)
        green = int(a[1],16)
        blue = int(a[2],16)
    elif message.topic == '/unicauca/light/D0/relay/0':
        line = str(message.payload.decode("utf-8"))
        print(line)
        status = int(line)
    elif message.topic == '/unicauca/light/D0/brightness':
        brightness = int(str(message.payload.decode("utf-8")))
        

broker_address="iot.eclipse.org"
client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback
client.connect(broker_address)
@app.route("/", methods=['GET','POST'])
def main():
    if request.method == 'POST':
        body = request.json        
        redR = str(body["red"])
        greenR = str(body["green"])
        blueR = str(body["blue"])
        whiteR = str(body["white"])        
        # Turn on the relay
        client.publish("/unicauca/light/D0/relay/0/set", str(body["status"]))
        # Set brightness to 255
        client.publish("/unicauca/light/D0/brightness/set", str(body["brightness"]))
        # Set red ligth to the max        
        client.publish("/unicauca/light/D0/color/set", "%s,%s,%s,%s" %(redR, greenR,blueR,whiteR))
        return jsonify(success=True,msg="Data has changed")
    if request.method == 'GET':
        client.loop_start() #start the loop
        client.subscribe("/unicauca/light/D0/color")  
        client.subscribe("/unicauca/light/D0/relay/0")  
        client.subscribe("/unicauca/light/D0/brightness")            
        time.sleep(0.5)
        client.loop_stop()        
        client.unsubscribe("/unicauca/light/D0/color")  
        client.unsubscribe("/unicauca/light/D0/relay/0")  
        client.unsubscribe("/unicauca/light/D0/brightness")
        
        return jsonify(red=red, green= green,blue=blue, white=white,brightness=brightness, status=status)




if __name__ == "__main__":
    app.run(host='0.0.0.0')