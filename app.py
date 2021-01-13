from flask import Flask, render_template, request, send_from_directory, session, jsonify
from flask_session import Session
from gpiozero import Button, LED
from time import sleep

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
state_led = LED(24)

#set the magnet off; remember the magnet works with inverted logic
magnet.on()
state_led.on()
print("Script app.py has started")

def blink(times=1, length=0.25):
    for i in range(times):
        print("i = {0}".format(i))
        state_led.off()
        sleep(length)
        state_led.on()
        sleep(length)


@app.route('/test_bill')
def test_bill_template():
    return render_template("bill.html", quantity=42)

@app.route('/test')
def test_template():
    return render_template("test.html")

@app.route('/test_index')
def test_index_template():
    return render_template('index.html', magnet_state=session["status_magnet"], door_state=session["status_door"])

@app.route('/get_state')
def get_state():
    dict_status = {}
    dict_status["session"] = session["status_session"]
    dict_status["magnet"] = session["status_magnet"]
    dict_status["door"] = session["status_door"]

    return(jsonify(dict_status))

# fridge closed, locked

# Endpoint will be called by Ajax-Call, when QR-code side will be displayed
# important, to initialize the fridge
@app.route('/set_state0')
def set_state0():
    session["status_session"] = "state0"
    session["status_magnet"] = "on"
    session["status_door"] = "closed"

    # magnet.on()

    return (str(session['status_session']) + " set")

# qr-code was detected
# fridge is unlocked, but closed
# Endpoint will be called automatically when QR-Code detected
@app.route('/set_state1')
def set_state1():
    session["status_session"] = "state1"
    session["status_magnet"] = "off"
    session["status_door"] = "closed"

    magnet.off()

    return render_template('index.html', magnet_state=session["status_magnet"], door_state=session["status_door"])
    #return (str(session['status_session']) + " set")

# fridge was opened
@app.route('/set_state2')
def set_state2():
    session["status_session"] = "state2"
    session["status_magnet"] = "off"
    session["status_door"] = "open"

    return render_template('index.html', magnet_state=session["status_magnet"], door_state=session["status_door"])
    #return (str(session['status_session']) + " set")

# fridge was closed, bill shall be shown
@app.route('/set_state3')
def set_state3():
    session["status_session"] = "state3"
    session["status_magnet"] = "on"
    session["status_door"] = "closed"

    magnet.on()
    # bill_show()

    #return render_template('index.html', magnet_state=session["status_magnet"], door_state="Ende Gelaende")
    #return (str(session['status_session']) + " set")
    return render_template('index.html', magnet_state=session["status_magnet"], door_state=session["status_door"])

# function will be called continuously
# status will be updated according to measured state
@app.route('/update-state_fridge')
def control_update_fridge_state():
    #session["status_door"] = "closed"
    # door_sensor.value == 1 --> closed
    # door_sensor.value == 0 --> open
    # door_sensor.value
    if door_sensor.value == 1:
        session["status_door"] = "closed"
    else:
        session["status_door"] = "open"

    # if status wasn't set for some reason
    if str(session.get('status_session')) == "None":
        set_state0()
        return("status is not set. set state0")

    # if last_status wasn't set yet
    if str(session.get('last_status')) == "None":
        session["last_status"] = "state0"

    # if state=state1 and status_door = "open", set state2
    elif str(session.get('status_session')) == "state1" and session["status_door"] == "open":
        blink(times=2)
        set_state2()

    # if state=state2 und status_door = "closed", set state3
    elif str(session.get('status_session')) == "state2" and session["status_door"] == "closed":
        blink(times=3)
        set_state3()

    # return render_template('index.html', magnet_state=session["status_magnet"], door_state=session["status_door"])
    if str(session.get('status_session')) == "state3":
        #return("This is a bill")
        return render_template('bill.html', quantity=42)
    else:
        return (str(session.get('status_session')))



# start the web server at localhost on port 80 (not port=1338)
if __name__ == '__main__':
    app.secret_key = "super secret fridge key"
    app.run(host='0.0.0.0', port=80, debug=False)
