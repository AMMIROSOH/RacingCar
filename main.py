import pygame
import random
import os
import time
import neat
pygame.font.init( )


GEN = 0
WIN_WIDTH = 800
WIN_HEIGHT = 800 
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
BG_IMG =  pygame.image.load(os.path.join("imgs", "bg.jpg"))
BLOCK_IMG = pygame.transform.scale( pygame.image.load(os.path.join("imgs", "block.png")),(100,50))
CAR_IMG =  pygame.transform.scale(pygame.image.load(os.path.join("imgs", "car.png")),(100,200)) 
STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Block:
    IMG = BLOCK_IMG
    VEL = 30
    def __init__(self):
        self.x = random.randrange(0, WIN_WIDTH - 100)
        self.y = -self.IMG.get_height() -100
        self.height = self.IMG.get_height()
        self.width = self.IMG.get_width()

    def move(self):
        self.y += self.VEL
    def draw(self, win):
        win.blit(self.IMG,(self.x, self.y))
    def collide(self, car):
        car_mask = car.get_mask()
        block_mask = pygame.mask.from_surface(self.IMG)
        offset = (round(car.x) - self.x, car.Y_CAR - self.y + self.height)
        point = block_mask.overlap(car_mask, offset)
        if point:
            return True
        return False


class Car:
    IMG = CAR_IMG
    Y_CAR = 570
    VEL = 20
    MAX_ROTATION = 12
    ROT_VEL = 10
    ANIMATION_TIME = 5
    IF_TILT = False
    def __init__(self, x):
        self.x = x
        self.tilt = 0
        self.tick_count = 0
        self.width = self.IMG.get_width()
        self.height = CAR_IMG.get_height()
        self.y = self.Y_CAR
    def move(self, Direction):
        #True direction is right and False is left
        if Direction == "right" and self.x < WIN_WIDTH-CAR_IMG.get_width():
            self.x += self.VEL
            if self.tilt > -20:
                self.tilt -= self.ROT_VEL+10
        elif Direction == "left" and self.x > 0:
            self.x -= self.VEL
            if self.tilt < 20:
                self.tilt += self.ROT_VEL+10
        elif Direction == "":
            if self.tilt < 0:
                self.tilt += self.ROT_VEL/5
                if 5< self.tilt <-5:
                    self.tilt = 0   
            elif self.tilt > 0:
                self.tilt -= self.ROT_VEL/5
                if 5< self.tilt <-5:
                    self.tilt = 0   

    
    def draw(self, win):
        rotated_image = pygame.transform.rotate(self.IMG, self.tilt)
        new_rect = rotated_image.get_rect(center=self.IMG.get_rect(topleft = (self.x, self.Y_CAR)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.IMG)

class Road:
    IMG = BG_IMG
    VEL = 30
    IMG_HEIGHT = IMG.get_height()
    def __init__(self, y):
        self.y = y
    def move(self):
        self.y += self.VEL
        if self.y > self.IMG_HEIGHT:
            self.y = -self.IMG_HEIGHT
    def draw(self, win):
        win.blit(self.IMG, (0, self.y))

def draw_window(win, roads, score, cars, blocks, pop, gen):
    for road in roads:
        road.draw(win)
    for block in blocks:
        block.draw(win)
    for car in cars:
        car.draw(win)
    text1 = STAT_FONT.render("Score: "+str(score), 1,(255, 255, 255))
    text2 = STAT_FONT.render("Generation: "+str(gen - 1), 1,(255, 255, 255))
    text3 = STAT_FONT.render("Population: "+str(pop), 1,(255, 255, 255))
    win.blit(text1, (30 ,10))
    win.blit(text2, (30 ,10 + text1.get_height()))
    win.blit(text3, (30 ,10 + text2.get_height() + text1.get_height()))
    pygame.display.update()

    

def main(genomes, config):
    global GEN
    GEN += 1
    roads = []
    blocks = []
    nets = []
    ge = []
    cars = []
    for _,g in genomes:
        g.fitness = 0 
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        cars.append(Car(WIN_WIDTH/2 - CAR_IMG.get_width()/2))
        ge.append(g)

    roads.append(Road(0))
    roads.append(Road(-800))
    score = 0

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(30)
        score += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            """ #user interface
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    car.move("right")
                elif event.key == pygame.K_LEFT:
                    car.move("left")
                    """
        if len(cars) > 0 :
            if len(blocks) > 0:
                for x, car in enumerate(cars):
                    ge[x].fitness += 0.1
                    b = blocks[0]  
                    #                          center x of car           distance car and block         x-distance left of car from left of block  x of block
                    output = nets[x].activate((abs(car.x + car.width/2), abs(car.y -( b.y + b.height)), abs(car.x  + car.width - (b.x + b.width)), abs(b.x),     abs(b.x - car.x),  abs(WIN_WIDTH-(b.x+b.width)) ))
                    best = output[0]
                    output[1] = output[1] + 0.001
                    ind_best = 0
                    for index, o in enumerate(output):
                        if o > best:
                            best = o
                            ind_best = index
                    if ind_best== 0:
                        car.move("left")
                    elif ind_best == 1:
                        car.move("right")
        else:
            run = False
            break

        
        if len(blocks) == 0:
            blocks.append(Block())
        for x, block in enumerate(blocks):
            if len(blocks)<=1:
                if block.y > 650:
                    blocks.append(Block())
            block.move()
            if block.y > WIN_HEIGHT:
                blocks.pop(x)
            for x, car in enumerate(cars):
                if block.y > car.y + car.height:
                    ge[x].fitness += 5 
                if car.x < 0 or car.x + car.height > WIN_WIDTH or block.collide(car):
                    ge[x].fitness -= 3
                    cars.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                

            

        for road in roads:
            road.move()

        draw_window(win, roads, score, cars, blocks, len(cars), GEN)
    

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                neat.DefaultSpeciesSet, neat.DefaultStagnation,config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.run(main,300)



if __name__ == "__main__":
    localdir = os.path.dirname(__file__)
    config_path = os.path.join(localdir, "config-feedforward.txt")
    run(config_path)