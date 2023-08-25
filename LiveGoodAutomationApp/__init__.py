from flask import Flask
from LiveGoodAutomationApp import auth, dashboard
from flask_session import Session

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.register_blueprint(auth.auth_bp)
app.register_blueprint(dashboard.dashboard_bp)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

if __name__ == '__main__':
    app.run(debug=True)