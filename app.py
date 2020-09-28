from flask import Flask, render_template, request, send_from_directory, session, jsonify
from flask_session import Session
from gpiozero import Button,LED
import json
import requests

'''
State-flow:

state0:
   door: closed
   magnet: on
   qr code: not recognized


   if qr-code recognized:
      state_fridge 1

state1:
   door closed
   magnet: off


   qr code: was recognized

   if door was opened:
      state_fridge 2

state2:
   door: opened
   magnet: off
   qr code: ...

   if door is closed again:
      state_fridge 3

State 3:
   door: closed
   magnet: on
   qr code: ...

   show bill

'''

app = Flask(__name__)
sess = Session()

door_sensor = Button(18)
magnet = LED(23)

#set the magnet off; remember the magnet works with inverted logic
magnet.on()

# css
@app.route('/static/<path:path>')
def send_css(path):
    return send_from_directory('static', path)

# returns dict based on requested json-data
@app.route('/get_qrcodes')
def get_qrcodes():
    url = 'http://127.0.0.1:1337/get_qrcodes'
    response = requests.get(url)
    response_dict = json.loads(response.text)
    return(response_dict)


def get_qrcode_amount_items(response_dict):
    return(str(len(response_dict.keys())))

def get_qrcode_html(response_dict):
    
    html_string_body = ""

    for medic_order, medic_name in response_dict.items():
        html_string_body += "<tr><td>" + medic_order + "</td><td>" +  medic_name + "</td></tr>"
        
    html_string = "<table>" + html_string_body + "</table>"

    return(html_string)


@app.route('/get_state')
def get_state():
    dict_status = {}
    dict_status["session"] = session["status_session"]
    dict_status["magnet"] = session["status_magnet"]
    dict_status["door"] = session["status_door"]

    return(jsonify(dict_status))

# fridge geschlossen, verriegelt

# Endpunkt wird aufgerufen von Ajax-Call, wenn QR-Code seite angezeigt wird
# wichtig, damit der fridge initialissiert wird
@app.route('/set_state0')
def set_state0():
    session["status_session"] = "state0"
    session["status_magnet"] = "on"
    session["status_door"] = "closed"

    magnet.off()

    return (str(session['status_session']) + " set")

# qr-code wurde detected
# fridge wird entsperrt, ist aber noch geschlossen
# Endpunkt wird aufgerufen automatisch wenn QR-Code erkannt wurde
@app.route('/set_state1')
def set_state1():
    session["status_session"] = "state1"
    session["status_magnet"] = "off"
    session["status_door"] = "closed"

    magnet.on()

    return render_template('index.html')
    #return (str(session['status_session']) + " set")

# fridge wurde geoeffnet
@app.route('/set_state2')
def set_state2():
    session["status_session"] = "state2"
    session["status_magnet"] = "off"
    session["status_door"] = "open"

    #return render_template('index.html', magnet_state=session["status_magnet"], door_state=session["status_door"])
    #return (str(session['status_session']) + " set")

# fridge wurde geschlossen, bill soll angezeigt werden
@app.route('/set_state3')
def set_state3():
    session["status_session"] = "state3"
    session["status_magnet"] = "on"
    session["status_door"] = "closed"

    magnet.off()

    #return render_template('index.html', magnet_state=session["status_magnet"], door_state="Ende Gelaende")

# funktion wird regelmaessig aufgerufen.
# Abhaengig vom tatsaechlichen status soll der status geupdatet werden
@app.route('/update-state_fridge')
def control_update_fridge_state():

    session["status_door"] = "closed"
    if door_sensor.value == 1:
        session["status_door"] = "closed"
    else:
        session["status_door"] = "open"

    # status wurde noch nicht gesetzt aus irgend einem grund
    if str(session.get('status_session')) == "None":
        set_state0()
        return("status is not set. set state0")

    # wenn state=state1 und status_door = "open", setze state2
    elif str(session.get('status_session')) == "state1" and session["status_door"] == "open":
        set_state2()

    # wenn state=state2 und status_door = "closed", setze state3
    elif str(session.get('status_session')) == "state2" and session["status_door"] == "closed":
        set_state3()

    # state3 = fridge closed, display bill.
    # else display "feel free to help yourself"
    if str(session.get('status_session')) == "state1":
        #qrcodes_dict = get_qrcodes()
        #qrcodes_amount_items = get_qrcode_amount_items(qrcodes_dict)
        #qrcodes_html = get_qrcode_html(qrcodes_dict) 
        #return render_template('bill.html', quantity=qrcodes_amount_items, status_magnet=session["status_magnet"])
        return("state1")
    elif(str(session.get('status_session')) == "state2"):
        #return render_template('state1_2.html', status_magnet=session["status_magnet"])
        return("state2")
    elif(str(session.get('status_session')) == "state3"):
        return("state3")



#start the web server at localhost on port 80 port=1338
if __name__ == '__main__':
    app.secret_key = "super secret fridge key"
    app.run(host='0.0.0.0', port=80, debug=False)
