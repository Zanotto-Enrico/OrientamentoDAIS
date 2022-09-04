from cmath import cos
from gettext import install
from fpdf import FPDF
from flask import make_response
import hashlib
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
from datetime import *
import random
import string

#-------------------------------------------------------------
# VARIABILI GLOBALI CHE PERMETTONO DI CONNETTERSI AL DATABASE 
# Se si necessita di cambiare la modalità di connessione basta
# modificare il contenuto di queste due variabili
address = "orientamentodais.com"#"orientamentodais.com"
database = "orientamento"
# per il locale usa '127.0.0.1:5432', 'orientamentodais_locale'
#-------------------------------------------------------------

Base = declarative_base()

# definito un tipo enumerativo per la gestione dei casi che possono verificarsi quando
# viene eseguita una query: può avere successo, può fallire o l'elemento può già esistere 
# (vedere ad esempio il caso degli utenti)
class Return(Enum):
    SUCCESS = 1
    FAILURE = 2
    EXISTS = 3


# DEFINIZIONE DELLE CLASSI CHE VANNO A RAPPRESENTARE LE TABELLE DEL DB
# Per ciascuna viene anche implementato il metodo di pretty-printing a scopo di sviluppo
# +----
class Edifici(Base):
    __tablename__ = "edifici"
    
    id_edificio = Column(Integer, primary_key = True)
    nome = Column(String)
    indirizzo = Column(String)
    
    def __repr__(self):
        return "<Edificio (nome: %s, indirizzo: %s)>" % (self.nome, self.indirizzo) 
    
class IscrizioniCorsi(Base):
    __tablename__ = "iscrizionicorsi"
    
    id_corso = Column(Integer, primary_key = True)
    username = Column(String, primary_key = True)
    
    def __repr__(self):
        return "<IscrizioneCorso (idcorso: %d, username: %s)>" % (self.id_corso, self.username)
    
class Lezioni(Base):
    __tablename__ = "lezioni"
    
    id_lezione = Column(Integer, primary_key = True)
    data = Column(Date)
    secret_code = Column(String)
    orario_inizio = Column(Time)
    orario_fine = Column(Time)
    id_corso = Column(Integer)
    
    def __repr__(self):
        return "<Lezione (Inizio: %s, Fine: %s)>" % (self.orario_inizio, self.orario_fine)
    
class Partecipanti(Base):
    __tablename__ = "partecipanti"
    
    username = Column(String, primary_key = True)
    scuola_provenienza = Column(String)
    
    def __repr__(self):
        return "<Partecipante (username: %s, scuola: %s)>" % (self.username, self.scuola_provenienza)
    
class PartecipazioniLezione(Base):
    __tablename__ = "partecipazionilezione"
    
    id_lezione = Column(Integer, primary_key = True)
    username = Column(String, primary_key = True)
    
    def __repr__(self):
        return "<PartecipazioneLezione (id_lezione: %d, username: %s)>" % (self.id_lezione, self.username)
    
class Utenti(Base):
    __tablename__ = "utenti"
    
    username = Column(String, primary_key = True)
    nome = Column(String)
    cognome = Column(String)
    email = Column(String)
    nascita = Column(Date)
    password = Column(String)
    
    def __repr__(self):
        return "<Utente (username: %s, nome: %s, congome: %s)>" % (self.username, self.nome, self.cognome)

class Aule(Base) :
    __tablename__ = 'aule'

    id_aula = Column(Integer, primary_key = True)
    nome = Column(String)
    id_edificio = Column(Integer)

    def __repr__(self):
        return "<Aula(nome: %s)>" % (self.nome)
    
class Docenti(Base):
    __tablename__ = 'docenti'
    
    username = Column(String, primary_key = True)
    
    def __repr__(self):
        return "<Docente (nome: %s)>" % self.username
    
class Corsi(Base):
    __tablename__ = 'corsi'
    
    id_corso = Column(Integer, primary_key = True)
    nome = Column(String)
    descrizione = Column(String)
    is_online = Column(Boolean)
    min_partecipanti = Column(Integer)
    max_partecipanti = Column(Integer)
    docente = Column(String)
    id_aula = Column(Integer)
    
    def __repr__(self):
        return "<Corso (nome: %s, descrizione: %s, docente: %s)>" % (self.nome, self.descrizione, self.docente)

   
# + - - - - - - - - - - +
# |        METODI       |
# + - - - - - - - - - - +

#---- Metodo utilizzato per inizializzare la sessione di connessione alla base di dati
def initialize_db (user):
    try:
        engine = None
        if user == 'admin':
            engine = create_engine('postgresql+psycopg2://admin:yQ9q8XgWYzYQv3RWccc3@' + address + '/' + database)
        elif user == 'utente':
            engine = create_engine('postgresql+psycopg2://utente:CLgC92dK9DbEkrMSRS4j@' + address + '/' + database)
        elif user == 'prof':
            engine = create_engine('postgresql+psycopg2://prof:7TpSZbBYJTcGUxxyqtSD@' + address + '/' + database)
        else:
            print('Utente non esistente')

        maker = sessionmaker(bind = engine)
        global session
        session = maker()
        return True
    except:
        print("[*] - Errore nella creazione della sessione\n" + 
              "      Vedi metodo initialize_db(...)")
        return False

#---- Metodo utilizzato per verificare se è già stata creata una connessione valida alla 
#     base di dati, se così non è richiama il metodo di inizializzazione
def check_session():
    if 'session' not in globals():
        initialize_db(session['access'])
    

#---- Metodo utilizzato per inserire un nuovo utente nella base di dati
def insert_new_user(username, nome, cognome, email, data_nascita, password, is_professore, scuolaprovenienza = ''):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
        
    try:
        # prima di tutto genero l'hash della nuova password
        passwordHash = hashlib.sha256(password.encode()).hexdigest()
        # creo il nuovo oggetto da inserire nella tabella utenti
        new_utente = Utenti(username = username, nome = nome, cognome = cognome, email = email, nascita = data_nascita, password = passwordHash)
        
        # controllo anche a mano se è già presente l'utente che si vuole inserire in modo 
        # da ritornare il tipo di ritorno EXISTS, ciò non sarebbe possibile senza dato che 
        # verrebbe propagata una eccezione dal metodo di inserimento che sarebbe sfociata nel 
        # ramo except del try e avrebbe restituito un generico FAILURE
        for user in get_users():
            if (user.username == username):
                return Return.EXISTS
        
        # se l'utente non è già presente aggiungo alla base di dati ed eseguo subito un commit
        # per riflettere l'operazione: operazione necessaria per fare in modo che successivamente
        # si sia in grado di trovare la chiave all'interno dei tipi specializzati docenti e partecipanti
        session.add(new_utente)
        session.commit()
        
        # aggiungo alla tabella docenti lo username dell'utente se esso è un docente
        # altrimenti aggiungo username e scuola alla tabella relativa ai partecipanti
        ret = True
        if (is_professore == True):
            try:
                new_docente = Docenti(username = username)
                session.add(new_docente)
                session.commit()
            except:
                print("[!] - Errore nella creazione dell'utente specializzato docente\n" +
                        "      Vedi metodo insert_new_user(...)")
                ret = False
        else:
            try:
                new_partecipante = Partecipanti(username = username, scuola_provenienza = scuolaprovenienza)
                session.add(new_partecipante)
                session.commit()
            except:
                print("[!] - Errore nella creazione dell'utente specializzato partecipante\n" +
                      "      Vedi metodo insert_new_user(...)")
                ret = False

        # se non ho inserito correttamente il tipo specializzato faccio un rollback anche 
        # del commit dell'utente generico precedentemente inserito nella tabella utenti
        if (ret == False):
            session.rollback()
        
        # se arrivo qui vuol dire che tutti gli inserimenti sono avvenuti con successo
        return Return.SUCCESS
    except Exception as e:
        print("[!] - Utente già presente nella base di dati o errore nell'inserimento!\n" +
              "      Vedi metodo insert_new_user()\n" +
              "      Per maggiori info:\n")
        print(e)
        return Return.FAILURE
    

#---- Metodo che contiene una query che legge tutti i gli utenti della base di dati
#     e ne restituisce una lista di oggetti Utenti
def get_users():
    return list(session.query(Utenti).all())


#---- Metodo che contiene una query che legge tutti i docenti della base di dati e ne
#     restituisce una lista di oggetti Docenti
def get_docenti():
    return list(session.query(Docenti).all())


#---- Metodo utile per verificare le credenziali fornite in fase di accesso e quindi per stabilire
#     se l'utente può avere accesso all'area privata del sito
def check_user_login(username, password):
    # inizializzo la connessione al database
    initialize_db('admin')
    
    for u in get_users():
        # prima di tutto genero l'hash della nuova password e poi comparo gli hash
        passwordHash = hashlib.sha256(password.encode()).hexdigest()
        if (u.username == username and u.password == passwordHash):
            return Return.SUCCESS
    
    return Return.FAILURE


#---- Metodo per la creazione di un corso e per la generazione delle relative lezioni
#     Ritorna la lista con data e ora delle lezioni che non possono essere create per via
#     di mancata disponibilià dell'aula.   Se la lista è vuota il corso è stato creato
def insert_new_corso(nome, descrizione, is_online, min_stud, max_stud, docente, id_aula, first_week, last_week, orari):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    
    orariFine = {"8:00:00":"9:30:00","9:30:00":"11:00:00","11:00:00":"12:30:00","12:30:00":"14:00:00","14:00:00":"15:30:00","15:30:00":"17:00:00"}
    inizio = datetime.fromisocalendar(year=int(first_week.split('-')[0]),week=int(first_week.split('W')[1]),day=1)
    fine = datetime.fromisocalendar(year=int(last_week.split('-')[0]),week=int(last_week.split('W')[1]),day=7)
    
    
    if(int(min_stud) > int(max_stud) or (fine - inizio).total_seconds() < 0):
        return None

    # verifico che le aule siano libere prima di creare nuove lezioni
    collisioni = check_disponibilita_aula(id_aula,orari, inizio.strftime("%Y-%m-%d"), fine.strftime("%Y-%m-%d") )
    
    if(len(collisioni) > 0):
        return collisioni

    # creo il corso effettivo con le relative informazioni e lo aggiungo alla base di dati
    new_corso = Corsi(nome=nome, descrizione=descrizione, is_online=is_online, min_partecipanti=min_stud, max_partecipanti=max_stud, docente=docente, id_aula=id_aula)
    session.add(new_corso)
    session.commit()

    # scorro tutte le date scelte e creo le varie lezioni del corso
    while(inizio <= fine):
        if(orari[inizio.isoweekday()-1] != None):
            new_lesson = Lezioni(id_corso=new_corso.id_corso,secret_code=get_random_string(10),data=inizio.strftime("%Y-%m-%d"),orario_inizio=orari[inizio.isoweekday()-1],orario_fine=orariFine[orari[inizio.isoweekday()-1]])
            session.add(new_lesson)
            session.commit()
        inizio = inizio + timedelta(days = 1)
    
    return collisioni

#---- Metodo per l'eliminazione di un corso con le relative lezioni.
#     Eliminando le lezioni rimuoverà anche le partecipazioni alle lezioni
def remove_corso(idCorso):
    result = session.query(Corsi).filter_by(id_corso = idCorso).delete()
    session.commit()


#---- Metodo utile per generare un pdf contenente tutte le chiavi relative alle lezioni di un
#     determinato corso, identificato mediante il parametro idcorso
def get_pdfchiavi(idcorso):
    
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_author("Università Ca' Foscari - Venezia")
        pdf.set_title("Chiavi delle lezioni")
        
        pdf.set_font("Arial", size = 26)
        corso = get_info_corso(id_corso=str(idcorso))
        pdf.cell(188,20,'%s' % (str(corso["nome"])),align='C',ln=1)
        pdf.cell(180,10,' ',align='C',ln=1)
        pdf.set_font("Arial", size = 12)
        pdf.cell(180, 10, txt=corso["descrizione"], align='C', ln = 1)
        pdf.cell(180, 10, txt='Di seguito le chiavi delle lezioni:', align='L', ln = 1)
        
        # scorro tutte le lezioni di un certo corso e ne aggiungo il relativo codice segreto
        # al pdf
        i = 0
        for l in session.query(Lezioni).filter_by(id_corso = idcorso).all():
            pdf.cell(180, 10, txt='   -  Lezione %s: %s' % (str(i), l.secret_code), align='L', ln=1)
            i += 1
        pdf.cell(180, 40, txt = ' ', ln = 1)
        pdf.image("static/imgs/unive.png",x=80)
            
        return pdf
        
    except Exception as e:
        print("[!] - Errore nella generazione del pdf con i codici delle lezioni. Per maggiori info:")
        print(e)
        

#---- Metodo creato con lo scopo di confermare la partecipazione ad una data lezione
#     tramite il codice segreto immesso dall'utente
#     ritorna True o False in base al successo dell'operazione
def conferma_partecipazione(idLezione, secret, username):
    if(session.query(PartecipazioniLezione).filter(PartecipazioniLezione.id_lezione == idLezione and PartecipazioniLezione.username == username).count() > 0):
        return True
    if(secret == session.query(Lezioni.secret_code).filter(Lezioni.id_lezione == idLezione).first()[0]):
        partecipazione  = PartecipazioniLezione(id_lezione=idLezione,username=username)
        session.add(partecipazione)
        session.commit()
        return True
    return False
        
    

#---- Metodo utile per generare il pdf relativo all'attestato di partecipazione al corso identificato
#     da id_corso per l'utente identificato da id_utente. Il certificato può essere rilasciato però
#     solo se lo studente ha partecipato 
def get_attestatocorso(id_utente, id_corso):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    
    # il certificato può essere rilasciato solo se lo studente ha completato il corso in questione
    if has_user_completed_course(id_corso=id_corso, username=id_utente):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_author("Università Ca' Foscari - Venezia")
            pdf.set_title("Attestato di partecipazione")
            
            corso = get_info_corso(id_corso=id_corso)
            utente = get_info_utente(username=id_utente)
            pdf.set_font("Arial", size = 26)
            pdf.cell(180,40,'',align='C',ln=1)
            pdf.cell(188,20,'Attestato di partecipazione',align='C',ln=1)
            pdf.set_font("Arial", size = 14)
            pdf.cell(188,20,'Università Ca\' Foscari',align='C',ln=1)
            pdf.cell(180,10,'',align='C',ln=1)
            pdf.set_font("Arial", size = 19)
            pdf.cell(180, 10, txt = ("Si attesta che lo studente %s" % (utente["nome"] + utente["cognome"])),align='C',ln=1)
            pdf.cell(180, 10, txt = ("ha partecipato al corso %s" % ( corso["nome"])),align='C',ln=1)
            pdf.cell(180, 10, txt = ("tenuto dal professor %s" % ( corso["prof"])),align='C',ln=1)
            pdf.cell(180,20,'',align='C',ln=1)
            pdf.set_font("Arial", size = 17)
            pdf.cell(180, 10, txt="Di seguito una breve descrizione del corso seguito:", ln=1,align='C')
            pdf.cell(180, 10, txt=corso["descrizione"], ln=1,align='C')
            pdf.cell(180,20,'',align='C',ln=1)
            pdf.image("static/imgs/unive.png",x=80)
            
            return pdf
        except Exception as e:
            print("[!] - Errore nella generazione del file PDF\n      Per maggiori info:\n")
            print(e)
            
        return False
    
    

# + - - - - - - - - - - +
# | METODI DI SUPPORTO  |
# + - - - - - - - - - - +

#---- Metodo utile per verificare se un certo username, e quindi utente, del sito sia registrato
#     come docente o meno restituendone il risultato della verifica
def is_professor(username):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    
    for u in get_docenti():
        if u.username == username:
            return True
    return False

#---- Metodo utile per resituire direttamente la struttura in cui un'aula (identificata dall'id
#     passato come parametro) è situata
def get_struttura(id_aula):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    return session.query(Edifici).filter_by(id_edificio = 
                                            session.query(Aule).filter_by(id_aula = id_aula).first().id_edificio).first()

#---- Metodo utile per restituire il numero di iscritti ad un corso dato il suo id
def get_iscritti(id_corso):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    return session.query(IscrizioniCorsi).filter_by(id_corso = id_corso).count()

#---- Metodo utile per restituire il numero di lezioni in cui un corso (identificato dall'id
#     passato come argomento) è suddiviso 
def get_nlezioni(id_corso):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    return session.query(Lezioni).filter_by(id_corso = id_corso).count()

#---- Metodo utile per restituire il numero di lezioni di un determinato corso
#     in cui un utente ha dimostrato di aver preso parte
def get_npartecipazioni(id_corso, username):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    return session.query(Lezioni,PartecipazioniLezione).filter(and_(Lezioni.id_corso == id_corso, PartecipazioniLezione.username == username, 
                                                                    PartecipazioniLezione.id_lezione == Lezioni.id_lezione)).count()

#---- Metodo che, passato l'username dello studente, restituisce il numero di corsi ai quali
#     appare iscritto
def get_numeroiscrizioni(username):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    return session.query(IscrizioniCorsi).filter_by(username = username).count()

#---- Metodo che, dato un professore, restituisce il numero di corsi da lui tenuti
def get_corsitenuti(prof):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    return session.query(Corsi).filter_by(docente = prof).count()


def check_iscrizione(id_Corso, id_Studente):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    if(session.query(IscrizioniCorsi).filter(and_(IscrizioniCorsi.id_corso == id_Corso, IscrizioniCorsi.username == id_Studente)).first() != None):
        return True
    return False

#---- Metodo che, passato l'username dello studente e l'id di un corso restituisce True
#     se l'utente ha partecipato a tutte le lezioni, False altrimenti
def has_user_completed_course(id_corso, username):
    return get_nlezioni(id_corso) == get_npartecipazioni(id_corso,username)

#---- Metodo avente il compito di aggiungere una iscrizione ad un corso (corsoidentificato 
#     da id_corso e utente da username) se il valore contenuto nella variabile tipo è uguale 
#     a 'I'. Rimuove invece l'iscrizione se il contenuto della variabile tipo è 'A'
def gestione_iscriz(id_corso, username, tipo):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    if(tipo == "I"):   
        try:
            result = IscrizioniCorsi(id_corso = id_corso, username = username)
            session.add(result)
            # rendo subito effettive le modifiche sulla base di dati tramite un commit
            session.commit()
            res = True
        except Exception as e:
            print("[!] - Errore nell'operazione!\n      Di seguito per maggiori informazioni:\n")
            print(e)
            res = False
    if(tipo == "A"):
        try:
            result = session.query(IscrizioniCorsi).filter_by(id_corso = id_corso, username = username).delete()
            # rendo subito effettive le modifiche sulla base di dati tramite un commit
            session.commit()
            res = True
        except Exception as e:
            print("[!] - Errore nell'operazione!\n      Di seguito per maggiori informazioni:\n")
            print(e)
            res = False
    
    return res

#---- Metodo che verifica la disponibilità di un aula di poter ospitare una lezione
#     Ritorna False se l'aula è gia occupata in quella data e ora, True altrimenti
def check_disponibilita_aula(id_aula, orari, dataInizio, dataFine):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    collisioni = []
    for dayofweek in range(1,7):
        result = None
        if(orari[dayofweek-1] != None):
            result = session.query(Lezioni.id_lezione
                   ).filter(and_(Lezioni.id_corso == Corsi.id_corso, Aule.id_aula == Corsi.id_aula, Aule.id_aula == id_aula)
                   ).filter(Lezioni.orario_inizio == orari[dayofweek-1]
                   ).filter(and_(Lezioni.data.between(dataInizio,dataFine))
                   ).filter(func.extract('dow',Lezioni.data) == dayofweek).all()
        if(result != None):
            for item in result: 
                collisioni.append(item[0])
    return collisioni

# + - - - - - - - - - - - - - - - - - - - - - +
# | METODI PER RESTITUZIONE DIZIONARI O LISTE |
# + - - - - - - - - - - - - - - - - - - - - - +


#---- Metodo che restituisce un dizionario rifornito di informazioni dettagliate relative 
#     ad un singolo corso, quello passato come id
def get_info_corso(id_corso):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    
    try:
        # eseguo una query alla base di dati per ricevere l'oggetto corso filtrato per 
        # l'id richiesto
        corso = session.query(Corsi).filter_by(id_corso = str(id_corso)).first()
        prof = session.query(Utenti).filter(Utenti.username == corso.docente).first()
        
        struttura = get_struttura(id_aula=int(corso.id_aula))
        
        # traduco la modalità da valore booleano a stringa da inserire poi nel dizionario
        modalita = ""
        if corso.is_online == True:
            modalita = "In Presenza"
        else:
            modalita = "Online"
        
        return { "id": corso.id_corso,
                "nome": corso.nome,
                "struttura": struttura.nome + " - " + struttura.indirizzo,
                "modalita": modalita,
                "durata": str(get_nlezioni(corso.id_corso)) + " lezioni",
                "iscrizioni": "Aperte",
                "postimin": corso.min_partecipanti,
                "postimax": corso.max_partecipanti,
                "iscritti": get_iscritti(id_corso=corso.id_corso),
                "prof": prof.nome + " " + prof.cognome,
                "descrizione": corso.descrizione,
                "inizio": "15/05/2022"}
    except Exception as e:
        print("[!] - Errore nella restituzione delle informazioni relative al corso con id: " + id_corso + ", verificare il metodo get_info_corso(...)\n")
        print(e)
    

#---- Metodo che, dato l'id di un corso, restituisce il dati dei partecipanti 
#     con il numero di lezioni frequentate
def get_dati_iscritti(idCorso):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    info =  session.query(Utenti.username,Utenti.nome,Utenti.cognome,Utenti.email, func.count(Utenti.username)).filter(
                    and_(IscrizioniCorsi.id_corso == idCorso, PartecipazioniLezione.id_lezione == Lezioni.id_lezione, 
                            Lezioni.id_corso == IscrizioniCorsi.id_corso, PartecipazioniLezione.username == IscrizioniCorsi.username, IscrizioniCorsi.username == Utenti.username)).group_by(
                    Utenti.username,Utenti.nome,Utenti.cognome,Utenti.email).all()
                            
    print("-----------------------\n")
    print(info)
    return info


#---- Metodo che restituisce una lista di dizionari contenenti alcune informazioni essenziali per
#     rappresentare in maniera minimal le informazioni di un corso
def get_lista_corsi(prof,filter,user):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    
    # eseguo una query alla base di dati per ricevere l'oggetto corso filtrato per 
    # il professore se richiesto
    
    query = session.query(Corsi)
    if(prof != None):
        query = query.filter(Corsi.docente==prof)
    if(user != None):
        query = query.filter(Corsi.id_corso ==  IscrizioniCorsi.id_corso).filter(IscrizioniCorsi.username == user)
    if(filter != None):
        query = query.filter(Corsi.nome.ilike("%"+filter+"%"))
    
    corsi = list(query.all())

    # creo la lista di dizionari
    infos = []
    for c in corsi:
        info = {}
        
        info["id"] = c.id_corso
        info["nome"] = c.nome
        struttura = get_struttura(id_aula=c.id_aula)
        info["struttura"] = struttura.nome + " - " + struttura.indirizzo
        
        if c.is_online == True:
            info["modalita"] = "Online"
        else:
            info["modalita"] = "In Presenza"
        
        info["durata"] = str(get_nlezioni(id_corso=c.id_corso)) + " lezioni"
        
        info["iscrizioni"] = "Aperte"                                               # DA CAMBIARE UNA VOLTA MODIFICATA STRUTTURA DB
        
        info["postimax"] = c.max_partecipanti
        
        info["iscritti"] = get_iscritti(id_corso=c.id_corso)
        
        infos.append(info)
        
    return infos

#---- Metodo avente il compito di restituire tutte le informazioni relative ad un utente, a prescindere
#     dal suo tipo (docente o studente)
def get_info_utente(username):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    
    try:
        user = session.query(Utenti).filter_by(username = username).first()
        
        corsi = 0
        tipo_utente = ""
        # se l'utente è un professore salvo il numero di corsi da lui tenuti e il suo tipo di utente 
        # ("Professore") mentre per gli studenti, oltre al loro tipo, salvo il numero di corsi ai 
        # quali sono iscritti
        if is_professor(username = user.username):
            corsi = get_corsitenuti(user.username)
            tipo_utente = "Professore"
        else:
            corsi = get_numeroiscrizioni(user.username)
            tipo_utente = "Studente"
            
        return {    
                    "username": user.username,
                    "nome": user.nome,
                    "cognome": user.cognome,
                    "email": user.email,
                    "nascita": user.nascita,
                    "account": tipo_utente,
                    "corsi": corsi 
                }
        
    except Exception as e:
        print("[!] - Errore nella restituzione delle informazioni relative all'utente con username: " + username + ", verificare il metodo get_info_utente(...)")
        print(e)

#---- Metodo utilizato che restituisce una lista contenente le lezioni con le relative info
#     necessita come parametro un'array con gli id delle lezioni richieste
def get_info_lezioni(lezioni):
    info = []
    for id in lezioni:
        info.append(session.query(Lezioni.data,Lezioni.orario_inizio,Lezioni.orario_fine).filter(Lezioni.id_lezione == id).all())
    return info


#---- Metodo utilizato per generare codici random, utile per creare le chiavi di
#     conferma partecipazione delle lezioni
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return(result_str)

#---- Metodo avente il compito di restituire un dizionario contenente per ogni edificio (chiave
#     del dizionario stesso) la lista delle aule (id e nome) ad esso appartenenti
def get_edifici_aule():
    res = {}
    # scorro tutti gli edifici presenti
    for ed in session.query(Edifici.id_edificio, Edifici.nome).all():
        lista = []
        # scorro tutte le aule per tale edificio
        for aula in session.query(Aule.id_aula, Aule.nome).filter(Aule.id_edificio == ed[0]).all():
            # aggiungo una ad una tutte le classi, con relativo id e nome, alla lista
            lista.append((aula[0],aula[1]))
        
        # salvo nel dizionario nella posizione data dal nome dell'edificio la lista 
        # contenente tutte le aule
        res[ed[1]] = lista
    return res



def get_lezioni_giorno(user, date) :
    list = []
    for lez in session.query(Lezioni).filter(and_(Lezioni.data == date,Lezioni.id_corso == IscrizioniCorsi.id_corso,IscrizioniCorsi.username ==user)).all():
        diz = {}
        diz["id"] =	lez.id_lezione 
        diz["nome"] = session.query(Corsi.nome).filter(Corsi.id_corso == lez.id_corso).first()[0]
        diz["inizio"] = lez.orario_inizio
        diz["fine"] = lez.orario_fine
        struttura = get_struttura(id_aula=int( session.query(Corsi.id_aula).filter(Corsi.id_corso == lez.id_corso).first()[0]))
        diz["struttura"] = struttura.nome + " - " + struttura.indirizzo
        diz["aula"] = session.query(Aule.nome).filter(and_(Corsi.id_corso == lez.id_corso, Aule.id_aula == Corsi.id_aula)).first()[0]
        prof = session.query(Utenti.nome,Utenti.cognome).filter(Corsi.docente == Utenti.username, Corsi.id_corso == lez.id_corso).first()
        diz["prof"] = prof[0] +" "+ prof[1]
        diz["HaPartecipato"] = session.query(PartecipazioniLezione).filter(PartecipazioniLezione.id_lezione == lez.id_lezione and PartecipazioniLezione.username == user).count() > 0
        list.append(diz)

    return list