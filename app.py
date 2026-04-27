from datetime import datetime, time

from flask import Flask, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vita_win.db"
db = SQLAlchemy(app)


# Database Model for Binary Logger
class AdherenceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(10), nullable=False)  # 'Taken' or 'Skipped'
    timestamp = db.Column(db.DateTime, default=datetime.now)


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    # Fetch all logs to show the history of adherence
    all_logs = AdherenceLog.query.order_by(AdherenceLog.timestamp.desc()).all()

    # Identify the most recent log for the "Current Status" display
    last_log = all_logs[0] if all_logs else None

    return render_template("index.html", last_log=last_log, history=all_logs)


@app.route("/log/<status>", methods=["POST"])
def log_status(status):
    # Define the start of the current day (midnight)
    today_start = datetime.combine(datetime.now().date(), time.min)

    # Check if a log already exists for today
    existing_log = AdherenceLog.query.filter(
        AdherenceLog.timestamp >= today_start
    ).first()

    if existing_log:
        # Override the existing log for today
        existing_log.status = status
        existing_log.timestamp = datetime.now()  # Update timestamp to the latest action
    else:
        # Create a new log if it's the first action of the day
        new_log = AdherenceLog(status=status)
        db.session.add(new_log)

    db.session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
