import requests
import json

import requests
import json

def get_games_for_date(date_str: str):
    """
    Fetches the ESPN WNBA scoreboard for a given date (format: YYYYMMDD).
    Returns a list of dictionaries containing game IDs and team names.
    """
    # api url
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard?dates={date_str}"
    print(f"Querying ESPN API for date: {date_str}...")
    
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        return []
        
    data = response.json()
    events = data.get("events", [])
    games_list = []
    for event in events:
        game_id = event.get("id")
        game_name = event.get("name")
        games_list.append({
            "game_id": game_id,
            "game_name": game_name
        })
        
    return games_list

def get_game_summary(game_id: str):
    """
    Fetches the full summary JSON (plays, boxscore, header) for a specific game_id.
    """

    summary_url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/summary?event={game_id}"
    print(f"Fetching summary data for game ID: {game_id}...")
    
    response = requests.get(summary_url)
    if response.status_code != 200:
        print(f"Error fetching summary for game {game_id}: Status {response.status_code}")
        return None
    
    return response.json()

def parse_plays(summary_data, game_date="Unknown"):
    """
    Takes the raw summary JSON and flattens the 'plays' list into a list of dictionaries.
    """
    plays = summary_data.get("plays", [])

    home_team_name = "Unknown"
    away_team_name = "Unknown"
    
    for team_entry in summary_data.get("boxscore", {}).get("teams", []):
        team_dict = team_entry.get("team", {})
        team_name = team_dict.get("displayName", "Unknown")
        
        if team_entry.get("homeAway") == "home":
            home_team_name = team_name
        elif team_entry.get("homeAway") == "away":
            away_team_name = team_name

    player_map = {}

    for entry in summary_data.get("boxscore", {}).get("players", []):
        for stat_group in entry.get("statistics", []):
            for athlete_obj in stat_group.get("athletes", []):
                ath = athlete_obj.get("athlete", {})
                p_id = str(ath.get("id"))
                p_name = ath.get("displayName")
                
                if p_id and p_name:
                    player_map[p_id] = p_name

    if len(game_date) == 8:
        formatted_date = f"{game_date[:4]}-{game_date[4:6]}-{game_date[6:]}"
    else:
        formatted_date = game_date
    
    parsed_rows = []
    
    for play in plays:
        participants = play.get("participants", [])
        
        p1 = participants[0].get("athlete", {}) if len(participants) > 0 else {}
        p2 = participants[1].get("athlete", {}) if len(participants) > 1 else {}
        p3 = participants[2].get("athlete", {}) if len(participants) > 2 else {}
        
        row = {
            "game_date": formatted_date,          
            "play_id": play.get("id"),
            "text": play.get("text"),
            "type_text": play.get("type", {}).get("text"),
            "type_id": play.get("type", {}).get("id"),
            "scoring_play": play.get("scoringPlay", False),
            "period": play.get("period", {}).get("number"),
            "clock_display": play.get("clock", {}).get("displayValue"),
            "home_score": play.get("homeScore"),
            "away_score": play.get("awayScore"),
            "home_team": home_team_name,     
            "away_team": away_team_name,
            "athlete_id_1": p1.get("id"),
            "athlete_name_1": player_map.get(p1.get("id")),
            "athlete_id_2": p2.get("id"),
            "athlete_name_2": player_map.get(p2.get("id")),
            "athlete_id_3": p3.get("id"),
            "athlete_name_3": player_map.get(p3.get("id")),
            "coordinate_x": play.get("coordinate", {}).get("x"),
            "coordinate_y": play.get("coordinate", {}).get("y")
        }
        parsed_rows.append(row)
        
    return parsed_rows


import pandas as pd
import os

def save_data_to_csv(dates_list, filename="wnba_data.csv"):
    all_data = []
    
    for date_str in dates_list:
        games = get_games_for_date(date_str)
        for game in games:
            print(f"Processing {game['game_name']}...")
            summary = get_game_summary(game['game_id'])
            if summary:
                rows = parse_plays(summary, game_date=date_str)
                all_data.extend(rows)
    
    if not all_data:
        print("No new data to save.")
        return

    new_df = pd.DataFrame(all_data)
    
    if os.path.exists(filename):
        existing_df = pd.read_csv(filename)
        final_df = pd.concat([existing_df, new_df])
        final_df = final_df.drop_duplicates(subset=['play_id'], keep='last')
        
        print(f"Updating file... Old size: {len(existing_df)} rows. New size: {len(final_df)} rows.")
    else:
        final_df = new_df
        print(f"Creating new file with {len(final_df)} rows.")
        

    final_df.to_csv(filename, index=False)
    print(f"\nPipeline complete! Saved to {filename}")

def get_all_game_dates():
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard"
    response = requests.get(url)
    data = response.json()
    
    game_dates = []
    
    leagues = data.get("leagues", [])
    if leagues:
        calendar_list = leagues[0].get("calendar", [])
        for date_string in calendar_list:
            # date_string example "2026-04-25T07:00Z"
            date_str = date_string.split("T")[0].replace("-", "")
            game_dates.append(date_str)
                
    return game_dates


if __name__ == "__main__":
    all_dates = get_all_game_dates()
    print(f"Found {len(all_dates)} total game days in the season.")
    
    test_dates = all_dates[:3] 
    print(f"\nTesting pipeline with dates: {test_dates}")
    
    save_data_to_csv(test_dates, "wnba_data.csv")