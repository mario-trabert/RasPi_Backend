from gpiozero import Button

inputdevice = Button("GPIO18")
while True:
  
    print inputdevice.value

