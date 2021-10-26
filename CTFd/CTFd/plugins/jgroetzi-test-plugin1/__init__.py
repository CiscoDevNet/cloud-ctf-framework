from flask import render_template
import json

def load(app):
    @app.route('/plugins/jgroetzi-test-1', methods=['POST', 'GET'])
    def view_plugins_jgroetzi_test1():
        data = {"some": "value"}
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response
        #return render_template('page.html', content="<h1>jgroetzi Test</h1><p>this is a test</p>")