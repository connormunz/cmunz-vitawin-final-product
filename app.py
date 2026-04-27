from datetime import datetime

from flask import Flask, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vita_win.db'
db = SQLAlchemy(app)

# Database Model for Binary Logger 
class AdherenceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(10), nullable=False) # 'Taken' or 'Skipped'
    timestamp = db.Column(db.DateTime, default=datetime.now)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Fetch most recent log to provide "Absolute Certainty" [cite: 13]
    last_log = AdherenceLog.query.order_by(AdherenceLog.timestamp.desc()).first()
    return render_template('index.html', last_log=last_log)

@app.route('/log/<status>', methods=['POST'])
def log_status(status):
    # Log action with timestamp 
    new_log = AdherenceLog(status=status)
    db.session.add(new_log)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)    app.run(debug=True)