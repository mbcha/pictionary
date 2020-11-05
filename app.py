from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()
app = Flask(__name__, static_folder='frontend/static', template_folder='frontend')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.config.from_object('config')
    db.init_app(app)
    from models import Team, Player, Word
    from routes import api

    app.register_blueprint(api)

    admin = Admin(app, name='sz-pictionary')
    admin.add_view(ModelView(Team, db.session))
    admin.add_view(ModelView(Player, db.session))
    admin.add_view(ModelView(Word, db.session))

    app.run(threaded=True, port=5000)
