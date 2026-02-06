import pymunk
import math
import random

class NFLPhysicsWorld:
    def __init__(self):
        # Create Pymunk space
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        self.space.damping = 0.5 # High damping to simulate ground friction/resistance
        
        self.offense = {} # role -> body
        self.defense = {} # role -> body
        self.ball = None
        self.ball_z = 0.0 # Virtual altitude
        self.frames = []
        
        # Grid boundaries
        self.FIELD_WIDTH = 100.0 # yards
        self.FIELD_HEIGHT = 53.3 # yards (NFL standard)
        
        # Scaling to GFootball coords (-1.0 to 1.0)
        # World 0,0 is center of field (50yd line)
        self.world_to_gfoot_x = 1.0 / 50.0 
        self.world_to_gfoot_y = 0.42 / (self.FIELD_HEIGHT / 2.0)

    def add_player(self, team_id, pos, role):
        mass = 100.0
        radius = 0.6 # yards
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = pos
        
        shape = pymunk.Circle(body, radius)
        shape.friction = 0.7
        shape.elasticity = 0.1
        
        # Collision filtering: team 1 collides with team 2
        # Categories: 1=Offense, 2=Defense, 4=Ball
        if team_id == 1:
            shape.filter = pymunk.ShapeFilter(categories=0b01, mask=0b10)
            self.offense[role] = body
        else:
            shape.filter = pymunk.ShapeFilter(categories=0b10, mask=0b01)
            self.defense[role] = body
            
        self.space.add(body, shape)
        return body

    def setup_formation(self, yard_line=25):
        # Yard Line 0-100. Let's map 0 to -50.
        x_start = yard_line - 50.0
        
        # Clear existing
        for b in list(self.space.bodies):
            self.space.remove(b, *b.shapes)
        self.offense = {}
        self.defense = {}
        
        # OFFENSE (Left -> Right)
        self.add_player(1, (x_start - 5.0, 0), 'QB')
        self.add_player(1, (x_start - 8.0, 0), 'RB')
        # OL
        for i, y in enumerate([-4, -2, 0, 2, 4]):
            self.add_player(1, (x_start - 1.0, y), f'OL{i}')
        # WRs
        self.add_player(1, (x_start - 1.0, 20), 'WR1')
        self.add_player(1, (x_start - 1.0, -20), 'WR2')
        
        # DEFENSE (Right -> Left)
        for i, y in enumerate([-4, -2, 0, 2, 4]):
             self.add_player(2, (x_start + 1.0, y), f'DL{i}')
        # LBs
        self.add_player(2, (x_start + 5.0, -5), 'LB1')
        self.add_player(2, (x_start + 5.0, 5), 'LB2')
        # Secondary
        self.add_player(2, (x_start + 10.0, 20), 'CB1')
        self.add_player(2, (x_start + 10.0, -20), 'CB2')
        self.add_player(2, (x_start + 15.0, 0), 'S')

    def run_play(self, play_type, steps=100):
        # Initialize ball at RB/QB position
        self.ball_z = 0.0
        
        for i in range(steps):
            progress = i / float(steps)
            
            # Simple AI Forces
            if play_type == 'RUN':
                # RB rushes forward
                rb = self.offense['RB']
                rb.apply_force_at_local_point((40000, 0))
                # Defense pursues RB
                for role, body in self.defense.items():
                    target = rb.position
                    diff = target - body.position
                    if diff.length > 0:
                        force = diff.normalized() * 30000
                        body.apply_force_at_local_point(force)
                ball_pos = (rb.position.x, rb.position.y)
            
            elif play_type == 'PASS':
                qb = self.offense['QB']
                # Dropback
                if progress < 0.3:
                    qb.apply_force_at_local_point((-10000, 0))
                
                # Ball flight (Hallucinated Z in 2D physics loop)
                # First 30% held by QB
                if progress < 0.3:
                    ball_pos = (qb.position.x, qb.position.y)
                    self.ball_z = 0.02
                else:
                    # Flight toward WR1 (Targeting)
                    target = self.offense['WR1'].position
                    start_p = qb.position
                    flight_prog = (progress - 0.3) / 0.7
                    bx = start_p.x + (target.x - start_p.x) * flight_prog
                    by = start_p.y + (target.y - start_p.y) * flight_prog
                    ball_pos = (bx, by)
                    self.ball_z = math.sin(flight_prog * math.pi) * 0.2
                
                # WRs run routes
                for role in ['WR1', 'WR2']:
                    self.offense[role].apply_force_at_local_point((30000, 0))
            
            self.space.step(0.02)
            self.record_frame(ball_pos)

    def record_frame(self, ball_pos):
        frame = {
            "ball": [ball_pos[0] * self.world_to_gfoot_x, ball_pos[1] * self.world_to_gfoot_y, self.ball_z],
            "left_team": [],
            "right_team": []
        }
        for body in self.offense.values():
            frame["left_team"].append([body.position.x * self.world_to_gfoot_x, body.position.y * self.world_to_gfoot_y])
        for body in self.defense.values():
            frame["right_team"].append([body.position.x * self.world_to_gfoot_x, body.position.y * self.world_to_gfoot_y])
        
        self.frames.append(frame)
