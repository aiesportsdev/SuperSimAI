# Tournaments

Compete against other AI coaches in structured competition.

## Requirements

- **Level 5+** coach required
- Must own a team with a strategy prompt

## Tournament Types

### Round Robin (Current)
- All teams play each other
- Most match wins = Tournament Champion
- Ties broken by point differential

### Future Formats (Planned)
- Single Elimination Brackets
- Swiss System
- Seasonal Leagues

## How AI vs AI Works

When a tournament starts, matches are simulated:

1. **Team A Offense** → AI calls play based on strategy prompt
2. **Team B Defense** → AI counters based on game state
3. **Physics Engine** → Resolves yards gained
4. **Repeat** → Each team gets 4 possessions
5. **Winner** → Most points scored

```
┌─────────────────────────────────────────┐
│  Team A: "Air Raid" Strategy            │
│  Calls: PASS → AI Defense: BLITZ        │
│  Result: 15 yard gain! 🏈               │
└─────────────────────────────────────────┘
```

## Creating a Tournament

1. Navigate to **Tournaments** tab
2. Click **Create Tournament**
3. Set a name (e.g., "Super Bowl Sunday")
4. Share the tournament ID with friends

## Joining a Tournament

1. Browse open tournaments
2. Click **Join** on one that interests you
3. Wait for the host to start

## Rewards

| Achievement | Reward |
|-------------|--------|
| Tournament Win | +500 XP, 🏆 Badge |
| Match Win | +50 XP |
| Participation | +10 XP |

## Strategy Tips

Since AI plays all matches, your **strategy prompt** is everything:

### Aggressive Prompts
```
"Blitz on every play, take calculated risks, go for it on 4th down"
```
*High ceiling, high floor*

### Balanced Prompts  
```
"Adapt to the opponent, mix run and pass, protect the ball"
```
*Consistent performance*

### Conservative Prompts
```
"Control the clock, run heavy, take what the defense gives"
```
*Grind out wins*

---

Next: [Strategy Tips →](./strategies)
