from flask import Flask, render_template, request, send_from_directory, session, jsonify
from flask_session import Session
from gpiozero import Button,LED
import json
import requests

app = Flask(__name__)
sess = Session()

# returns html-table based on requested json-data
@app.route('/get_qrcodes')
def get_qrcodes():
    url = 'http://127.0.0.1:1337/get_qrcodes'
    response = requests.get(url)
    response_dict = json.loads(response.text)
    return(response_dict)

@app.route('/test')
def test_me():
    qrcodes_dict = get_qrcodes()
    qrcodes_amount_items = get_qrcode_amount_items(qrcodes_dict)
    qrcodes_html = get_qrcode_html(qrcodes_dict) 

    test_response = qrcodes_amount_items + qrcodes_html
    return(test_response)

def get_qrcode_amount_items(response_dict):
    return(str(len(response_dict.keys())))

def get_qrcode_html(response_dict):
    
    html_string_body = ""

    for medic_order, medic_name in response_dict.items():
        html_string_body += "<tr><td>" + medic_order + "</td><td>" +  medic_name + "</td></tr>"
        
    html_string = "<table>" + html_string_body + "</table>"

    return(html_string)

#start the web server at localhost on port 80 port=1338
if __name__ == '__main__':
    app.secret_key = "super secr3eet fridge key"
    app.run(host='0.0.0.0', port=1338, debug=False)