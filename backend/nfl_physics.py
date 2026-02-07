import pymunk
import math
import random

class NFLPhysicsWorld:
    # Physics constants
    GRAVITY = -32.0  # feet/sec² (scaled for game feel)
    PASS_SPEED = 45.0  # yards/sec (average NFL pass ~50 mph)
    
    def __init__(self):
        # Create Pymunk space
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        self.space.damping = 0.5  # High damping to simulate ground friction
        
        self.offense = {}  # role -> body
        self.defense = {}  # role -> body
        
        # Ball state (true 3D trajectory)
        self.ball_x = 0.0
        self.ball_y = 0.0
        self.ball_z = 0.0  # Altitude in yards
        self.ball_vx = 0.0
        self.ball_vy = 0.0
        self.ball_vz = 0.0
        self.ball_in_flight = False
        self.ball_carrier = None  # 'QB', 'RB', 'WR1', etc.
        self.pass_result = None  # 'complete', 'incomplete', 'interception'
        
        # Ball trail for visualization
        self.ball_trail = []
        self.MAX_TRAIL_LENGTH = 15
        
        self.frames = []
        
        # Grid boundaries
        self.FIELD_WIDTH = 100.0  # yards
        self.FIELD_HEIGHT = 53.3  # yards (NFL standard)
        
        # Scaling to GFootball coords (-1.0 to 1.0)
        self.world_to_gfoot_x = 1.0 / 50.0 
        self.world_to_gfoot_y = 0.42 / (self.FIELD_HEIGHT / 2.0)

    def add_player(self, team_id, pos, role):
        mass = 100.0
        radius = 0.6  # yards
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = pos
        
        shape = pymunk.Circle(body, radius)
        shape.friction = 0.7
        shape.elasticity = 0.1
        
        # Collision filtering: team 1 collides with team 2
        if team_id == 1:
            shape.filter = pymunk.ShapeFilter(categories=0b01, mask=0b10)
            self.offense[role] = body
        else:
            shape.filter = pymunk.ShapeFilter(categories=0b10, mask=0b01)
            self.defense[role] = body
            
        self.space.add(body, shape)
        return body

    def setup_formation(self, yard_line=25):
        # Yard Line 0-100. Map 0 to -50 in world coords
        x_start = yard_line - 50.0
        
        # Clear existing
        for b in list(self.space.bodies):
            self.space.remove(b, *b.shapes)
        self.offense = {}
        self.defense = {}
        self.ball_trail = []
        self.pass_result = None
        
        # OFFENSE
        self.add_player(1, (x_start - 5.0, 0), 'QB')
        self.add_player(1, (x_start - 8.0, 0), 'RB')
        # OL
        for i, y in enumerate([-4, -2, 0, 2, 4]):
            self.add_player(1, (x_start - 1.0, y), f'OL{i}')
        # WRs
        self.add_player(1, (x_start - 1.0, 20), 'WR1')
        self.add_player(1, (x_start - 1.0, -20), 'WR2')
        
        # DEFENSE
        for i, y in enumerate([-4, -2, 0, 2, 4]):
            self.add_player(2, (x_start + 1.0, y), f'DL{i}')
        # LBs
        self.add_player(2, (x_start + 5.0, -5), 'LB1')
        self.add_player(2, (x_start + 5.0, 5), 'LB2')
        # Secondary
        self.add_player(2, (x_start + 10.0, 20), 'CB1')
        self.add_player(2, (x_start + 10.0, -20), 'CB2')
        self.add_player(2, (x_start + 15.0, 0), 'S')
        
        # Initialize ball at QB
        self.ball_carrier = 'QB'
        qb = self.offense['QB']
        self.ball_x = qb.position.x
        self.ball_y = qb.position.y
        self.ball_z = 0.8  # Waist height (held)
        self.ball_in_flight = False

    def throw_ball(self, target_role='WR1', throw_power=1.0):
        """Launch ball toward target with realistic trajectory"""
        if self.ball_carrier != 'QB':
            return
        
        qb = self.offense['QB']
        target = self.offense[target_role]
        
        # Calculate distance to target
        dx = target.position.x - qb.position.x
        dy = target.position.y - qb.position.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Calculate flight time based on distance and power
        speed = self.PASS_SPEED * throw_power
        flight_time = distance / speed
        
        # Horizontal velocities
        self.ball_vx = dx / flight_time
        self.ball_vy = dy / flight_time
        
        # Vertical velocity - calculate to land at catch height (~2 yards)
        # Using: z = z0 + vz*t + 0.5*g*t²
        # Want z_final = 2, z0 = 2
        # 2 = 2 + vz*t + 0.5*(-32)*t²
        # vz = 16 * t (to peak and come back down)
        self.ball_vz = -0.5 * self.GRAVITY * flight_time
        
        # Set ball position at QB's hands
        self.ball_x = qb.position.x
        self.ball_y = qb.position.y
        self.ball_z = 2.0
        
        self.ball_in_flight = True
        self.ball_carrier = None
        self.ball_trail = []

    def update_ball_physics(self, dt):
        """Update ball position with gravity"""
        if not self.ball_in_flight:
            return
        
        # Store trail position
        self.ball_trail.append((self.ball_x, self.ball_y, self.ball_z))
        if len(self.ball_trail) > self.MAX_TRAIL_LENGTH:
            self.ball_trail.pop(0)
        
        # Update position
        self.ball_x += self.ball_vx * dt
        self.ball_y += self.ball_vy * dt
        self.ball_z += self.ball_vz * dt
        
        # Apply gravity to vertical velocity
        self.ball_vz += self.GRAVITY * dt
        
        # Check for interception by defenders
        if self.ball_z < 4.0:  # Ball low enough to catch/intercept
            for role, body in self.defense.items():
                dist = math.sqrt(
                    (body.position.x - self.ball_x)**2 + 
                    (body.position.y - self.ball_y)**2
                )
                if dist < 2.0:  # Within 2 yards
                    # Interception chance based on proximity
                    int_chance = (2.0 - dist) / 2.0 * 0.3  # Max 30% chance
                    if random.random() < int_chance:
                        self.ball_in_flight = False
                        self.pass_result = 'interception'
                        self.ball_carrier = role
                        return
        
        # Check for catch by receivers
        if self.ball_z < 3.0 and self.ball_z > 0.5:
            for role in ['WR1', 'WR2']:
                body = self.offense[role]
                dist = math.sqrt(
                    (body.position.x - self.ball_x)**2 + 
                    (body.position.y - self.ball_y)**2
                )
                if dist < 1.5:  # Within catching range
                    self.ball_in_flight = False
                    self.pass_result = 'complete'
                    self.ball_carrier = role
                    return
        
        # Ball hits ground - incomplete
        if self.ball_z <= 0:
            self.ball_z = 0
            self.ball_in_flight = False
            self.pass_result = 'incomplete'

    def run_play(self, play_type, steps=100):
        dt = 0.02  # 50 Hz
        
        for i in range(steps):
            progress = i / float(steps)
            
            if play_type == 'RUN':
                # RB rushes forward
                rb = self.offense['RB']
                rb.apply_force_at_local_point((40000, 0))
                
                # Ball stays with RB
                self.ball_x = rb.position.x
                self.ball_y = rb.position.y
                self.ball_z = 0.8
                self.ball_carrier = 'RB'
                
                # Defense pursues RB
                for role, body in self.defense.items():
                    target = rb.position
                    diff = target - body.position
                    if diff.length > 0:
                        force = diff.normalized() * 30000
                        body.apply_force_at_local_point(force)
            
            elif play_type == 'PASS':
                qb = self.offense['QB']
                
                # QB dropback (first 30%)
                if progress < 0.3:
                    qb.apply_force_at_local_point((-10000, 0))
                    self.ball_x = qb.position.x
                    self.ball_y = qb.position.y
                    self.ball_z = 0.8
                    self.ball_carrier = 'QB'
                
                # Throw at 30%
                elif progress >= 0.3 and not self.ball_in_flight and self.ball_carrier == 'QB':
                    self.throw_ball('WR1', throw_power=1.0)
                
                # WRs run routes
                for role in ['WR1', 'WR2']:
                    self.offense[role].apply_force_at_local_point((30000, 0))
                
                # Defenders cover
                cb1 = self.defense['CB1']
                wr1 = self.offense['WR1']
                diff = wr1.position - cb1.position
                if diff.length > 0:
                    cb1.apply_force_at_local_point(diff.normalized() * 25000)
            
            # Update ball physics
            self.update_ball_physics(dt)
            
            # If receiver caught it, they run
            if self.ball_carrier in ['WR1', 'WR2'] and self.pass_result == 'complete':
                receiver = self.offense[self.ball_carrier]
                receiver.apply_force_at_local_point((35000, 0))
                self.ball_x = receiver.position.x
                self.ball_y = receiver.position.y
                self.ball_z = 0.8
            
            self.space.step(dt)
            
            # Clamp players to field boundaries
            for body in list(self.offense.values()) + list(self.defense.values()):
                x = max(0, min(self.FIELD_WIDTH, body.position.x))
                y = max(-self.FIELD_HEIGHT / 2, min(self.FIELD_HEIGHT / 2, body.position.y))
                body.position = pymunk.Vec2d(x, y)
            
            self.record_frame()

    def record_frame(self):
        frame = {
            "ball": [
                self.ball_x * self.world_to_gfoot_x, 
                self.ball_y * self.world_to_gfoot_y, 
                self.ball_z * 0.1  # Scale z for visual
            ],
            "ball_trail": [
                [p[0] * self.world_to_gfoot_x, p[1] * self.world_to_gfoot_y, p[2] * 0.1] 
                for p in self.ball_trail
            ],
            "ball_in_flight": self.ball_in_flight,
            "pass_result": self.pass_result,
            "left_team": [],
            "right_team": []
        }
        for body in self.offense.values():
            frame["left_team"].append([
                body.position.x * self.world_to_gfoot_x, 
                body.position.y * self.world_to_gfoot_y
            ])
        for body in self.defense.values():
            frame["right_team"].append([
                body.position.x * self.world_to_gfoot_x, 
                body.position.y * self.world_to_gfoot_y
            ])
        
        self.frames.append(frame)
