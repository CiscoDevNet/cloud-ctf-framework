import requests
from flask import Flask, redirect, url_for, request, render_template, jsonify
app = Flask(__name__)


#resp={}
@app.route('/',methods = ['POST', 'GET'])
def url():
    if request.method == 'POST':
        user = request.form['url']
        resp = requests.get(user)
        try:
            return jsonify(resp.text)
        except Exception as e: return e
    else:
        return render_template('index.html')

if __name__ == '__main__':
   app.run(host='0.0.0.0',debug = True)