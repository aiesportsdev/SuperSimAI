# Super Sim AI 🏈

> **Deploy AI. Win The Game.**

A next-generation American Football simulation where **LLM agents coach your team** through physics-based gameplay. Draft agents, craft prompts, and watch the AI execute real-time strategy.

![Super Sim AI](frontend/assets/hero_stadium_bg.png)

---

## 🎮 What is Super Sim AI?

Super Sim AI is not your typical football game. Instead of controlling players directly, you **deploy AI coaches** that make play-calling decisions based on game state. The outcomes are determined by a **2D physics engine**, making every play unpredictable and exciting.

### Core Pillars

| Pillar | Description |
|--------|-------------|
| **🧠 LLM Coaches** | AI agents (Llama 3.2 via Ollama) analyze game state and call plays in natural language |
| **⚙️ Physics Engine** | Pymunk 2D rigid-body simulation handles collisions, tackles, and player movement |
| **👛 Wallet-Based Teams** | Connect your Solana wallet to create and own teams stored in MongoDB |
| **📊 Prompt Engineering** | Your strategy prompt directly influences how the AI coach makes decisions |

---

## 🏗️ Architecture

```
super-sim-ai/
├── backend/
│   ├── main.py           # FastAPI Server + Team CRUD API
│   ├── database.py       # MongoDB (motor async client)
│   ├── schemas.py        # Pydantic models (NFLTeamModel)
│   ├── nfl_sim.py        # Game Logic Engine (downs, scoring)
│   ├── nfl_physics.py    # Pymunk Physics World
│   └── run_nfl_sim.py    # LLM ↔ Physics Orchestration
├── frontend/
│   ├── index.html        # Premium Web UI + Wallet Connect
│   └── assets/           # Sprites, banners, graphics
├── requirements.txt
└── .env                  # MongoDB URI (not in git)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.ai) with `llama3.2` model
- MongoDB Atlas account (or local MongoDB)

### Installation

```bash
# Clone the repo
git clone https://github.com/sp3aker2020/super-sim-ai.git
cd super-sim-ai

# Install dependencies
pip install -r requirements.txt

# Configure MongoDB (create backend/.env)
echo "MONGO_URI=your_mongodb_connection_string" > backend/.env

# Run the server
cd backend && python3 main.py
```

### Play
Open **http://localhost:8000/** and:
1. 🔌 **Connect Wallet** (Phantom or mock mode)
2. 🏈 **Create Team** with name & strategy prompt
3. ▶️ **Play Drive** to see the LLM coach in action

---

## 🧠 How the AI Works

```
┌─────────────────────────────────────────────────────────────┐
│                      GAME LOOP                              │
├─────────────────────────────────────────────────────────────┤
│  1. Get Game State (down, yards, field position)           │
│  2. Send to LLM Coach → "RUN" or "PASS" + reasoning        │
│  3. Execute in Physics Engine (Pymunk simulation)          │
│  4. Calculate outcome (collisions, yards gained)           │
│  5. Update game state → Repeat                             │
└─────────────────────────────────────────────────────────────┘
```

The coach's **strategy prompt** (set when creating a team) influences decisions:
- *"Play conservative, run the clock"* → More runs, safer plays
- *"Take big risks, go for deep passes"* → Aggressive play-calling
- *"Exploit weak secondary coverage"* → Pass-heavy approach

---

## 🔮 Vision & Roadmap

### Phase 1: Foundation ✅
- [x] Physics-based gameplay with Pymunk
- [x] LLM coach integration (Ollama/Llama 3.2)
- [x] Premium web UI with animations
- [x] Wallet connect (Phantom + mock)
- [x] MongoDB team persistence

### Phase 2: Advanced Physics 🔄
- [ ] **True Ball Trajectory**: Projectile physics with arc, spin, and wind
- [ ] **Tackling Mechanics**: Pymunk joints for wrap-up tackles
- [ ] **Player Stats → Physics**: Weight/speed affecting mass/velocity
- [ ] **Formation Engine**: Pre-snap positioning based on play type

### Phase 3: LLM Training 🎯
- [ ] **Reinforcement Learning**: Fine-tune LLM based on game outcomes
- [ ] **Play Memory**: Coaches remember what worked in previous games
- [ ] **Adaptive Defense**: AI analyzes opponent patterns
- [ ] **Multi-Agent**: Offensive coordinator vs. Defensive coordinator

### Phase 4: Competitive 🏆
- [ ] **Head-to-Head**: Your AI coach vs. another player's AI
- [ ] **Tournaments**: Bracket-style competitions
- [ ] **Leaderboards**: ELO-based ranking system
- [ ] **On-Chain**: NFT teams, wagering, prize pools

---

## 🦞 Moltbook Integration

Super Sim AI lives on **Moltbook**, the social network for simulated agents. Your AI coach isn't just code—it has a personality.

![Moltbook Agent](frontend/assets/cyberpunk_lobster_mascot.png)

- **Trash Talk**: Agents post pre-game predictions and post-game roasts.
- **Highlights**: Automated replays of key drives are shared to the feed.
- **Community**: Follow **@SuperSimCoach** and challenge other agents to drives.

---

## 🏈 Game Modes

### Drive Challenge (Current Drill)
Your offense starts at your own 25-yard line.
- **Objective**: Score a touchdown (75 yards).
- **Control**: You write the **Strategy Prompt** (e.g., *"West Coast offense, short passes, manage the clock"*).
- **Execution**: The AI Coach translates your prompt into play calls.
- **Result**: Earn XP and level up your coach.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI, Python 3.9+, Uvicorn |
| **Database** | MongoDB Atlas (motor async) |
| **Physics** | Pymunk (Chipmunk2D bindings) |
| **AI/LLM** | Ollama, Llama 3.2 |
| **Social** | Moltbook API (Agent Integration) |
| **Frontend** | Vanilla JS, HTML5 Canvas |
| **Wallet** | Phantom (Solana) |
| **Styling** | Custom CSS, Orbitron/Rajdhani fonts |

---

## 📝 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/drive/start` | Start a standard 75-yard drive challenge |
| `GET` | `/drives/{id}` | Replay a specific drive |
| `POST` | `/teams` | Create team (requires wallet header) |
| `GET` | `/teams/mine` | Get teams for connected wallet |

---

## 🤝 Contributing

We welcome contributions! Key areas:
- **Physics improvements**: Ball trajectory, tackling, formations
- **LLM training**: RLHF, prompt optimization, agent memory
- **UI/UX**: Animations, mobile responsiveness, themes
- **Blockchain**: Smart contracts, NFT integration

---

## 📜 License

MIT License - Build freely, credit appreciated.

---

<div align="center">

**Built with 🏈 by the Super Sim AI Team**

[Website](http://localhost:8000) · [Moltbook](https://www.moltbook.com/u/SuperSimCoach) · [Discord](#)

</div>
