from flask import Blueprint, request, jsonify, make_response

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/teams/', methods=['GET'])
def get_teams():
    from models import Team
    teams = Team.query.all()

    teams_info = []
    for team in teams:
      teams_info.append(
          {'id': team.id, 'name': team.name, 'score': team.score})

    return make_response(jsonify(teams_info), 200)


@api.route('/select_player/', methods=['GET'])
def get_player():
    from models import Team
    from models import Word
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


@api.route('/save_word/', methods=['POST'])
def post_word():
    from models import Word
    from models import Player

    word = request.form.get('word')
    score = request.form.get('score')
    player_name = request.form.get('player_name')

    player = Player.query.filter_by(name=player_name).first()

    new_word = Word(word=word, score=score, player=player, guessed=0)
    new_word.save

    message = {"message": f"{word} saved"}
    return make_response(jsonify(message), 200)
