import uuid
from datetime import datetime, time

from flask import Flask, make_response, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vita_win.db"
db = SQLAlchemy(app)


# Database Model for Binary Logger
class AdherenceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), nullable=False)  # Stores the unique browser ID
    status = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    # 1. Get the User ID from the cookie
    user_id = request.cookies.get("vita_win_user")

    # 2. If no cookie exists, we will create one after rendering
    if not user_id:
        user_id = str(uuid.uuid4())

    # 3. Filter logs so users only see THEIR history (Absolute Certainty)
    all_logs = (
        AdherenceLog.query.filter_by(user_id=user_id)
        .order_by(AdherenceLog.timestamp.desc())
        .all()
    )
    last_log = all_logs[0] if all_logs else None

    # 4. Create the response and set the cookie if it was new
    response = make_response(
        render_template("index.html", last_log=last_log, history=all_logs)
    )

    # Set cookie to expire in 1 year
    response.set_cookie("vita_win_user", user_id, max_age=31536000)
    return response


@app.route("/log/<status>", methods=["POST"])
def log_status(status):
    user_id = request.cookies.get("vita_win_user")

    if user_id:
        today_start = datetime.combine(datetime.now().date(), time.min)

        # Only override the log belonging to THIS user
        existing_log = AdherenceLog.query.filter(
            AdherenceLog.user_id == user_id, AdherenceLog.timestamp >= today_start
        ).first()

        if existing_log:
            existing_log.status = status
            existing_log.timestamp = datetime.now()
        else:
            new_log = AdherenceLog(status=status, user_id=user_id)
            db.session.add(new_log)

        db.session.commit()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
