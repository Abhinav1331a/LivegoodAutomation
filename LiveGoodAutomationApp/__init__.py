from flask import Flask
from LiveGoodAutomationApp import auth, dashboard

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.register_blueprint(auth.auth_bp)
app.register_blueprint(dashboard.dashboard_bp)

if __name__ == '__main__':
    app.run(debug=True)