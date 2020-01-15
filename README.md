# Raspi-backend dev-state-machine

Example for a proper state machine and endpoints.


## Todos:
* QR-scanpage -> regular call to /set_state0 via body-onload javascript
* QR-scanpage -> after recognized qr-code, call /set_state1

## Flow

State-flow:

QR-Scanseite wird aufgerufen
-> ajax-call /set_state0
```
state0:
   door: closed
   magnet: on
   qr code: not recognized


   if qr-code recognized:
      state_fridge 1
      /set_state1

state1:
   door closed
   magnet: off

   if door was opened:
      state_fridge 2

state2:
   door: opened
   magnet: off

   if door is closed again:
      state_fridge 3

State 3:
   door: closed
   magnet: on
   qr code: ...

   show bill
```