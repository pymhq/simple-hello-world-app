from flask import Flask
import os
import time
app = Flask(__name__)
@app.route('/')
def hello_world():
    time.sleep(0.5)
    return 'Hello World! Startdeployment V1'
@app.route('/health')
def health_check():
    return 'health check'
if __name__ == '__main__':
    app.run(threaded=True, host="0.0.0.0", debug=True, port=int(os.environ.get("PORT", 8000)))
