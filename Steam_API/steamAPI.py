from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

STEAM_API_KEY = os.environ.get('STEAM_API_KEY')  # Set your Steam API key as an environment variable

@app.route('/steam/user/<steamid>', methods=['GET'])
def get_steam_user_profile(steamid):
    if not STEAM_API_KEY:
        return jsonify({'error': 'Steam API key not set'}), 500

    url = (
        f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        f"?key={STEAM_API_KEY}&steamids={steamid}"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        players = data.get('response', {}).get('players', [])
        if not players:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(players[0])
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/steam/user/<steamid>/friends', methods=['GET'])
def get_steam_user_friends(steamid):
    if not STEAM_API_KEY:
        return jsonify({'error': 'Steam API key not set'}), 500

    url = (
        f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/"
        f"?key={STEAM_API_KEY}&steamid={steamid}&relationship=friend"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        friends = data.get('friendslist', {}).get('friends', [])
        return jsonify({'friends': friends})
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/steam/user/<steamid>/games', methods=['GET'])
def get_steam_user_owned_games(steamid):
    if not STEAM_API_KEY:
        return jsonify({'error': 'Steam API key not set'}), 500

    url = (
        f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        f"?key={STEAM_API_KEY}&steamid={steamid}&format=json"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        games = data.get('response', {}).get('games', [])
        return jsonify({'games': games})
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500


@app.route('/steam/user/<steamid>/cs2', methods=['GET'])
def get_steam_user_cs2_stats(steamid):
    if not STEAM_API_KEY:
        return jsonify({'error': 'Steam API key not set'}), 500
    cs2id = 730
    url = (
        f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/"
        f"?appid={cs2id}&key={STEAM_API_KEY}&steamid={steamid}"
    )
    url_games = (
        f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        f"?key={STEAM_API_KEY}&steamid={steamid}&format=json"
    )
    try:
        # first get games list and find cs2
        response = requests.get(url_games)
        response.raise_for_status()
        data = response.json()
        cs2 = next((game for game in data.get('response', {}).get('games', []) if game.get('appid') == 730), None)

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(data)
        stats = data.get('playerstats', {}).get('stats', [])
       
        return jsonify({'playtime':cs2,'stats': stats})
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500




if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
