from gettext import install
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum

# PER ACCEDERE AL DB USARE VARIABILE GLOBALE session
# CREATA DENTRO AD initialize_db
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
    secret_code = Column(String)
    orario_inizio = Column(Date)
    orario_fine = Column(Date)
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
def initialize_db ( user, db, table ):
    try:
        engine = None
        if user == 'admin':
            engine = create_engine('postgresql+psycopg2://admin:yQ9q8XgWYzYQv3RWccc3@' + db + '/' + table)
        elif user == 'utente':
            engine = create_engine('postgresql+psycopg2://utente:CLgC92dK9DbEkrMSRS4j@orientamentodais.com/orientamento')
        elif user == 'prof':
            engine = create_engine('postgresql+psycopg2://prof:7TpSZbBYJTcGUxxyqtSD@orientamentodais.com/orientamento')
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


def dump ():
    #initialize_db('admin', 'orientamentodais.com:5432', 'orientamento')
    initialize_db('admin', '127.0.0.1:5432', 'orientamentodais_locale')
    l = list()
    for i in get_users():
        l.append(str(i))
    return l

#---- Metodo utilizzato per verificare se è già stata creata una connessione valida alla 
#     base di dati, se così non è richiama il metodo di inizializzazione
def check_session():
    if 'session' not in globals():
        initialize_db('admin', '127.0.0.1:5432', 'orientamentodais_locale')
    

#---- Metodo utilizzato per inserire un nuovo utente nella base di dati
def insert_new_user(username, nome, cognome, email, data_nascita, password, is_professore, scuolaprovenienza = ''):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
        
    try:
        # creo il nuovo oggetto da inserire nella tabella utenti
        new_utente = Utenti(username = username, nome = nome, cognome = cognome, email = email, nascita = data_nascita, password = password)
        
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
              "      Vedi metodo insert_new_user()" +
              "      Per maggiori info:\n" + e)
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
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    
    for u in get_users():
        if (u.username == username and u.password == password):
            return Return.SUCCESS
    
    return Return.FAILURE


#---- Metodo utile per verificare se un certo username, e quindi utente, del sito sia registrato
#     come docente o meno restituendone il risultato della verifica
def is_professor(username):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    
    for u in get_docenti():
        if u.username == username:
            return True
    return False


def get_info_corso(id_corso):
    # controllo se è già stata inizializzata la sessione di connessione alla base di dati
    check_session()
    
    # eseguo una query alla base di dati per ricevere l'oggetto corso filtrato per 
    # l'id richiesto
    corso = session.query(Corsi).filter_by(id_corso = id_corso).first()
    
    # eseguo una query per poter visualizzare il numero di lezioni di cui è costituito 
    # il corso
    n_lezioni = session.query(Lezioni).filter_by(id_corso = id_corso).count()
    
    # eseguo una query per poter visualizzare il numero di iscritti al corso
    iscritti = session.query(IscrizioniCorsi).filter_by(id_corso = id_corso).count()
    
    # eseguo una query per poter ricevere il nome dell'aula e poi con il suo risultato 
    # ricerco il nome dell'edificio con un'altra query
    aula = session.query(Aule).filter_by(id_aula = corso.id_aula).first()
    struttura = session.query(Edifici).filter_by(id_edificio = aula.id_edificio).first()
    
    
    # traduco la modalità da valore booleano a stringa da inserire poi nel dizionario
    modalita = ""
    if corso.is_online == True:
        modalita = "In Presenza"
    else:
        modalita = "Online"
    
    return { "id": corso.id_corso,
			 "nome": corso.nome,
			 "struttura": struttura.nome,
			 "modalita": modalita,
			 "durata": str(n_lezioni) + " lezioni",
			 "iscrizioni": "aperte",
			 "postimin": corso.min_partecipanti,
			 "postimax": corso.max_partecipanti,
			 "iscritti": iscritti,
			 "prof": corso.docente,
			 "descrizione": corso.descrizione,
			 "inizio": "15/05/2022"}