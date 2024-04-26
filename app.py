import os
from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt 
import random
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import datetime

#classe per connessione partita  
#TODO: implementare le partite nel database

class Partita:
    def __init__(self):
        self.player=[]#dentro player ci sono gli username dei giocatori
        self.game_code=random.randint(100000,999999)#codice partita per collegarsi
        self.vincitore=None
        self.mosse=[]
        self.tempi=[]

    def creaStanza(self, player):
        self.player.append(player)
        return self.game_code
    
    
    def entraStanza(self, player, code):
        if len(self.player)==1 and code==str(self.game_code):
            self.player.append(player)
            return True
        else:
            #stanza piena
            return False

    
    def fine_gioco(self):
        if len(self.mosse)==len(self.player) and len(self.tempi)==len(self.player):
            if self.mosse[0]<self.mosse[1]:
                self.vincitore=self.player[0]
            elif self.mosse[0]>self.mosse[1]:
                self.vincitore=self.player[1]
            else:
                if self.tempi[0]<self.tempi[1]:
                    self.vincitore=self.player[0]
                elif self.tempi[0]>self.tempi[1]:
                    self.vincitore=self.player[1]
                else:
                    #pareggio
                    self.vincitore=None
        else:
            #non hanno finito entrambi
            return False
        return self.vincitore

    def player_end(self, mossa, tempo, player):
        index = self.player.index(player)
        self.mosse.insert(index, mossa)
        self.tempi.insert(index, tempo)
        return self.fine_gioco()
        
    def player_ingame(self, player):
        return player in self.player

    def get_adm(self):
        return self.player[0]
    
    def esci_stanza(self, player):
        if self.player[0]==player:
            self.player.remove(player)
            return False
        else:
            self.player.remove(player)
            return True
        
    def game_check(self):
        return len(self.player)==2
       

#variabili globali e inizializzazione

basedir = os.path.abspath(os.path.dirname(__file__))
partite=[]#lista delle partite in corso
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

#gestione accessibilità utente


# DATABASE CONFIGURATION

app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    username = db.Column(db.String(255), primary_key=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)

    statistics = db.relationship("Statistic", backref="user", uselist=False)  # One-to-One with Statistic

    def get_id(self):
           return (self.username)

    def __repr__(self):
        return '<User %r>' % self.username

class Partita(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player2 = db.Column(db.Integer, db.ForeignKey('users.username'), nullable=True)
    OraInizio = db.Column(db.DateTime, nullable=False)

class Statistic(db.Model):

    __tablename__ = 'statistics'

    user_id = db.Column(db.Integer, db.ForeignKey('users.username'), primary_key=True)
    id = db.Column(db.Integer, unique=True, nullable=False, autoincrement=True)
    wins = db.Column(db.Integer, nullable=False, default=0)
    losses = db.Column(db.Integer, nullable=False, default=0)
    p_gio_computer = db.Column(db.Integer, nullable=False, default=0)

class Obiettivo(db.Model):
    __tablename__ = 'objectives'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    descrizione = db.Column(db.String(255), nullable=False)
    stella = db.Column(db.Integer, nullable=False)

class SbloccaObiettivo(db.Model):
    __tablename__ = 'unlocked_objectives'

    user_id = db.Column(db.Integer, db.ForeignKey('users.username'), primary_key=True)
    obiettivo_id = db.Column(db.Integer, db.ForeignKey('objectives.id'), primary_key=True)
    data = db.Column(db.DateTime, nullable=False)

class Partita_online(db.Model):
    __tablename__ = 'online_games'

    id = db.Column(db.Integer, db.ForeignKey('games.id'), primary_key=True,autoincrement=True)

    oraFine1 = db.Column(db.DateTime, nullable=True) 
    oraFine2 = db.Column(db.DateTime, nullable=True)
    codice1 = db.Column(db.String(4), nullable=True)        # codice per il primo giocatore (creatore)
    codice2 = db.Column(db.String(4), nullable=True)        # codice per il secondo giocatore
    player1 = db.Column(db.Integer, db.ForeignKey('users.username'), nullable=False)

class Mossa(db.Model):
    __tablename__ = 'moves'

    user_id = db.Column(db.Integer, db.ForeignKey('users.username'), nullable=False)
    partita_id = db.Column(db.Integer, db.ForeignKey('games.id'), primary_key=True, nullable=False)
    riga = db.Column(db.Integer, primary_key=True, nullable=False)
    colonna = db.Column(db.Integer, primary_key=True, nullable=False)
    colore = db.Column(db.String(255), nullable=False)

class Partita_computer(db.Model):

    __tablename__ = 'computer_games'

    id = db.Column(db.Integer, db.ForeignKey('games.id'), primary_key=True,autoincrement=True)
    difficolta = db.Column(db.Integer, nullable=False) # 1 = facile, 2 = medio, 3 = difficile
    oraFine = db.Column(db.DateTime, nullable=True) 

class CreaPartita(db.Model):

    __tablename__ = 'creations'

    user_id = db.Column(db.Integer, db.ForeignKey('users.username'))
    partita_id = db.Column(db.Integer, db.ForeignKey('games.id'), primary_key=True)

class Lobby(db.Model):
    
        __tablename__ = 'lobbies'
    
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        codice = db.Column(db.String(6), unique=True, nullable=False)
        player1 = db.Column(db.Integer, db.ForeignKey('users.username'), nullable=False)
        idGame = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=True)

class EntraLobby(db.Model):
        
            __tablename__ = 'lobby_entries'
        
            user_id = db.Column(db.Integer, db.ForeignKey('users.username'))
            lobby_id = db.Column(db.Integer, db.ForeignKey('lobbies.id'), primary_key=True)

# Create tables in database (if not exist)
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

#funzioni per la chiamata delle pagini html
@app.route('/', methods=['GET', 'POST'])

def index():

    if current_user.is_authenticated:
        lobby = Lobby.query.filter_by(player1=current_user.username).first()
        if lobby is not None:
            EntraLobby.query.filter_by(lobby_id=lobby.id).delete()
        EntraLobby.query.filter_by(user_id=current_user.username).delete()
        Lobby.query.filter_by(player1=current_user.username).delete()
        db.session.commit()
        return render_template('index.html', msg=current_user.username)
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])

def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if username in [user.username for user in User.query.all()]:
            msg = 'Username already exists'
            return render_template('auth/register.html', msg=msg)
        
        # Save hashed password to database for security purposes
        salt = bcrypt.gensalt() 
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bytes(salt))
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])

def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
    
        if user:
            session['username'] = username # Store username in session
            if user.password == bcrypt.hashpw(password.encode('utf-8'), user.password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = 'Incorrect password'
        else:
            msg = 'Username does not exist'

    return render_template('auth/login.html', msg=msg)

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    logout_user()
    return redirect(url_for('index'))

@app.route('/regole', methods=['GET', 'POST'])

def rules():
    return render_template('rules.html')

@app.route('/gioco-computer', methods=['GET', 'POST'])

def game():
    return render_template('gameoffline.html')

@app.route('/online-game', methods=['GET', 'POST'])
@login_required
def gameonline():
    # fetch data from json request. It has to contain the id of the game and the code to win the game
    if request.method == 'POST':
        data = request.json
        game_id = data.get('id')
        code = data.get('code')
        lobby = Lobby.query.filter_by(idGame=game_id).first()
        online_game = Partita_online.query.filter_by(id=game_id).first()
        if lobby is not None:
            # if the current user is the creator of the lobby, update the code for the first player
            if lobby.player1 == current_user.username:
                if online_game is not None:
                    online_game.codice1 = code
            # if the current user is the second player, update the code for the second player
            else:
                enter_lobby = EntraLobby.query.filter_by(id=lobby.id).first()
                if enter_lobby is not None:
                    if enter_lobby.user_id == current_user.username:
                        if online_game is not None:
                            online_game.codice2 = code
        return jsonify({'id': game_id})
    else:
        return render_template('gameonline.html')

@app.route('/lobby/', methods=['GET', 'POST'])

@login_required
def lobby():
    
    # select mode from url query string (create or enter)
    mode = request.args.get('mode')
    code = ''
    msg = ''

    if mode == 'create':
        msg='Hai creato una lobby'
        # check if user has already created a lobby (if so, doesn't change the code)
        if Lobby.query.filter_by(player1=current_user.username).first() is not None:
            
            code = Lobby.query.filter_by(player1=current_user.username).first().codice

        # create a new lobby
        else:
            codeArray = random.choices('0123456789', k=6)                               #array of 6 random numbers
            code = ''.join(codeArray)                                                   #join the array to create a string
            new_lobby = Lobby(codice=code, player1=current_user.username)               #prepare the new lobby
            db.session.add(new_lobby)
            db.session.commit()

        # return the lobby page with the code, lobby creator and a message for the user 
        return render_template('lobby.html', code=code, creator=current_user.username, msg=msg)
    
    elif mode == 'enter':
        msg='Sei entrato in una lobby'
        # check if user has already entered a lobby (if so, doesn't change the code)
        if EntraLobby.query.filter_by(user_id=current_user.username).first() is not None:
            lobby_id = EntraLobby.query.filter_by(user_id=current_user.username).first().lobby_id
            code = Lobby.query.filter_by(id=lobby_id).first().codice
            return render_template('lobby.html', code=code, creator=Lobby.query.filter_by(id=lobby_id).first().player1, msg=msg)
        
        # enter a lobby with the code provided by the user
        code = request.form['code']
        isCorrectLobby = Lobby.query.filter_by(codice = code).first()
        
        # if the lobby exists, add the user to the lobby
        if isCorrectLobby:
            enter = EntraLobby(user_id=current_user.username, lobby_id=isCorrectLobby.id)
            db.session.add(enter)
            db.session.commit()
            return render_template('lobby.html', code=code, msg=msg, creator=isCorrectLobby.player1)
        
        # if the lobby doesn't exist, return the index page with an error message
        else:
            return render_template('index.html', code=code, msg='Nessuna lobby disponibile')

    return render_template('index.html', msg='Errore')

# funzioni per il dialogo client-server
@app.route('/isConnected')
def isConnected():
    isCreator = False
    if current_user.is_authenticated:
        lobby = Lobby.query.filter_by(player1=current_user.username).first()
        # if the user is not the creator of the lobby, either he is the second player or the creator has left his lobby
        if lobby is None:
            lobby = EntraLobby.query.filter_by(user_id=current_user.username).first()
            # if the user is the second player
            if lobby is not None:
                lobby = Lobby.query.filter_by(id=lobby.lobby_id).first()
                # if the creator has left the lobby
                if lobby is None:
                    return jsonify({'disconnect': True})
                else:
                    return jsonify({'connected': True, 'creator': isCreator})
            # should never happen
            return jsonify({'connected': False, 'creator': isCreator})
        # if the user is the creator of the lobby
        if lobby.player1 == current_user.username:
                isCreator = True
        enterLobby = EntraLobby.query.filter_by(lobby_id=lobby.id).first()
        # if the creator is still in the lobby and a second player has joined
        if lobby is not None and enterLobby is not None:
            return jsonify({'connected': True, 'username': enterLobby.user_id, 'creator': isCreator})
        else:
            return jsonify({'connected': False, 'creator': isCreator})
    # should never happen
    return jsonify({'connected': False})

@app.route('/game-online-code', methods=['GET', 'POST'])
@login_required
def gameonlinecode():
    id = request.args.get('id')
    player2 = request.args.get('player2')
    # Se l'utente corrente non è il secondo giocatore, aggiorna il campo player1 della partita online
    if current_user.username != player2:
        online_game = Partita_online.query.filter_by(id=id).first()
        online_game.player1 = current_user.username
        db.session.commit()

    return render_template('gameonlinecode.html', id=id, player2=player2)


@app.route('/create-game', methods=['POST'])
@login_required
def create_game():
    
    data = request.json
    player2 = data.get('player2')
    new_Game = Partita()
    new_Game.OraInizio = datetime.datetime.now()
    new_Game.player2 = player2
    db.session.add(new_Game)
    db.session.commit()
    # Crea una partita online
    online_game = Partita_online()
    online_game.id = new_Game.id
    online_game.player1 = current_user.username
    db.session.add(online_game)
    db.session.commit()
    # Aggiorna la lobby con l'id della partita
    lobby = Lobby.query.filter_by(player1=current_user.username).first()
    if lobby is not None:
        lobby.idGame = new_Game.id
        db.session.commit()
    data = {'id': new_Game.id}
    return jsonify(data)

@app.route('/insert-code', methods=['POST'])
def insert_code():
    if current_user.is_authenticated:
        data = request.json
        code = data.get('code')  # Estrai il valore del campo 'code'
        id_game = data.get('id')  # Estrai il valore del campo 'id'
        player = data.get('player')  # Estrai il valore del campo 'player2'
        online_game = Partita_online.query.filter_by(id=id_game).first()
        if online_game is None:
            return jsonify({'error': 'Partita non trovata'})
        if player == online_game.player1:
            online_game.codice1 = code
        else:
            online_game.codice2 = code
        db.session.commit()
        print(code)
        return jsonify(data)

@app.route('/isCreated', methods=['POST'])
@login_required
def isCreated():
    
    lobby = Lobby.query.filter_by(player1=current_user.username).first()
    if lobby is not None:
        if lobby.idGame is not None:
            return jsonify({'created': True, 'id': lobby.idGame})
        else:
            return jsonify({'created': False, 'id': lobby.idGame})
    else:
        enterLobby = EntraLobby.query.filter_by(user_id=current_user.username).first()
        if enterLobby is not None:
            lobby = Lobby.query.filter_by(id=enterLobby.lobby_id).first()
            if lobby.idGame is not None:
                return jsonify({'created': True, 'id': lobby.idGame})
            else:
                return jsonify({'created': False, 'id': lobby.idGame})
    return jsonify({'created': False, 'id': lobby.idGame})

if __name__ == "__main__":

    app.run(debug=True)