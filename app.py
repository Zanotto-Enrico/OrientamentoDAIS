import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, render_template, redirect, url_for, session


app = Flask ( __name__ )
app.secret_key = "JG{~^VQnAX8dK*4P'=/XTg^rBhH_psx+/zK9#>YkR_bWd7Av"

#---------- LOG FILES

handler = RotatingFileHandler('./logs/logs.log', maxBytes=1000000, backupCount=5)
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
log.addHandler(handler)
#app.run(host='0.0.0.0', debug=True)

#----------- PAGINE WEB

#Carica la pagina di login
@app.route ('/', methods=['GET','POST'])
@app.route ('/login', methods=['GET','POST'])
def login ():
	if request.method == 'POST':
		request.form.get("username")
		if True:															# QUA VA VERIFICATA LA PASSWORD NEL DATABASE
			session["user"] = request.form.get("username")
			return redirect(url_for("benvenuto"))
		else:
			return render_template("login.html", fallito=True)
	else:
		return render_template("login.html", fallito=False)


#Carica la pagina di registrazione
@app.route ('/register', methods=['GET','POST'])
def register ():
	if request.method == 'POST':
		request.form.get("username")
		if True:															#QUA VA LA VERIFICA DI REGISTRAZIONE NEL DATABASE
			return render_template("register.html", result="effettuata")
		elif True:															# QUA NEL CASO FALLISSE
			return render_template("register.html", result="fallita")
		elif True:															# QUA NEL CASO L'ACCOUNT ESISTA GIA'
			return render_template("register.html", result="giaEsistente")
	else:
		return render_template("register.html")


#Carica la pagina di benvenuto
@app.route ('/benvenuto', methods=['GET'])
def benvenuto ():
	if "user" in session:
		user = session["user"]
		return render_template("benvenuto.html", user=user)
	else:
		return redirect(url_for("login"))

#Carica la pagina con la lista dei corsi disponibili
@app.route ('/listaCorsi', methods=['GET'])
def listaCorsi ():
	if "user" in session:
		return render_template("listaCorsi.html")
	else:
		return redirect(url_for("login"))

#Effettua il logout dalla sessione
@app.route ('/logout', methods=['GET'])
def logout():
	session.pop("user", None)
	return redirect(url_for("login"))


