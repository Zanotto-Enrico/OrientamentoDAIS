import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, render_template

app = Flask ( __name__ )

handler = RotatingFileHandler('./logs/logs.log', maxBytes=1000000, backupCount=5)
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
log.addHandler(handler)
#app.run(host='0.0.0.0', debug=True)

@app.route ('/', methods=['GET', 'POST'])
@app.route ('/login', methods=['GET', 'POST'])
def login ():
	return render_template("login.html")



@app.route ('/register', methods=['GET', 'POST'])
def register ():
	return render_template("register.html")


@app.route ('/home')
def home ():
	return render_template("home.html")
