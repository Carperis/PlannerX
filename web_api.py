import requests
from flask_mail import Message
from flask import url_for
from web_init import mail, app

# The following are custom modules
import GetPreferenceWeb
import AutoSelection
import AddPlanDetails
import AutoRanking
import GetSeats
import GetSchedulePic


def allow_access(user, other):
    if (hasattr(other, "user_id") and user.id != other.user_id):
        return False
    else:
        return True


def get_google_redirect_uri():
    def get_public_ip():
        try:
            response = requests.get("https://api.ipify.org?format=json")
            if response.status_code == 200:
                data = response.json()
                return data["ip"]
            else:
                print("Request failed with status code:", response.status_code)
                return None
        except Exception as e:
            print("Error:", e)
            return None

    if (get_public_ip() == "158.101.17.48"):
        google_redirect_uri = "https://buplannerx.my.to/google_callback"
    else:
        # google_redirect_uri="http://localhost:5000/google_callback"
        google_redirect_uri = "http://127.0.0.1:5000/google_callback"
    return google_redirect_uri


def send_reset_email(user):
    token = user.get_token()
    msg = Message('Password Reset Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_password_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


def send_verification_email(user):
    print(app.config['MAIL_USERNAME'])
    token = user.get_token()
    msg = Message('Email Verification Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email])
    msg.body = f'''To confirm your email, visit the following link:
{url_for('email_verification_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
