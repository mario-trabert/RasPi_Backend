from flask import Flask, render_template, request
from gpiozero import Button,LED


app = Flask(__name__)

inputdevice = Button(18)
magnet = LED(23)

#set the magnet off; remember the magnet works with inverted logic
magnet.on()
#save current magnet state
magnet_state = 'Doorlock is off'
door_state = 'Door is closed'

#display the main web page
@app.route('/')
def main():
   global magnet_state
   global door_state
   # pass the magnet state to the index.html and return it to the user
   if inputdevice.value == 1:
      door_state = 'Door is closed'
   if inputdevice.value == 0:
      door_state = 'Door is open'
   return render_template('index.html', magnet_state=magnet_state,door_state=door_state)

#execute control() when someone presses the on/off buttons
@app.route('/<action>')
def control(action):
   global magnet_state
   global door_state
   #if the action part of the URL is 'on', turn the magnet on
   if action == 'on':
      #set the magnet on
      magnet.on()
      #save the magnet state
      magnet_state = 'Doorlock is on'
   if action == 'off':
      magnet.off()
      magnet_state = 'Doorlock is off'
   if inputdevice.value == 1:
      door_state = 'Door is closed'
   if inputdevice.value == 0:
      door_state = 'Door is open'

   #pass the magnet state to the index.html and return it to the user
   return render_template('index.html', magnet_state=magnet_state, door_state=door_state)

#start the web server at localhost on port 80
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=80, debug=True)