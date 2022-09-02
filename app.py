from crypt import methods
from distutils.log import info
from locale import delocalize
import logging
from logging.handlers import RotatingFileHandler
#from ossaudiodev import SNDCTL_DSP_BIND_CHANNEL
from pickle import FALSE, TRUE
from xml.dom.minidom import Document
from flask import Flask, request, render_template, redirect, url_for, session
import jyserver.Flask as jsf
from database import *
from datetime import date
from datetime import datetime


app = Flask ( __name__ )
app.secret_key = "JG{~^VQnAX8dK*4P'=/XTg^rBhH_psx+/zK9#>YkR_bWd7Av"

#---------- JavaScript

@jsf.use(app)
class JavaScriptServer:
	def __init__(self):
		self.giorni = {"lun": 0,"mar": 0,"mer": 0,"gio": 0,"ven": 0,"sab": 0,"dom": 0,}
		self.totalCount = 0
	
	def setEdifici(self,diz):
		self.diz = diz
	
	# funzione per mostrare o meno gli orari del giorno di lezione in CreaCorso 
	def showOrHide(self,giorno):
		if(self.giorni[giorno] == 0):
			self.js.document.getElementById(giorno).style.display = "flex"
			self.js.document.getElementById("orario"+giorno).setAttribute('required', '')
			self.giorni[giorno] = 1
			self.totalCount +=1
		else:
			self.js.document.getElementById(giorno).style.display = "none"
			self.js.document.getElementById("orario"+giorno).removeAttribute('required')
			self.giorni[giorno] = 0
			self.totalCount -=1
		if(self.totalCount == 0):
			self.js.document.getElementById("almenoUnGiorno").style.display = "inline-block"
		else:
			self.js.document.getElementById("almenoUnGiorno").style.display = "none"

	def updateAulaDrop(self):
		edificio = self.js.document.getElementById("edificio").value
		self.js.document.getElementById("aula").value = 0
		self.js.document.getElementById("aula").removeAttribute('disabled')
		i = 0
		for aula in self.diz[str(edificio)]:
			self.js.document.getElementById(i).style.display = "inline-block"
			self.js.document.getElementById(i).innerHTML = aula[1]
			self.js.document.getElementById(i).value = aula[0]
			i+=1
		for aula in range(i, 19,1):
			self.js.document.getElementById(aula).style.display = "none"

	def CheckBoxProfessore(self):
		if(self.js.document.getElementById("scuola").disabled == True ):
			self.js.document.getElementById("scuola").removeAttribute('disabled')
			self.js.document.getElementById("scuola").setAttribute('required', '')
		else:
			self.js.document.getElementById("scuola").removeAttribute('required')
			self.js.document.getElementById("scuola").setAttribute('disabled', '')


	def reset(self):
		self.giorni = {"lun": 0,"mar": 0,"mer": 0,"gio": 0,"ven": 0,"sab": 0,"dom": 0,}
		self.totalCount = 0

	def togglePopup(self,id):
		self.js.document.getElementById(id).style.display = "none"

	def setIdCorso(self, id_corso):
		self.id_corso = id_corso

	def downloadList(self):
		print(self.id_corso) #self.id_corso contiene l'id del corso da cui scaricare il certificato

	
	def downloadCert(self):
		session["attestato"] = get_attestatocorso(id_utente=session["user"],id_corso=self.id_corso)
		return redirect(url_for("login"))



#---------- LOG FILES

handler = RotatingFileHandler('./logs/logs.log', maxBytes=1000000, backupCount=5)
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
log.addHandler(handler)
#app.run(host='0.0.0.0', debug=True)

#----------- PAGINE WEB

@app.route('/test_db')
def test_db():
    print(dump())
    return '<h1 style="text-align: center; font-family: Arial"><b>Guardare ouput nella console</b></h1>'

#Carica la pagina di login
@app.route ('/', methods=['GET','POST'])
@app.route ('/login', methods=['GET','POST'])
def login ():
	if request.method == 'POST':

		if check_user_login(username = str(request.form.get("username")), password = str(request.form.get("password"))) == Return.SUCCESS:
			session["user"] = request.form.get("username")
   
			# verifico se l'utente è un professore e setto la relativa variabile di sessione 
   			# di conseguenza
			if is_professor(username = str(request.form.get("username"))) == True:
				session["isProfessor"] = True
			else:
				session["isProfessor"] = False
    
			return redirect(url_for("benvenuto"))
		else:
			return render_template("login.html", fallito=True)
	else:
		return render_template("login.html", fallito=False)


#Carica la pagina di registrazione
@app.route ('/register', methods=['GET','POST'])
def register ():
	if request.method == 'POST':
		
		res = insert_new_user(username = request.form.get("username"), 
                        	  nome = request.form.get("nome"), 
                              cognome = request.form.get("cognome"),
                              email = request.form.get("email"),
                              data_nascita = request.form.get("nascita"),
                              password = request.form.get("password"),
                              is_professore = bool(request.form.get("professore")), 
                              scuolaprovenienza = request.form.get("scuola"))
  
		if res == Return.SUCCESS:															#QUA VA LA VERIFICA DI REGISTRAZIONE NEL DATABASE
			return JavaScriptServer.render(render_template("register.html", result="effettuata"))
		elif res == Return.FAILURE:															# QUA NEL CASO FALLISSE
			return JavaScriptServer.render(render_template("register.html", result="fallita"))
		elif res == Return.EXISTS:															# QUA NEL CASO L'ACCOUNT ESISTA GIA'
			return JavaScriptServer.render(render_template("register.html", result="giaEsistente"))
	else:
		return JavaScriptServer.render(render_template("register.html"))


#Carica la pagina di benvenuto
@app.route ('/benvenuto', methods=['GET'])
def benvenuto ():
	if "user" in session:
		user = session["user"]
		return render_template("benvenuto.html", user=user, isProfessor=session["isProfessor"], benvenuto=1)
	else:
		return redirect(url_for("login"))

#Carica la pagina con la lista dei corsi disponibili
@app.route ('/listaCorsi', methods=['GET','POST'])
def listaCorsi ():
	if "user" in session:
		if(request.method == 'POST'):
			listaDiDiz = get_lista_corsi(None,request.form.get("filter"),None)
		else:
			listaDiDiz = get_lista_corsi(None,None,None)
		return render_template("listaCorsi.html",info=listaDiDiz , isProfessor=session["isProfessor"], soloIscritti=False)
	else:
		return redirect(url_for("login"))

		
#Carica la pagina con la lista dei corsi a cui ci si è iscritti
@app.route ('/iTuoiCorsi', methods=['GET','POST'])
def iTuoiCorsi ():
	if "user" in session:
		listaDiDiz = get_lista_corsi(None,None,session["user"])
		return render_template("listaCorsi.html",info=listaDiDiz , isProfessor=session["isProfessor"], soloIscritti=True)
	else:
		return redirect(url_for("login"))

#Carica la pagina per la creazione di un nuovo corso (solo per prof)
@app.route ('/creaCorso', methods=['GET', 'POST'])
def creaCorso ():
	if "user" in session and session["isProfessor"] == True:
		diz = get_edifici_aule()
		pagina = JavaScriptServer
		pagina.setEdifici(diz)
		pagina.reset()
		collisioni = []
		if request.method == 'POST':
			collisioni = insert_new_corso(nome = request.form.get("name"),
						descrizione = request.form.get("description"),
						is_online = request.form.get("tipologia")=="online",
						min_stud = request.form.get("num-min"),
						max_stud = request.form.get("num-max"),
						docente = session["user"],
						id_aula = request.form.get("aula"),
						first_week = request.form.get("firstWeek"),
						last_week = request.form.get("lastWeek"),
						orari = [request.form.get("orariolun"),request.form.get("orariomar"),request.form.get("orariomer"),
								request.form.get("orariogio"),request.form.get("orarioven"),request.form.get("orariosab"),None])
			if(collisioni == None):
				return pagina.render(render_template("creaCorso.html",diz=diz,errore=1,riusito=0))
			elif(len(collisioni) > 0):
				return pagina.render(render_template("creaCorso.html",diz=diz,collisioni = get_info_lezioni(lezioni=collisioni), errore=0,riusito=0))
			else:
				return pagina.render(render_template("creaCorso.html", diz=diz, errore=0,riuscito=1))
		else:
			return pagina.render(render_template("creaCorso.html", diz=diz, errore=0,riusito=0))

	else:
		return redirect(url_for("login"))

#Carica la pagina di gestione corsi (solo per prof)
@app.route ('/gestisciCorsi', methods=['GET','POST'])
def gestisciCorsi ():
	if "user" in session and session["isProfessor"] == True:
		listaDiDiz = get_lista_corsi(session["user"],None,None)
		return render_template("gestisciCorsi.html",info=listaDiDiz , isProfessor=session["isProfessor"])
	else:
		return redirect(url_for("login"))

#Effettua il logout dalla sessione
@app.route ('/logout', methods=['GET','POST'])
def logout():
	session.pop("user", None)
	return redirect(url_for("login"))

#Carica la pagina con la pagina con il calendario delle lezioni
@app.route ('/calendario', methods=['GET','POST'])
def calendario ():
	if "user" in session:
		if ("date" not in session):
			session["date"] = date.today().strftime("%Y-%m-%d")
		listaDiDiz = None; 
		errore=successo=richiedi=False

		if(request.method == 'POST'):
			if(request.form.get("date") != None):
				session["date"] = request.form.get("date")
			if(request.form.get("idLezione") != None):
				session["idLezione"] = request.form.get("idLezione")
				richiedi = True
			if(request.form.get("secret") != None):
				if(conferma_partecipazione(session["idLezione"], request.form.get("secret"),session["user"]) == True):
					successo= True
				else:
					errore = True
		data = session["date"]
		listaDiDiz = get_lezioni_giorno(session["user"], data)
 
		pagina = JavaScriptServer	
		return pagina.render(render_template("calendario.html", info=listaDiDiz ,isProfessor=session["isProfessor"],data=datetime.strptime(data,'%Y-%m-%d').strftime("%d/%m/%Y"),errore=errore,successo=successo,richiedi=richiedi))
	else:
		return redirect(url_for("login"))

#Carica la pagina di informazioni riguardanti il corso selezionato
@app.route ('/infoCorso', methods=['POST'])
def infoCorso ():
	if "user" in session:
		if request.form.get("idCorso") != None : session["idCorso"] = request.form.get("idCorso")
		iscritto = check_iscrizione(session["idCorso"], session["user"])														# VARIABILE DA ASSEGNARE A TRUE SE GIà ISCRITTO
		iscrivimi = request.form.get("iscrivimi")											# E FALSE ALTRIMENTI (TRAMITE FUNZIONE APPOSITA IN DATBASE.PY)
		annulla = request.form.get("annulla")
		result=""
		if iscrivimi == "1":
			if iscritto == True:												# VERIFICO CHE L'UTENTE NON SIA GIà ISCRITTO
				result = "Già iscritto"
			elif gestione_iscriz(session["idCorso"], session["user"], "I") == True:
				result = "effettuata"
				iscritto = True
			else:
				result = "fallita"
		if annulla == "1":
			if iscritto == False:												# VERIFICO CHE L'UTENTE NON SIA GIà NON ISCRITTO
				result="Già disiscritto"
			elif gestione_iscriz(session["idCorso"], session["user"], "A") == True:
				result = "annullata"
				iscritto = False
			else:
				result = "annullamento-fallito"
		
		certificato = has_user_completed_course(session["idCorso"], session["user"])

		if session["idCorso"] != None:
			#/infoCorso richiedo le informazioni relative al corso da analizzare tramite opportuno metodo
			diz = get_info_corso(id_corso = session["idCorso"])
			
			return render_template("infoCorso.html", info=diz, isProfessor=session["isProfessor"], result=result, iscritto=iscritto, certificato=certificato)
		else:
			return redirect(url_for("listaCorsi"))
	else:
		return redirect(url_for("login"))

#Carica la pagina di gestione di un preciso corso
@app.route ('/gestisciCorso', methods=['POST'])
def gestisciCorso ():
	if "user" in session:
		if request.form.get("idCorso") != None : session["idCorso"] = request.form.get("idCorso")

		if session["idCorso"] != None:
			diz = get_info_corso(id_corso = session["idCorso"])
			pagina = JavaScriptServer
			pagina.setIdCorso(session["idCorso"])
			
			return pagina.render(render_template("gestisciCorso.html", info=diz, isProfessor=session["isProfessor"]))
		else:
			return redirect(url_for("gestisciCorsi"))
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
		diz = get_info_utente(session["user"])

		return render_template("profilo.html", isProfessor=session["isProfessor"], info=diz)
	else:
		return redirect(url_for("login"))

#Carica la pagina dove viene generato il pdf del certificato
@app.route('/certificato', methods=['GET','POST'])
def certificato():
	if "user" in session:
		pdf =  get_attestatocorso(id_utente=session["user"],id_corso=session["idCorso"])
		response = response = make_response(pdf.output(dest='S').encode('latin-1'))
		response.headers['Content-Type'] = 'application/pdf'
		response.headers['Content-Disposition'] = 'inline; filename=certificato.pdf'
	return response

#Carica la pagina dove viene generato il pdf con le chiavi delle lezioni di un certo corso
@app.route('/chiavi', methods=['GET','POST'])
def chiavi():
	if "user" in session:
		pdf =  get_pdfchiavi(session["idCorso"])
		response = response = make_response(pdf.output(dest='S').encode('latin-1'))
		response.headers['Content-Type'] = 'application/pdf'
		response.headers['Content-Disposition'] = 'inline; filename=chiavi.pdf'
		return response

@app.route('/test', methods=['GET','POST'])
def test():
    session["idCorso"] = 1
    print(session["idCorso"])
    pdf = get_pdfchiavi(session["idCorso"])
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=chiavi.pdf'
    return response