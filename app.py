import logging
from logging.handlers import RotatingFileHandler
from pickle import FALSE
from flask import Flask, request, render_template, redirect, url_for, session
import jyserver.Flask as jsf


app = Flask ( __name__ )
app.secret_key = "JG{~^VQnAX8dK*4P'=/XTg^rBhH_psx+/zK9#>YkR_bWd7Av"

#---------- JavaScript

@jsf.use(app)
class Calendario:
	def __init__(self):
		self.giorni = {"lun": 0,"mar": 0,"mer": 0,"gio": 0,"ven": 0,"sab": 0,"dom": 0,}
		self.totalCount = 0
	
	# funzione per mostrare o meno gli orari del giorno di lezione in CreaCorso 
	def showOrHide(self,giorno):
		if(self.giorni[giorno] == 0):
			self.js.document.getElementById(giorno).style.display = "flex"
			self.giorni[giorno] = 1
			self.totalCount +=1
		else:
			self.js.document.getElementById(giorno).style.display = "none"
			self.giorni[giorno] = 0
			self.totalCount -=1
		if(self.totalCount == 0):
			self.js.document.getElementById("almenoUnGiorno").style.display = "inline-block"
		else:
			self.js.document.getElementById("almenoUnGiorno").style.display = "none"

	def reset(self):
		self.giorni = {"lun": 0,"mar": 0,"mer": 0,"gio": 0,"ven": 0,"sab": 0,"dom": 0,}
		self.totalCount = 0

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
			session["isProfessor"] = False									# QUA VA MESSO TRUE SE L'UTENTE È UN PROFESSORE
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
		return render_template("benvenuto.html", user=user, isProfessor=session["isProfessor"])
	else:
		return redirect(url_for("login"))

#Carica la pagina con la lista dei corsi disponibili
@app.route ('/listaCorsi', methods=['GET'])
def listaCorsi ():
	if "user" in session:
		return render_template("listaCorsi.html", isProfessor=session["isProfessor"])
	else:
		return redirect(url_for("login"))

#Carica la pagina con la lista dei corsi disponibili
@app.route ('/creaCorso', methods=['GET'])
def creaCorso ():
	if "user" in session and session["isProfessor"] == True:
		return Calendario.render(render_template("creaCorso.html"))
	else:
		return redirect(url_for("login"))

#Carica la pagina con la lista dei corsi disponibili
@app.route ('/gestisciCorsi', methods=['GET'])
def gestisciCorsi ():
	if "user" in session and session["isProfessor"] == True:
		return render_template("gestisciCorsi.html")
	else:
		return redirect(url_for("login"))

#Effettua il logout dalla sessione
@app.route ('/logout', methods=['GET'])
def logout():
	session.pop("user", None)
	return redirect(url_for("login"))

#Carica la pagina con la pagina con il calendario
@app.route ('/calendario', methods=['GET'])
def calendario ():
	if "user" in session and session["isProfessor"] == False:
		return render_template("calendario.html", isProfessor=session["isProfessor"])
	else:
		return redirect(url_for("login"))

#Carica la pagina di benvenuto
@app.route ('/infoCorso', methods=['POST'])
def infoCorso ():
	if "user" in session:
		idCorso = request.form.get("idCorso")
		if idCorso != None:												# DIZIONARIO DA RIEMPIRE CON LE INFO DEL CORSO
			diz = { "id":12,
					"nome": "Organizzazione di eventi culturali L'arte ai giovani! Incontriamo l'arte russa",
					"struttura": "Centro Studi sulle Arti della Russia",
					"posti": "",
					"modalita": "In Presenza",
					"durata": "30 ore",
					"iscrizioni": "aperte",
					"posti": "80/110",
					"prof": "Edsger Dijkstra",
					"descrizione": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "}
			return render_template("infoCorso.html", info=diz, isProfessor=session["isProfessor"])
		else:
			return render_template("listaCorsi.html", isProfessor=session["isProfessor"])
	else:
		return redirect(url_for("login"))