#sudo pip3 install gpiozero
# 
from flask import Flask, render_template, request
from gpiozero import LED


#create a Flask object
app = Flask(__name__)

#create an object that refers to a magnet
magnet = LED(23)
#set the magnet off; remember the magnet works with inverted logic
magnet.on()
#save current magnet state
magnet_state = 'Doorlock is off'

#display the main web page
@app.route('/')
def main():
   global magnet_state
   # pass the magnet state to the index.html and return it to the user
   return render_template('index.html', magnet_state=magnet_state)

#execute control() when someone presses the on/off buttons
@app.route('/<action>')
def control(action):
   global magnet_state
   #if the action part of the URL is 'on', turn the magnet on
   if action == 'on':
      #set the magnet on
      magnet.on()
      #save the magnet state
      magnet_state = 'Doorlock is on'
   if action == 'off':
      magnet.off()
      magnet_state = 'Doorlock is off'

   #pass the magnet state to the index.html and return it to the user
   return render_template('index.html', magnet_state=magnet_state)

#start the web server at localhost on port 80
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=80, debug=True)
