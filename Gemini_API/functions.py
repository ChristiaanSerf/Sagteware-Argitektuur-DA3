import json
from typing import List, Dict, Any

def save_cs2_scoreboard(players: List[Dict[str, Any]], CT_score: int, T_score: int) -> Dict[str, Any]:
    """
    Saves the Counter-Strike 2 scoreboard information, including player stats and team scores.
    
    Args:
        players: List of player stat dictionaries from the scoreboard
        CT_score: Score of the CT team
        T_score: Score of the T team
    
    Returns:
        A JSON object containing all the saved scoreboard details
    """
    # Create the scoreboard data structure
    scoreboard_data = {
        "players": players,
        "CT_score": CT_score,
        "T_score": T_score,
        "total_players": len(players),
        "match_summary": {
            "total_kills": sum(player.get("Kills", 0) for player in players),
            "total_deaths": sum(player.get("Deaths", 0) for player in players),
            "total_assists": sum(player.get("Assists", 0) for player in players),
            "total_damage": sum(player.get("DMG", 0) for player in players),
            "average_headshot_percentage": sum(player.get("HeadshotPerc", 0) for player in players) / len(players) if players else 0
        }
    }
    
    # Add team-specific statistics
    ct_players = [p for p in players if p.get("team") == "CT"]
    t_players = [p for p in players if p.get("team") == "T"]
    
    scoreboard_data["team_stats"] = {
        "CT": {
            "score": CT_score,
            "player_count": len(ct_players),
            "total_kills": sum(p.get("Kills", 0) for p in ct_players),
            "total_deaths": sum(p.get("Deaths", 0) for p in ct_players),
            "total_assists": sum(p.get("Assists", 0) for p in ct_players),
            "total_damage": sum(p.get("DMG", 0) for p in ct_players)
        },
        "T": {
            "score": T_score,
            "player_count": len(t_players),
            "total_kills": sum(p.get("Kills", 0) for p in t_players),
            "total_deaths": sum(p.get("Deaths", 0) for p in t_players),
            "total_assists": sum(p.get("Assists", 0) for p in t_players),
            "total_damage": sum(p.get("DMG", 0) for p in t_players)
        }
    }
    
    # Add top performers
    if players:
        top_killer = max(players, key=lambda x: x.get("Kills", 0))
        top_damage = max(players, key=lambda x: x.get("DMG", 0))
        top_headshot = max(players, key=lambda x: x.get("HeadshotPerc", 0))
        
        scoreboard_data["top_performers"] = {
            "most_kills": {
                "player": top_killer.get("player"),
                "kills": top_killer.get("Kills", 0)
            },
            "most_damage": {
                "player": top_damage.get("player"),
                "damage": top_damage.get("DMG", 0)
            },
            "best_headshot_percentage": {
                "player": top_headshot.get("player"),
                "headshot_percentage": top_headshot.get("HeadshotPerc", 0)
            }
        }
    
    return scoreboard_data
