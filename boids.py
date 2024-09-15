import pygame
import random
import math

#############
# CONSTANTS #
#############
visualRange = 100
avoidRange = 100
avoidFactor = 0.5
cohesionFactor = 1
alignmentFactor = 1
coneSize = math.radians(180)


##############
# BOID CLASS #
##############

class Boid(pygame.sprite.Sprite):
    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)
        self.position =     pygame.Vector2(random.randint(0, 1280), random.randint(0, 720))
        self.velocity =     pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
        self.acceleration = pygame.Vector2(0, 0)

        self.type = random.choice(["blue", "red", "gray"])

        self.speed =        0

        if self.type == "blue":
            self.maxSpeed =     10
            self.minSpeed =     7
        elif self.type == "red":
            self.maxSpeed =     8
            self.minSpeed =     5
        elif self.type == "gray":
            self.maxSpeed =     12
            self.minSpeed =     9

        self.mass = random.uniform(1.0,2.0)

        self.screen =       screen

    def update(self):
        self.wrap()
        self.avoidEdge()
        self.acceleration /= self.mass
        self.velocity +=    self.acceleration
        self.speed =        math.sqrt(self.velocity.x**2 + self.velocity.y**2)

        if self.speed > self.maxSpeed:
            self.velocity *= 0.95
        if self.speed < self.minSpeed:
            self.velocity *= 1.05

        self.position +=    self.velocity      
        self.acceleration = pygame.Vector2(0, 0) 

    def avoidEdge(self):
        x, y = self.position.x, self.position.y

        # Calculate distance from edges
        left_distance = x
        right_distance = 1280 - x
        top_distance = y
        bottom_distance = 720 - y

        # Calculate the minimum distance to any edge
        min_edge_distance = min(left_distance, right_distance, top_distance, bottom_distance)

        if min_edge_distance < avoidRange and min_edge_distance > 0:
            # Determine which edge is closest
            if left_distance == min_edge_distance:
                direction = pygame.Vector2(1, 0)
            elif right_distance == min_edge_distance:
                direction = pygame.Vector2(-1, 0)
            elif top_distance == min_edge_distance:
                direction = pygame.Vector2(0, 1)
            else:  # bottom_distance == min_edge_distance
                direction = pygame.Vector2(0, -1)

            # Apply force to move away from the edge
            avoidForce = (direction * (0.5 / min_edge_distance)).normalize() * 1.7
            self.acceleration += avoidForce


    def wrap(self):
        if self.position.x < 0:
            self.position.x = 1280
        if self.position.x > 1280:
            self.position.x = 0

        if self.position.y < 0:
            self.position.y = 720
        if self.position.y > 720:
            self.position.y = 0


    def draw(self):
        trianglePoints = [[0,10], [-5,0], [5,0]]
        rotation = math.atan2(self.velocity.y, self.velocity.x)
        rotatedPoints = [[trianglePoints[0][0]*math.cos(rotation)-trianglePoints[0][1]*math.sin(rotation)+self.position.x, trianglePoints[0][0]*math.sin(rotation)+trianglePoints[0][1]*math.cos(rotation)+self.position.y],
                         [trianglePoints[1][0]*math.cos(rotation)-trianglePoints[1][1]*math.sin(rotation)+self.position.x, trianglePoints[1][0]*math.sin(rotation)+trianglePoints[1][1]*math.cos(rotation)+self.position.y],
                         [trianglePoints[2][0]*math.cos(rotation)-trianglePoints[2][1]*math.sin(rotation)+self.position.x, trianglePoints[2][0]*math.sin(rotation)+trianglePoints[2][1]*math.cos(rotation)+self.position.y]]
        pygame.draw.polygon(self.screen, self.type, rotatedPoints)


##################
# MAIN FUNCTIONS #
##################
def alignment(boids):
    for boid1 in boids:
        avgVelocity = pygame.Vector2(0, 0)
        count = 0
        
        for boid2 in boids:
            if boid1 != boid2 and boid1.type == boid2.type:
                distance = boid1.position.distance_to(boid2.position)
                if distance < visualRange:    
                    avgVelocity += boid2.velocity
                    count += 1

        if count > 0:
            avgVelocity /= count  
            steeringForce = (avgVelocity - boid1.velocity).normalize() * alignmentFactor
            boid1.acceleration += steeringForce  

def cohesion(boids): 
    for boid1 in boids:
        netPos = pygame.Vector2(0,0)
        count = 0
        for boid2 in boids:
            if boid1 != boid2 and boid1.type == boid2.type:
                distance = boid1.position.distance_to(boid2.position) 
                if distance < visualRange:
                    netPos += boid2.position
                    count += 1
        if count != 0:
            netPos /= count 
            netForce = (netPos - boid1.position).normalize() * cohesionFactor
            boid1.acceleration += netForce

def avoid(boids, avoidFactor):
    for boid1 in boids:
        for boid2 in boids:
            if boid1 != boid2:
                distance = boid1.position.distance_to(boid2.position)
                if distance < avoidRange:
                    direction = boid1.position - boid2.position
                    avoidForce = (direction / distance**2).normalize() * avoidFactor
                    boid1.acceleration += avoidForce

        
def main():
    pygame.init()

    screen =    pygame.display.set_mode((1280, 720))
    clock =     pygame.time.Clock()

    boids = [Boid(screen) for _ in range(100)]
    

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()

        
        alignment(boids)
        cohesion(boids)
        avoid(boids, avoidFactor)

        screen.fill("black")
        
        for boid in boids:
            boid.update()
            boid.draw()
            
        
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
