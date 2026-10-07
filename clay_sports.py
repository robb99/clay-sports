#!/usr/bin/env python3
"""
clay-sports - Sports Scores CLI Tool
Get live scores, standings, and schedules for major sports leagues.

Usage:
    python3 clay_sports.py scores nfl
    python3 clay_sports.py scores nba --json
    python3 clay_sports.py standings nfl
    python3 clay_sports.py schedule nfl
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import Optional, List, Dict

# ESPN Scoreboard URLs
ESPN_URLS = {
    "nfl": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
    "nba": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
    "mlb": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
    "nhl": "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard",
    "college-football": "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard",
    "college-basketball": "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard",
}

# League display names
LEAGUE_NAMES = {
    "nfl": "NFL Football",
    "nba": "NBA Basketball", 
    "mlb": "MLB Baseball",
    "nhl": "NHL Hockey",
    "college-football": "College Football",
    "college-basketball": "College Basketball",
}


def make_request(url: str) -> Optional[dict]:
    """Make API request with error handling."""
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


def get_scores(league: str, date: str = None) -> List[Dict]:
    """Get scores for a league."""
    url = ESPN_URLS.get(league.lower())
    if not url:
        return []
    
    # Add date if specified
    if date:
        # Convert YYYY-MM-DD to YYYY/MM/DD
        url += f"?dates={date.replace('-', '/')}"
    
    data = make_request(url)
    if not data:
        return []
    
    events = data.get("events", [])
    games = []
    
    for event in events:
        competition = event.get("competitions", [{}])[0]
        competitors = competition.get("competitors", [])
        
        if len(competitors) < 2:
            continue
        
        # Determine home and away
        home = None
        away = None
        for c in competitors:
            if c.get("homeAway") == "home":
                home = c
            else:
                away = c
        
        if not home or not away:
            continue
        
        # Parse scores (score can be string or dict)
        home_score_str = home.get("score", "0")
        away_score_str = away.get("score", "0")
        try:
            home_score = int(home_score_str) if isinstance(home_score_str, str) else int(home_score_str.get("value", 0))
        except (ValueError, AttributeError):
            home_score = 0
        try:
            away_score = int(away_score_str) if isinstance(away_score_str, str) else int(away_score_str.get("value", 0))
        except (ValueError, AttributeError):
            away_score = 0
        
        # Get status
        status = competition.get("status", {})
        game_status = status.get("description", "Unknown")
        period = status.get("period", 0)
        clock = status.get("displayClock", "")
        
        if game_status == "Final":
            status_str = "Final"
        elif game_status == "Scheduled":
            time = competition.get("startTime", "")
            if time:
                try:
                    dt = datetime.fromisoformat(time.replace("Z", "+00:00"))
                    status_str = dt.strftime("%I:%M %p")
                except:
                    status_str = "Scheduled"
            else:
                status_str = "Scheduled"
        elif period > 0:
            status_str = f"Q{period}"
            if clock:
                status_str += f" {clock}"
        else:
            status_str = game_status
        
        game = {
            "home": {
                "name": home.get("team", {}).get("displayName", "Home"),
                "abbreviation": home.get("team", {}).get("abbreviation", "HOM"),
                "score": home_score,
                "winner": home.get("winner", False),
            },
            "away": {
                "name": away.get("team", {}).get("displayName", "Away"),
                "abbreviation": away.get("team", {}).get("abbreviation", "AWY"),
                "score": away_score,
                "winner": away.get("winner", False),
            },
            "status": status_str,
            "league": league.upper(),
        }
        games.append(game)
    
    return games


def format_game(game: dict, output_mode: str = "normal") -> str:
    """Format a single game for display."""
    home = game["home"]
    away = game["away"]
    
    if output_mode == "json":
        return game
    
    if output_mode == "spoken":
        # Spoken format: "Away Team 100, Home Team 95. Final."
        winner = ""
        if home.get("winner"):
            winner = f" {home['name']} win."
        elif away.get("winner"):
            winner = f" {away['name']} win."
        
        return f"{away['name']} {away['score']}, {home['name']} {home['score']}. {game['status']}.{winner}"
    
    # Normal format
    away_str = f"{away['name']:<25} {away['score']:>3}"
    home_str = f"{home['name']:<25} {home['score']:>3}"
    status_str = f"[{game['status']}]"
    
    # Add winner indicator
    if home.get("winner"):
        home_str += " ✓"
    elif away.get("winner"):
        away_str += " ✓"
    
    return f"{away_str} - {home_str}  {status_str}"


def format_games(games: List[Dict], league: str, output_mode: str = "normal") -> str:
    """Format all games for display."""
    if not games:
        return f"No {LEAGUE_NAMES.get(league, league).lower()} games today."
    
    if output_mode == "json":
        return json.dumps(games, indent=2)
    
    output = [f"\n{'='*60}"]
    output.append(f"  {LEAGUE_NAMES.get(league.upper(), league.upper())} SCORES")
    output.append(f"{'='*60}\n")
    
    for game in games:
        output.append(format_game(game, output_mode))
    
    return "\n".join(output)


def get_standings(league: str) -> str:
    """Get standings for a league."""
    return f"Standings for {LEAGUE_NAMES.get(league.upper(), league.upper())} not available via CLI.\nVisit ESPN for current standings."


def get_schedule(league: str, days: int = 7) -> str:
    """Get upcoming schedule for a league."""
    all_games = []
    
    for i in range(days):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        games = get_scores(league, date)
        if games:
            all_games.extend(games)
    
    if not all_games:
        return f"No upcoming {LEAGUE_NAMES.get(league.upper(), league.lower())} games in the next {days} days."
    
    return format_games(all_games, league)


def get_team_score(team_query: str, league: str = "nfl") -> str:
    """Get current score for a specific team."""
    games = get_scores(league)
    
    if not games:
        return f"No {LEAGUE_NAMES.get(league.upper(), league)} game found for {team_query} today."
    
    team_lower = team_query.lower()
    
    for game in games:
        home = game["home"]
        away = game["away"]
        
        # Check team names and abbreviations
        if (team_lower in home["name"].lower() or team_lower in home["abbreviation"].lower() or
            team_lower in away["name"].lower() or team_lower in away["abbreviation"].lower()):
            return format_game(game, "normal")
    
    return f"No game found for \"{team_query}\" in {LEAGUE_NAMES.get(league.upper(), league)} today."


def main():
    parser = argparse.ArgumentParser(
        description="clay-sports - Get sports scores, standings, and schedules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scores nfl              Get today's NFL scores
  %(prog)s scores nba --json      Get NBA scores as JSON
  %(prog)s scores nba --spoken   Get scores in TTS-friendly format
  %(prog)s standings nfl          Get NFL standings info
  %(prog)s schedule nfl           Get upcoming NFL games
  %(prog)s score chiefs           Get score for specific team
  %(prog)s score lakers nba       Get Lakers score

Supported leagues: nfl, nba, mlb, nhl, college-football, college-basketball
        """
    )
    
    parser.add_argument("command", choices=["scores", "standings", "schedule", "score"],
                        help="Command to execute")
    parser.add_argument("league", nargs="?", help="League (nfl, nba, mlb, nhl, college-football, college-basketball)")
    parser.add_argument("team", nargs="?", help="Team name (for score command)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--spoken", action="store_true", help="Output for TTS (spoken)")
    parser.add_argument("--date", help="Date in YYYY-MM-DD format")
    
    args = parser.parse_args()
    
    output_mode = "json" if args.json else "spoken" if args.spoken else "normal"
    
    if args.command == "scores":
        if not args.league:
            print("Error: league required for scores command", file=sys.stderr)
            sys.exit(1)
        
        league = args.league.lower()
        if league not in ESPN_URLS:
            print(f"Unsupported league: {league}", file=sys.stderr)
            print("Supported:", ", ".join(ESPN_URLS.keys()), file=sys.stderr)
            sys.exit(1)
        
        games = get_scores(league, args.date)
        print(format_games(games, league, output_mode))
    
    elif args.command == "standings":
        if not args.league:
            print("Error: league required for standings command", file=sys.stderr)
            sys.exit(1)
        print(get_standings(args.league))
    
    elif args.command == "schedule":
        if not args.league:
            print("Error: league required for schedule command", file=sys.stderr)
            sys.exit(1)
        print(get_schedule(args.league))
    
    elif args.command == "score":
        if not args.team:
            print("Error: team name required for score command", file=sys.stderr)
            sys.exit(1)
        
        league = args.league.lower() if args.league else "nfl"
        if league not in ESPN_URLS:
            league = "nfl"  # Default to NFL
        
        print(get_team_score(args.team, league))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
