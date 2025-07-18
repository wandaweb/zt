# ZT Miner - Chapter I: The Escape

A vertically scrolling shooter game where you control a drill-equipped spaceship escaping from a planet's core to the surface.

This was my entry for the AWS Build Games Challenge.  
Gameplay video (no commentary): [https://youtu.be/05CnL5O9Uk8](https://youtu.be/05CnL5O9Uk8)  
Dev stream: [https://www.twitch.tv/videos/2513334863](https://www.twitch.tv/videos/2513690390)  

## Story
Your ship has been locked away deep in the planet's core by those who feared its unmatched potential. Now activated, you must drill and fight your way through multiple layers of the planet to reach the surface and join your kind above ground.

## Features
- **5 Distinct Layers**: Core, Mantle, Lower Crust, Upper Crust, and Ice
- **Drill Mechanics**: Use your drill to break through obstacles
- **Combat System**: Shoot enemies and avoid their attacks
- **Checkpoint System**: Restart from the beginning of each layer when destroyed
- **Progressive Difficulty**: Each layer introduces new challenges
- **Seamless Level Progression**: Environment changes as you ascend
- **Score System**: Earn points for destroying enemies, obstacles, and completing layers
- **Window Scaling**: Scale the game window by 2x or 4x for high DPI displays

## Controls
- **Arrow Keys**: Move your ship
- **X**: Activate drill (destroys obstacles in front)
- **SPACE**: Shoot bullets
- **R**: Restart from checkpoint (when destroyed)
- **ENTER**: Skip intro screen

## Gameplay Mechanics
- **Health System**: Take damage from enemies and obstacles
- **Invulnerability Frames**: Brief protection after taking damage
- **Drill Cooldown**: Drill has a brief cooldown between uses
- **Enemy Types**: Basic enemies, aggressive seekers, and static pattern shooters
- **Destructible Obstacles**: Use drill or bullets to clear paths
- **Bullet Hell Patterns**: Static enemies fire in circular, spiral, and aimed patterns
- **Obstacle Formations**: Walls, mazes, tunnels, and scattered formations
- **Indestructible Barriers**: Some obstacles require navigation, not destruction

## Scoring System
- **Enemy Kills**:
  - Basic Enemy: 100 points
  - Aggressive Enemy: 150 points
  - Circular Pattern Enemy: 200 points
  - Spiral Pattern Enemy: 250 points
  - Aimed Pattern Enemy: 300 points
- **Obstacle Destruction**:
  - Basic Obstacle: 25 points
  - Crystal Obstacle: 35 points
  - Reinforced Obstacle: 50 points
- **Layer Completion Bonuses**:
  - Core: 1,000 points
  - Mantle: 1,500 points
  - Lower Crust: 2,000 points
  - Upper Crust: 2,500 points
  - Surface: 3,000 points
- **Death Penalty**:
  - Ship Destruction: -1,000 points (minimum score of 0)

## Layer Progression
1. **Core** (Red): Molten environment with heat-based enemies
2. **Mantle** (Orange): Intense pressure with aggressive creatures
3. **Lower Crust** (Brown): Rocky terrain with mining machines
4. **Upper Crust** (Gray): Dense rock formations
5. **Ice** (Blue): Final escape to freedom

## Installation & Running
1. Install pygame: `pip install pygame`
2. Run the game:
   - Default size (800x600): `python zt_miner.py`
   - 2x scaling (1600x1200): `python zt_miner.py --scale 2`
   - 4x scaling (3200x2400): `python zt_miner.py --scale 4`

## Tips
- Use your drill strategically - it's more effective against obstacles than bullets
- Keep moving to avoid enemy fire
- Each layer is a checkpoint - you'll restart from the current layer if destroyed
- Watch your health and use invulnerability frames wisely
- Different enemy types require different strategies
- Focus on high-value targets like static pattern enemies for better scores
- Complete layers quickly to maximize your layer completion bonuses

Escape the depths and reclaim your freedom!
