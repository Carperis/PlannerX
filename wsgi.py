from web_init import app

if __name__ == "__main__":
    print(app.config['MAIL_USERNAME'])
    app.run(port="5000", host="0.0.0.0")
