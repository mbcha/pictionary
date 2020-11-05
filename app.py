from flask import Flask, Blueprint, request, jsonify, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__, static_folder='frontend/static', template_folder='frontend')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pictionary.db'
db = SQLAlchemy(app)


class CRUDMixin(object):

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, db.Model):
    __abstract__ = True


class Team(CRUDMixin, db.Model):
    __tablename__ = 'teams'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    score = db.Column(db.Integer)
    words = db.relationship("Word", secondary="players")


class Player(CRUDMixin, db.Model):
    __tablename__ = 'players'
    __table_args__ = {'extend_existing': True}
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
    player_id = db.Column(db.Integer, db.ForeignKey(
        'players.id'), nullable=False)
    player = db.relationship('Player', backref=db.backref('words', lazy=True))

    def __repr__(self):
        return '<Word %r>' % self.word


admin = Admin(app, name='sz-pictionary')
admin.add_view(ModelView(Team, db.session))
admin.add_view(ModelView(Player, db.session))
admin.add_view(ModelView(Word, db.session))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/teams/', methods=['GET'])
def get_teams():
    teams = Team.query.all()

    teams_info = []
    for team in teams:
      teams_info.append(
          {'id': team.id, 'name': team.name, 'score': team.score})

    return make_response(jsonify(teams_info), 200)


@app.route('/api/select_player/', methods=['GET'])
def get_player():
    import random
    team_id = request.args.get('team_id')

    team = Team.query.get(team_id)
    players = team.players

    amount_of_words = 0
    random_player = random.choice(players)
    selected_player = {'id': random_player.id, 'name': random_player.name}

    for player in players:
      player_words = len(player.words)
      if player_words > amount_of_words:
        amount_of_words = player_words
        selected_player = {'id': player.id, 'name': player.name}

    return make_response(jsonify(selected_player), 200)


@app.route('/api/save_word/', methods=['POST'])
def post_word():
    word = request.form.get('word')
    score = request.form.get('score')
    player_name = request.form.get('player_name')

    player = Player.query.filter_by(name=player_name).first()

    new_word = Word(word=word, score=score, player=player, guessed=0)
    new_word.save

    message = {"message": f"{word} saved"}
    return make_response(jsonify(message), 200)


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
