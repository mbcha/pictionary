from app import db

class Team(db.Model):
    __tablename__ = 'teams'
    __table_args__ = { 'extend_existing': True }
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.Text)
    score = db.Column(db.Integer)

class Player(db.Model):
    __tablename__ = 'players'
    __table_args__ = { 'extend_existing': True }
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    words = db.Column(db.Text)
    team_id = db.Column(db.Integer)

# CREATE TABLE teams (
#   id INTEGER PRIMARY KEY,
#   name TEXT not null,
#   score integer default 0
# );

# CREATE TABLE players (
#   id INTEGER PRIMARY KEY,
#   name TEXT not null,
#   words TEXT,
#   team_id INTEGER NOT NULL,
#   FOREIGN KEY (team_id)
#     REFERENCES teams (team_id)
# );
