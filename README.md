# clay-sports 🏈

Sports scores CLI tool - Get live scores, standings, and schedules for major sports leagues.

## Features

- 🏈 **NFL** - Football scores
- 🏀 **NBA** - Basketball scores  
- ⚾ **MLB** - Baseball scores
- 🏒 **NHL** - Hockey scores
- 🎓 **College Football** - CFB scores
- 🎓 **College Basketball** -CBB scores

## Installation

```bash
# Clone or use directly
git clone https://github.com/robb99/clay-sports.git

# Add to PATH or use symlink
ln -s /path/to/clay-sports/clay_sports.py /usr/local/bin/clay_sports
```

## Usage

### Get Today's Scores

```bash
# NFL scores
python3 clay_sports.py scores nfl

# NBA scores
python3 clay_sports.py scores nba

# MLB scores
python3 clay_sports.py scores mlb
```

### Output Modes

```bash
# JSON output (for scripting)
python3 clay_sports.py scores nfl --json

# Spoken output (for TTS/voice)
python3 clay_sports.py scores nba --spoken
```

### Get Specific Team Score

```bash
# Chiefs score today
python3 clay_sports.py score chiefs nfl

# Lakers score
python3 clay_sports.py score lakers nba
```

### Schedule

```bash
# Upcoming games
python3 clay_sports.py schedule nfl

# Specific date
python3 clay_sports.py scores nfl --date 2026-10-15
```

### Standings

```bash
# Get standings info
python3 clay_sports.py standings nfl
```

## Examples

```
$ python3 clay_sports.py scores nfl
============================================================
  NFL SCORES
============================================================

Kansas City Chiefs         30 - Las Vegas Raiders           27  [Final]
Dallas Cowboys            34 - Houston Texans              30  [Final]
...
```

## Requirements

- Python 3.7+
- No external dependencies (uses urllib)
- Internet connection for ESPN API

## Data Source

Uses ESPN's public API - no API key required.

## License

MIT
