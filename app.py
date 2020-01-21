from flask import Flask, render_template, request, send_from_directory, session, jsonify
from flask_session import Session
from gpiozero import Button,LED

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

    # magnet.on()

    return (str(session['status_session']) + " set")

# qr-code wurde detected
# fridge wird entsperrt, ist aber noch geschlossen
# Endpunkt wird aufgerufen automatisch wenn QR-Code erkannt wurde
@app.route('/set_state1')
def set_state1():
    session["status_session"] = "state1"
    session["status_magnet"] = "off"
    session["status_door"] = "closed"

    magnet.off()

    return render_template('index.html', magnet_state=session["status_magnet"], door_state=session["status_door"])
    #return (str(session['status_session']) + " set")

# fridge wurde geoeffnet
@app.route('/set_state2')
def set_state2():
    session["status_session"] = "state2"
    session["status_magnet"] = "off"
    session["status_door"] = "open"

    return render_template('index.html', magnet_state=session["status_magnet"], door_state=session["status_door"])
    #return (str(session['status_session']) + " set")

# fridge wurde geschlossen, bill soll angezeigt werden
@app.route('/set_state3')
def set_state3():
    session["status_session"] = "state3"
    session["status_magnet"] = "on"
    session["status_door"] = "closed"

    magnet.on()
    # bill_show()

    #return render_template('index.html', magnet_state=session["status_magnet"], door_state=session["status_door"])
    return render_template('index.html', magnet_state=session["status_magnet"], door_state="Ende Gelaende")
    #return (str(session['status_session']) + " set")

# fuunktion wird regelmaessig aufgerufen.
# Abhaengig vom tatsaechlichen status soll der status geupdatet werden
@app.route('/update-state_fridge')
def control_update_fridge_state():
    session["status_door"] = "closed"
    # door_sensor.value == 1 --> closed
    # door_sensor.value == 0 --> open
    # door_sensor.value
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

    # return render_template('index.html', magnet_state=session["status_magnet"], door_state=session["status_door"])
    return ("status is set: " + str(session.get('status_session')))


#start the web server at localhost on port 80 port=1338
if __name__ == '__main__':
    app.secret_key = "super secret fridge key"
    app.run(host='0.0.0.0', port=80, debug=False)