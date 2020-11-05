from flask import Flask, Blueprint, request, jsonify, make_response, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import UserMixin, login_user, LoginManager, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login.utils import current_user
from flask_admin.helpers import get_form_data
from flask_admin.babel import gettext
from markupsafe import Markup


app = Flask(__name__, static_folder='frontend/static', template_folder='frontend')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pictionary.db'
app.config['SECRET_KEY'] = "bel-pictionary"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


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


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean)


class Team(CRUDMixin, db.Model):
    __tablename__ = 'teams'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    score = db.Column(db.Integer, default=0)


class Player(CRUDMixin, db.Model):
    __tablename__ = 'players'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    email = db.Column(db.Text)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team = db.relationship('Team', backref=db.backref('players', lazy="dynamic"))

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
    player = db.relationship('Player', backref=db.backref('words', lazy="dynamic"))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team = db.relationship(
        'Team', backref=db.backref('words', lazy="dynamic"))

    def __repr__(self):
        return '<Word %r>' % self.word


class LastPlay(CRUDMixin, db.Model):
    __tablename__ = 'last_play'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey(
        'players.id'), nullable=False)
    player = db.relationship('Player', backref=db.backref('last_play', lazy="dynamic"))
    team_id = db.Column(db.Integer, db.ForeignKey(
        'teams.id'), nullable=False)
    team = db.relationship('Team', backref=db.backref('last_play', lazy="dynamic"))

    def __repr__(self):
        return '<LastPlay %r>' % self.player.name


class MyView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('Must be logged in to access the admin pages')
        return redirect(url_for('login'))

class MyAdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('Must be logged in to access the admin pages')
        return redirect(url_for('login'))

class WordView(ModelView):
    def _format_guessed_now(view, context, model, name):
        if model.guessed:
            return 'Guessed'

        guessed_url = url_for('.guessed_view')

        _html = '''
            <form action="{guessed_url}" method="POST">
                <input id="word_id" name="word_id"  type="hidden" value="{word_id}">
                <button type='submit'>Set to guessed</button>
            </form
        '''.format(guessed_url=guessed_url, word_id=model.id)

        return Markup(_html)

    column_formatters = {
        'guessed': _format_guessed_now
    }

    @expose('guessed_view', methods=['POST'])
    def guessed_view(self):
        return_url = self.get_url('.index_view')

        form = get_form_data()
        word_id = form['word_id']

        word = self.get_one(word_id)
        word.guessed = True
        team = word.team
        team.score = team.score + word.score

        try:
            self.session.commit()
            flash(gettext('Word ID {word_id} guessed!'.format(
                word_id=word_id)))
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flash(gettext('Failed to set word ID {word_id} to guessed.'.format(
                word_id=word_id), error=str(ex)), 'error')

        return redirect(return_url)


admin = Admin(app, index_view=MyAdminView(), name='sz-pictionary')
admin.add_view(MyView(Team, db.session))
admin.add_view(MyView(Player, db.session))
admin.add_view(WordView(Word, db.session))
admin.add_view(MyView(User, db.session))
admin.add_view(MyView(LastPlay, db.session))
admin.add_link(MenuLink(name='Logout', url='/logout'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    if current_user and current_user.is_authenticated and current_user.is_admin :
        return redirect(url_for('admin.index'))
    else :
        return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))

    login_user(user, remember=remember)
    return redirect(url_for('admin.index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out')
    return render_template('login.html')


@app.route('/api/teams/', methods=['GET'])
def get_teams():
    teams = Team.query.all()

    teams_info = []
    for team in teams:
        info = {'id': team.id, 'name': team.name, 'score': team.score, 'players': []}
        for player in team.players :
            info['players'].append({ 'id': player.id, 'name': player.name })

        teams_info.append(info)

    return make_response(jsonify(teams_info), 200)


@app.route('/api/select_player/', methods=['GET'])
def get_player():
    import random
    last_play = LastPlay.query.one()

    if last_play :
        team = last_play.team
        players = team.players.filter(Player.id != last_play.player_id).all()
    else :
        team = Team.query.first()
        players = team.players.all()

    amount_of_words = 0
    random_player = random.choice(players)
    selected_player = {'id': random_player.id, 'name': random_player.name}

    for player in players:
        player_words = len(player.words.all())
        if player_words > amount_of_words:
            amount_of_words = player_words
            selected_player = {'id': player.id, 'name': player.name}

    return make_response(jsonify(selected_player), 200)



@app.route('/api/save_word/', methods=['POST'])
def post_word():
    word = request.form.get('word')
    score = request.form.get('score')
    player_id = request.form.get('player_id')

    if word and score and player_id :
        player = Player.query.get(player_id)

        new_word = Word(word=word, score=score, player=player, guessed=0, team=player.team)
        new_word.save()
        last_play = LastPlay.query.first()

        if last_play :
            last_play.player = player
            last_play.team = player.team
        else :
            last_play = LastPlay(player=player, team=player.team)

        last_play.save()

        message = {"message": f"{word} saved"}
        return make_response(jsonify(message), 200)
    else :
        error = {"error": "incorrect data provided"}
        return make_response(jsonify(error), 500)


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
