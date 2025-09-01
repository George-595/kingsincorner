# Kings in the Corner - Deployment Guide

This guide explains how to deploy and run the Kings in the Corner multiplayer card game.

## Local Development

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Clone the repository:
```bash
git clone <your-repo-url>
cd kings-corner-game
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game locally:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

## Sharing Over WiFi (Local Network)

To play with your girlfriend over the same WiFi network:

1. Start the game on your computer:
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

2. Find your local IP address:
   - **Mac/Linux**: `ifconfig | grep "inet " | grep -v 127.0.0.1`
   - **Windows**: `ipconfig | findstr "IPv4"`

3. Share the URL with your girlfriend:
   - Example: `http://192.168.1.100:8501`
   - Replace `192.168.1.100` with your actual IP address

4. Both players can now access the game from any device on the same WiFi network!

## Cloud Deployment Options

### 1. Streamlit Cloud (Recommended - Free)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy your repository
5. Share the public URL with anyone!

### 2. Heroku

1. Install Heroku CLI
2. Create a `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### 3. Railway

1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Deploy with one click

### 4. Replit

1. Go to [replit.com](https://replit.com)
2. Import from GitHub
3. Run the project - it will be automatically deployed

## Game Instructions

### How to Play
1. **Create a Game**: Enter your name and click "Create Game"
2. **Share Game ID**: Give the Game ID to other players
3. **Join Game**: Other players enter the Game ID to join
4. **Start Game**: Once 2-4 players have joined, click "Start Game"
5. **Play Cards**: Take turns playing cards on foundation piles or corner piles
6. **Win**: Be the first player to empty your hand!

### Game Rules
- **Foundation Piles**: Play cards in descending order with alternating colors
- **Corner Piles**: Only Kings can be played on empty corner piles
- **Turn Actions**: Play one card OR draw a card (ends turn)
- **Goal**: Empty your hand first to win!

## Troubleshooting

### Common Issues

**Game not loading over WiFi:**
- Make sure both devices are on the same WiFi network
- Check firewall settings - may need to allow port 8501
- Try disabling VPN if active

**Cards not displaying correctly:**
- Refresh the page
- Clear browser cache
- Make sure browser supports modern JavaScript

**Game state not syncing:**
- The game auto-refreshes every 3 seconds
- Click the refresh button in your browser if needed
- Check internet connection

## Performance Tips

- Game supports 2-4 players simultaneously
- Uses in-memory storage (games reset if server restarts)
- For production use, consider adding Redis for persistent storage
- Mobile-friendly interface works on phones and tablets

## Security Notes

- Game IDs are randomly generated UUIDs for security
- No personal data is stored permanently
- Games automatically expire after 1 hour of inactivity
- Only share Game IDs with people you want to play with

Enjoy playing Kings in the Corner! 🃏
