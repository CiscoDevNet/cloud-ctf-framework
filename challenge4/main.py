import requests
import uuid
import logging
from flask import Flask, request, render_template, jsonify
from flask_sessionstore import Session
from flask_session_captcha import FlaskSessionCaptcha
from pymongo import MongoClient

app = Flask(__name__)

# Database Config
# If your mongodb runs on a different port
# change 27017 to that port number
mongoClient = MongoClient('localhost', 27017)

# Captcha Configuration
app.config["SECRET_KEY"] = uuid.uuid4()
app.config['CAPTCHA_ENABLE'] = True

# Set 5 as character length in captcha
app.config['CAPTCHA_LENGTH'] = 5

# Set the captcha height and width
app.config['CAPTCHA_WIDTH'] = 160
app.config['CAPTCHA_HEIGHT'] = 60
app.config['SESSION_MONGODB'] = mongoClient
app.config['SESSION_TYPE'] = 'mongodb'

# Enables server session
Session(app)

# Initialize FlaskSessionCaptcha
captcha = FlaskSessionCaptcha(app)

@app.route('/',methods = ['POST', 'GET'])
def url():
   if request.method == 'POST':
      if captcha.validate():
          user = request.form['url']
          print(user)
          try:
              resp = requests.get(user, stream=True)
              if int(resp.headers.get('Content-Length', 0)) > 1024:
                  return render_template('excp.html')
              chunk = resp.raw.read(1024)
              resp.close() 
              return render_template("index.html",abc=chunk)
          except Exception as e:
              return render_template('excp.html')
      else:
          return render_template('capta.html')
   else:
      return render_template('form.html')

if __name__ == '__main__':
   app.run(host='0.0.0.0',debug = True)