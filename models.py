from app import db
from mixins import CRUDMixin

class Team(CRUDMixin, db.Model):
    __tablename__ = 'teams'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.Text)
    score = db.Column(db.Integer)
    words = db.relationship("Word", secondary="players")


class Player(CRUDMixin, db.Model):
    __tablename__ = 'players'
    __table_args__ = { 'extend_existing': True }
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team = db.relationship('Team', backref=db.backref('players', lazy=True))

    def __repr__(self):
        return '<Player %r>' % self.name


class Word(CRUDMixin, db.Model):
    __tablename__ = 'words'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.Text)
    score = db.Column(db.Integer, default=0)
    guessed = db.Column(db.Boolean)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    player = db.relationship('Player', backref=db.backref('words', lazy=True))

    def __repr__(self):
        return '<Word %r>' % self.word

# CREATE TABLE teams (
#   id INTEGER PRIMARY KEY,
#   name TEXT not null,
#   score integer default 0
# );

# CREATE TABLE words(
#     id INTEGER PRIMARY KEY,
#     word TEXT not null,
#     score integer not null,
#     player_id INTEGER NOT NULL,
#     FOREIGN KEY (player_id)
#         REFERENCES teams (player_id)
# );

# CREATE TABLE players (
#   id INTEGER PRIMARY KEY,
#   name TEXT not null,
#   words TEXT,
#   team_id INTEGER NOT NULL,
#   FOREIGN KEY (team_id)
#     REFERENCES teams (team_id)
# );
