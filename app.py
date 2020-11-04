from flask import Flask, request, jsonify, make_response, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='dist/static', template_folder='dist')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pictionary.db'
db = SQLAlchemy(app)

db.Model.metadata.reflect(db.engine)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teams/', methods=['GET'])
def get_teams():
    from models import Team
    teams = Team.query.all()
    names = {}
    for idx, team in enumerate(teams):
      names.update({ idx + 1: team.name })

    return make_response(jsonify(names), 200)

@app.route('/selected_word/', methods=['POST'])
def post_word():
    word = request.form.get('word')

    if word:
        message = { "message": f"{word} saved" }
        return make_response(jsonify(message), 200)
    else:
        message = { "message": "no word found"}
        return make_response(jsonify(message), 404)

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
