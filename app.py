from distutils.log import info
import logging
from logging.handlers import RotatingFileHandler
from pickle import FALSE, TRUE
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
			session["isProfessor"] = True									# QUA VA MESSO TRUE SE L'UTENTE È UN PROFESSORE
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

#Carica la pagina per la creazione di un nuovo corso (solo per prof)
@app.route ('/creaCorso', methods=['GET'])
def creaCorso ():
	if "user" in session and session["isProfessor"] == True:
		pagina = Calendario
		pagina.reset()
		return pagina.render(render_template("creaCorso.html"))
	else:
		return redirect(url_for("login"))

#Carica la pagina di gestione corsi (solo per prof)
@app.route ('/gestisciCorsi', methods=['GET','POST'])
def gestisciCorsi ():
	if "user" in session and session["isProfessor"] == True:
		return render_template("gestisciCorsi.html")
	else:
		return redirect(url_for("login"))

#Effettua il logout dalla sessione
@app.route ('/logout', methods=['GET','POST'])
def logout():
	session.pop("user", None)
	return redirect(url_for("login"))

#Carica la pagina con la pagina con il calendario delle lezioni
@app.route ('/calendario', methods=['GET'])
def calendario ():
	if "user" in session:
		return render_template("calendario.html", isProfessor=session["isProfessor"])
	else:
		return redirect(url_for("login"))

#Carica la pagina di informazioni riguardanti il corso selezionato
@app.route ('/infoCorso', methods=['POST'])
def infoCorso ():
	if "user" in session:
		if request.form.get("idCorso") != None : session["idCorso"] = request.form.get("idCorso")
		iscritto = False														# VARIABILE DA ASSEGNARE A TRUE SE GIà ISCRITTO
		iscrivimi = request.form.get("iscrivimi")											# E FALSE ALTRIMENTI (TRAMITE FUNZIONE APPOSITA IN DATBASE.PY)
		annulla = request.form.get("annulla")
		result=""

		if iscrivimi == "1":
			if iscritto == True:												# VERIFICO CHE L'UTENTE NON SIA GIà ISCRITTO
				result=""
			elif True:															# ISCRIVIAMO L'UTENTE E RITORNIAMO TRUE SE RIUSCITA
				result="effettuata"
			elif True:															# QUA NEL CASO FALLISSE
				result="fallita"
		if annulla == "1":
			if iscritto == False:												# VERIFICO CHE L'UTENTE NON SIA GIà NON ISCRITTO
				result=""
			elif True:															# DISISCRIVIAMO L'UTENTE E RITORNIAMO TRUE SE RIUSCITA
				result="annullata"
			elif True:															# QUA NEL CASO FALLISSE
				result="annullamento-fallito"

		if session["idCorso"] != None:											# DIZIONARIO DA RIEMPIRE CON LE INFO DEL CORSO
			diz = { "id":12,
					"nome": "Organizzazione di eventi culturali L'arte ai giovani! Incontriamo l'arte russa",
					"struttura": "Centro Studi sulle Arti della Russia",
					"posti": "",
					"modalita": "In Presenza",
					"durata": "7 lezioni",
					"iscrizioni": "aperte",
					"postimin": "10",
					"postimax": "110",
					"iscritti": "80",
					"prof": "Edsger Dijkstra",
					"descrizione": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. ",
					"inizio": "15/05/2022"}
			
			return render_template("infoCorso.html", info=diz, isProfessor=session["isProfessor"], result=result, iscritto=iscritto)
		else:
			return render_template("listaCorsi.html", isProfessor=session["isProfessor"])
	else:
		return redirect(url_for("login"))

#Carica la pagina di gestione di un preciso corso
@app.route ('/gestisciCorso', methods=['POST'])
def gestisciCorso ():
	if "user" in session:
		if request.form.get("idCorso") != None : session["idCorso"] = request.form.get("idCorso")

		if session["idCorso"] != None:											# DIZIONARIO DA RIEMPIRE CON LE INFO DEL CORSO
			diz = { "id":12,
					"nome": "Organizzazione di eventi culturali L'arte ai giovani! Incontriamo l'arte russa",
					"struttura": "Centro Studi sulle Arti della Russia",
					"posti": "",
					"modalita": "In Presenza",
					"durata": "7 lezioni",
					"iscrizioni": "aperte",
					"postimin": "10",
					"postimax": "110",
					"iscritti": "80",
					"prof": "Edsger Dijkstra",
					"descrizione": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. ",
					"inizio": "15/05/2022"}
			
			return render_template("gestisciCorso.html", info=diz, isProfessor=session["isProfessor"])
		else:
			return render_template("gestisciCorsi.html", isProfessor=session["isProfessor"])
	else:
		return redirect(url_for("login"))


#Elimina il corso e reinderizza sulla pagina di gestione corsi
@app.route ('/eliminaCorso', methods=['POST'])
def eliminaCorso ():
	if "user" in session and session["idCorso"] != None:
			
		if True:											# NELL'IF VA VERIFICATO SE L'UTENTE È IL PROF PROPRIETARIO DEL CORSO
			tmp = 0 # QUA AL POSTO DI QUESTO ASSEGNAMENTO VA CHIAMATA LA FUNZIONE PER CANCELLARE IL CORSO

		return redirect(url_for("gestisciCorsi"))

	else:
		return redirect(url_for("login"))

#Carica la pagina di gestione di un preciso corso
@app.route ('/modCorso', methods=['POST'])
def modificaCorso ():
	if "user" in session:

		if session["idCorso"] != None:											# DIZIONARIO DA RIEMPIRE CON LE INFO DEL CORSO
			diz = { "id":12,
					"nome": "Organizzazione di eventi culturali L'arte ai giovani! Incontriamo l'arte russa",
					"struttura": "Centro Studi sulle Arti della Russia",
					"posti": "",
					"modalita": "In Presenza",
					"durata": "7 lezioni",
					"iscrizioni": "aperte",
					"postimin": "10",
					"postimax": "110",
					"iscritti": "80",
					"prof": "Edsger Dijkstra",
					"descrizione": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. ",
					"inizio": "15/05/2022"}
			
			return render_template("modCorso.html", info=diz, isProfessor=session["isProfessor"])
		else:
			return redirect(url_for("gestisciCorsi"))
	else:
		return redirect(url_for("login"))

#Carica la pagina con la lista degli iscritti al corso
@app.route ('/listaIscritti', methods=['GET','POST'])
def listaIscritti ():
	if "user" in session:
		if session["idCorso"] != None:											# DIZIONARIO DA RIEMPIRE CON LE INFO DEGLI ISCRITTI AL CORSO
			lista =[    ["Cre_98","Crescenzo","Giustino","giustino@gmail.com","10"], 
						["antonina_sev","Antonina", "Severina","antonina@hotmail.com","0"], 
						["greg_nal","Naldo", "Gregorio","greg@gmail.com","5"], 
						["MariSab0077","Mariano","Sabino","marix@stud.unive.it","9"], 
						["arianna_888","Enrichetta","Arianna", "ari@gmail.com","11"]]

			return render_template("iscritti.html", isProfessor=session["isProfessor"], lista=lista)
	else:
		return redirect(url_for("login"))

#Carica la pagina con le info del profilo
@app.route ('/profilo', methods=['GET','POST'])
def profilo ():
	if "user" in session:
	
		diz = { "id":12,												# DIZIONARIO DA RIEMPIRE CON LE INFO PRIVATE DELL'UTENTE
				"username": "OttoZan",
				"nome": "Carlo",
				"cognome": "Rossi",
				"email": "carlo.rossi@gmail.com",
				"nascita": "30/02/1990",
				"account": "studente",
				"corsi": "10"}

		return render_template("profilo.html", isProfessor=session["isProfessor"], info=diz)
	else:
		return redirect(url_for("login"))
