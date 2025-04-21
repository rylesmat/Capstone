from flask import Flask, render_template, request, jsonify
from collections import deque

import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="MATHIEUR",
    password="Bubblegum12!",
    database="game_db"
)

cursor = db.cursor()

app = Flask(__name__)

# Graph Representation of Hogwarts (Rooms = Nodes, Paths = Edges)
room_graph = {
    'Dormitory': ['Gryffindor Common Room', 'Corridor'],
    'Gryffindor Common Room': ['Dormitory', "Headmaster's Office", 'Room of Requirement'],
    "Headmaster's Office": ['Gryffindor Common Room', 'Potions Classroom'],
    'Corridor': ['Dormitory', 'Room of Requirement', 'Store Room'],
    'Room of Requirement': ['Corridor', 'Chamber of Secrets', 'Gryffindor Common Room', 'Potions Classroom'],
    'Potions Classroom': ["Headmaster's Office", 'Great Hall', 'Room of Requirement'],
    'Store Room': ['Corridor', 'Chamber of Secrets'],
    'Chamber of Secrets': ['Room of Requirement', 'Store Room', 'Great Hall'],
    'Great Hall': ['Chamber of Secrets', 'Potions Classroom']
}

# Game Data
rooms = {
    'Dormitory': {'East': 'Gryffindor Common Room', 'South': 'Corridor', 'item': "Tom Riddle's Diary"},
    'Gryffindor Common Room': {'West': 'Dormitory', 'East': "Headmaster's Office", 'South': 'Room of Requirement', 'item': ''},
    "Headmaster's Office": {'West': 'Gryffindor Common Room', 'South': 'Potions Classroom', 'item': "Marvolo Gaunt's Ring"},
    'Corridor': {'North': 'Dormitory', 'East': 'Room of Requirement', 'South': 'Store Room', 'item': 'Nagini'},
    'Room of Requirement': {'West': 'Corridor', 'South': 'Chamber of Secrets', 'North': 'Gryffindor Common Room', 'East': 'Potions Classroom', 'item': "Rowena Ravenclaw’s Diadem"},
    'Potions Classroom': {'North': "Headmaster's Office", 'South': 'Great Hall', 'West': 'Room of Requirement', 'item': "Salazar Slytherin’s locket"},
    'Store Room': {'North': 'Corridor', 'East': 'Chamber of Secrets', 'item': "Helga Hufflepuff’s Cup"},
    'Chamber of Secrets': {'North': 'Room of Requirement', 'West': 'Store Room', 'East': 'Great Hall', 'item': 'Basilisk Fang'},
    'Great Hall': {'West': 'Chamber of Secrets', 'North': 'Potions Classroom', 'item': 'Voldemort'}
}

player = {
    "current_room": "Gryffindor Common Room",
    "inventory": []
}


# BFS Algorithm to Find Shortest Path
def find_shortest_path(start, target):
    queue = deque([(start, [start])])  # (current_room, path_taken)
    visited = set()

    while queue:
        current, path = queue.popleft()

        if current == target:
            return path  # Return the shortest path

        visited.add(current)

        for neighbor in room_graph.get(current, []):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))

    return []  # No path found


# Homepage (Game UI)
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def start():
    data = request.json
    player_name = data.get("player_name", "Guest")  # Default name if not provided
    player["current_room"] = "Gryffindor Common Room"
    player["inventory"] = []

    player_stats = get_or_create_player(player_name)

    return jsonify({
        "message": f"Game started! Welcome {player_name}. You are in the Gryffindor Common Room.",
        "current_room": player["current_room"],
        "inventory": player["inventory"],
        "wins": player_stats["wins"],
        "losses": player_stats["losses"]
    })


# Move Player
@app.route('/move', methods=['POST'])
def move():
    data = request.json
    direction = data.get("direction")
    current_room = player["current_room"]

    if direction in rooms[current_room]:
        player["current_room"] = rooms[current_room][direction]
        new_room = player["current_room"]
        message = f"You moved {direction} to {new_room}."

        if "item" in rooms[new_room] and rooms[new_room]["item"]:
            message += f" You see {rooms[new_room]['item']} here."

        return jsonify({
            "message": message,
            "current_room": new_room,
            "inventory": player["inventory"]
        })
    else:
        return jsonify({"message": "Invalid move! Try another direction."})


# Pick Up Item
@app.route('/pickup', methods=['POST'])
def pickup():
    current_room = player["current_room"]

    if "item" in rooms[current_room] and rooms[current_room]["item"]:
        item = rooms[current_room]["item"]
        player["inventory"].append(item)
        rooms[current_room]["item"] = ""  # Remove item from room
        return jsonify({
            "message": f"You picked up {item}.",
            "inventory": player["inventory"]
        })
    else:
        return jsonify({"message": "No items to pick up here!"})


@app.route('/destroy_all', methods=['POST'])
def destroy_all():
    data = request.json
    player_name = data.get('player_name')  # Get player_name from the request

    if player["current_room"] == "Great Hall" and len(player["inventory"]) == 7:
        # Player wins, update game result
        update_game_result(player_name, won=True)
        return jsonify({"message": "You destroyed all Horcruxes and defeated Voldemort! 🎉🏆"})

    elif player["current_room"] == "Great Hall":
        # Player loses (did not collect all Horcruxes), update game result
        update_game_result(player_name, won=False)
        return jsonify({"message": "You didn't collect all Horcruxes. Voldemort wins... 😈"})

    else:
        return jsonify({"message": "You must be in the Great Hall to destroy all Horcruxes!"})

# Provide Hint (Shortest Path to Great Hall)
@app.route('/hint', methods=['POST'])
def hint():
    current_room = player["current_room"]
    path = find_shortest_path(current_room, "Great Hall")

    if path:
        return jsonify({"message": f"Hint: The shortest path to the Great Hall is {' → '.join(path)}"})
    else:
        return jsonify({"message": "No possible path found!"})


@app.route('/stats', methods=['POST'])
def stats():
    data = request.json
    player_name = data.get("player_name", "Guest")

    cursor.execute("SELECT wins, losses FROM player_stats WHERE player_name = %s", (player_name,))
    result = cursor.fetchone()

    if result:
        return jsonify({"player_name": player_name, "wins": result[0], "losses": result[1]})
    else:
        return jsonify({"message": "No records found for this player."})


def get_or_create_player(player_name):
    cursor.execute("SELECT * FROM player_stats WHERE player_name = %s", (player_name,))
    result = cursor.fetchone()

    if result is None:
        cursor.execute("INSERT INTO player_stats (player_name, wins, losses) VALUES (%s, 0, 0)", (player_name,))
        db.commit()
        return {"player_name": player_name, "wins": 0, "losses": 0}

    return {"player_name": result[1], "wins": result[2], "losses": result[3]}


def update_game_result(player_name, won):
    cursor.execute("SELECT * FROM player_stats WHERE player_name = %s", (player_name,))
    result = cursor.fetchone()

    if result:
        if won:
            cursor.execute("UPDATE player_stats SET wins = wins + 1 WHERE player_name = %s", (player_name,))
        else:
            cursor.execute("UPDATE player_stats SET losses = losses + 1 WHERE player_name = %s", (player_name,))

        db.commit()


# Run the App
if __name__ == '__main__':
    app.run(debug=True)
