# Quick Start Guide - SimulAI Business Game

Get up and running in 5 minutes!

## 🚀 Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment file (optional)
cp .env.example .env

# 3. Create data directory
mkdir -p data
```

## ▶️ Start the Application

```bash
# Run all components at once
./run_all.sh
```

**Access Points:**
- 🎮 Game Master: http://localhost:8502
- 👤 Player Interface: http://localhost:8501
- 📊 Public Dashboard: http://localhost:8503
- 🔧 API Docs: http://localhost:8000/docs

## 🎯 First Game (5 Steps)

### Step 1: Create a Game (Game Master)
1. Open http://localhost:8502
2. Expand "Create New Game" in sidebar
3. Enter name: "My First Game"
4. Click "Create Game"
5. Select it from dropdown

### Step 2: Add Players (Game Master)
1. Go to "Players" tab
2. Expand "Add New Player"
3. Add players:
   - Name: "Alice", Email: "alice@example.com"
   - Name: "Bob", Email: "bob@example.com"
   - Name: "Charlie", Email: "charlie@example.com"

### Step 3: Start the Game (Game Master)
1. Click "▶️ Start Game" in sidebar
2. Game status changes to "ACTIVE"

### Step 4: Players Join (Player Interface)
1. Open http://localhost:8501 in new tabs/windows
2. Select "My First Game"
3. Select player name
4. Start trading!

### Step 5: Play the Game

**Game Master:**
- Click "⏭️ Advance to Next Quarter" to progress
- Watch as events trigger and markets change
- Monitor all players in "Players" tab
- Manually trigger events in "Events" tab

**Players:**
- Browse stocks in "Trading" tab
- Buy stocks you think will rise
- Sell stocks before they fall
- Check "Rankings" to see your position
- Read "News & Events" for market insights

## 💡 Quick Tips

### For Players
- **Starting Cash**: $100,000
- **Goal**: Have the highest portfolio value after 12 quarters
- **Strategy**: Diversify across sectors, watch for events
- **Trading**: Can only trade when game is active
- **Key Metric**: Total Portfolio Value = Cash + Holdings

### For Game Masters
- **Advance Quarter**: Click button to move to next quarter
- **Auto Events**: Random events trigger automatically (60% chance)
- **Manual Events**: Trigger specific events in "Events" tab
- **Game Flow**: Setup → Active → Completed
- **Controls**: Pause/Resume anytime, End to finish early

## 📊 Sample Gameplay

```
Quarter 1: Players build initial portfolios
Quarter 2: AI Breakthrough event → AI stocks surge
Quarter 3: Players rebalance based on news
Quarter 4: Energy Crisis → Energy stocks drop
...
Quarter 12: Final rankings, winner announced!
```

## 🎲 Example Event Chain

```
Event: "Quantum Computing Achieves Practical Supremacy"
↓
Direct Impact: Quantum sector +25%
↓
Causality Effects:
  → AI sector +8% (quantum helps AI)
  → Finance +5% (quantum cryptography)
  → Pharma +6% (quantum simulations)
```

## 🏆 Winning Strategies

1. **Diversify**: Don't invest everything in one sector
2. **Read News**: Events give you hints about market direction
3. **Understand Causality**: AI breakthrough? Buy Robotics too!
4. **Balance Risk**: Mix high-volatility (Quantum, AI) with stable (Finance, Energy)
5. **Cash Reserve**: Keep some cash to buy during dips

## 🔍 Troubleshooting

**Backend won't start:**
```bash
# Check if port 8000 is free
lsof -ti:8000 | xargs kill -9
./run_backend.sh
```

**Frontend won't connect to API:**
- Ensure backend is running (check http://localhost:8000)
- Check firewall settings
- Verify API_URL in frontend apps

**Database errors:**
```bash
# Reset database
rm -rf data/simulai.db
# Restart backend (will recreate DB)
./run_backend.sh
```

## 📱 Multiple Players on Same Computer

**Option 1: Different Browser Tabs**
- Each player opens http://localhost:8501 in a new tab
- Select different player name in each tab

**Option 2: Incognito/Private Windows**
- Use incognito mode for separate sessions

**Option 3: Different Browsers**
- Chrome for Player 1
- Firefox for Player 2
- Safari for Player 3

## 🎮 Game Variations

**Short Game:** 4 quarters
**Standard Game:** 12 quarters
**Long Game:** 20 quarters

**Easy Mode:** Lower volatility, fewer events
**Hard Mode:** Higher volatility, frequent events

Change these in Game Master when creating the game!

## 🆘 Need Help?

- Check main README.md for detailed docs
- Visit API docs at http://localhost:8000/docs
- Review sample data in `backend/database/seed_data.py`

---

**Now go play and have fun! 🎉**
