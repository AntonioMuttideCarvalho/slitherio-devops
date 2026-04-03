from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'devops-slitherio-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

players = {}
foods = []

def generate_food():
    return {'x': random.randint(50, 750), 'y': random.randint(50, 550)}

for _ in range(15):
    foods.append(generate_food())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    player_name = request.args.get('name', 'Anonymous')
    return render_template('game.html', player_name=player_name)

@socketio.on('join')
def handle_join(data):
    name = data['name']
    players[request.sid] = {
        'name': name,
        'score': 0,
        'x': random.randint(100, 700),
        'y': random.randint(100, 500),
        'color': f'#{random.randint(0, 0xFFFFFF):06x}'
    }
    emit('game_state', {
        'players': players,
        'foods': foods,
        'scores': get_scores()
    })

@socketio.on('move')
def handle_move(data):
    if request.sid in players:
        players[request.sid]['x'] = data['x']
        players[request.sid]['y'] = data['y']
        
        for i, food in enumerate(foods):
            if abs(players[request.sid]['x'] - food['x']) < 15 and abs(players[request.sid]['y'] - food['y']) < 15:
                players[request.sid]['score'] += 10
                foods[i] = generate_food()
        
        emit('update_players', players, broadcast=True)
        emit('update_scores', get_scores(), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in players:
        del players[request.sid]
        emit('update_scores', get_scores(), broadcast=True)

def get_scores():
    score_list = [(p['name'], p['score']) for p in players.values()]
    score_list.sort(key=lambda x: x[1], reverse=True)
    return score_list[:10]

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)