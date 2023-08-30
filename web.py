from web_init import app
import os

if __name__ == "__main__":
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER')
    app.run(debug=True, port="5100")
