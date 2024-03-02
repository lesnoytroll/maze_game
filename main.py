from pygame import *
import config

class Sprite:
    img: image
    x1: float
    x2: float
    y1: float
    y2: float
    def __init__(self, img, coords):
        self.img = img
        self.x1, self.y1 = coords
        width, height = img.get_size()
        self.x2 = self.x1 + width
        self.y2 = self.y1 + height
    def move(self, dx, dy):
        self.x1 += dx
        self.x2 += dx
        self.y1 += dy
        self.y2 += dy
    def touches(self, target):
        return ((self.x1 <= target.x1 <= self.x2 and self.y1 <= target.y1 <= self.y2) or
                (self.x1 <= target.x2 <= self.x2 and self.y1 <= target.y1 <= self.y2) or
                (self.x1 <= target.x1 <= self.x2 and self.y1 <= target.y2 <= self.y2) or
                (self.x1 <= target.x2 <= self.x2 and self.y1 <= target.y2 <= self.y2) or
                (target.x1 <= self.x1 <= target.x2 and target.y1 <= self.y1 <= target.y2) or
                (target.x1 <= self.x2 <= target.x2 and target.y1 <= self.y1 <= target.y2) or
                (target.x1 <= self.x1 <= target.x2 and target.y1 <= self.y2 <= target.y2) or
                (target.x1 <= self.x2 <= target.x2 and target.y1 <= self.y2 <= target.y2))

class Player(Sprite):
    speedX: float
    speedY: float
    jump_power = 7
    hp = 3
    def __init__(self, img, coords, speedX, speedY):
        super().__init__(img, coords)
        self.speedX = speedX
        self.speedY = speedY

class Enemy(Sprite):
    pass

class Obstacle(Sprite):
    pass

class Buff(Sprite):
    duration: int
    effect: int
    def __init__(self, img, coords, dur, eff):
        super().__init__(img, coords)
        self.duration = dur
        self.effect = eff
    def activate(self, target):
        match self.effect:
            case 1:
                target.jump_power *= 2
            case 2:
                target.speedX *= 1.5
            case 3:
                target.hp += 2
                # size +
            case 4:
                # damage +
                pass
            case 5:
                # invisible
                pass
    def deactivate(self, target):
        match self.effect:
            case 1:
                target.jump_power /= 2
            case 2:
                target.speedX /= 1.5
            case 3:
                target.hp -= 2
                # size-
            case 4:
                # damage-
                pass
            case 5:
                # visible
                pass

screen = display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

player = Player(image.load('king.png'), (config.SCREEN_WIDTH * 0.9, config.SCREEN_HEIGHT * 0.8), 6, 1)

clock = time.Clock()
game_running = True
current_level = 1

while game_running:
    for ev in event.get():
        if ev.type == QUIT:
            game_running = False

    keys = key.get_pressed()
    if keys[K_a] or keys[K_LEFT]:
        if player.x1 > 0:
            player.move(-player.speedX, 0)
    if keys[K_d] or keys[K_RIGHT]:
        if player.x2 < config.SCREEN_WIDTH:
            player.move(player.speedX, 0)

    player.move(0, player.speedY)

    match current_level:
        case 1:
            gr_img1 = transform.scale(image.load('ground.png'), (config.SCREEN_WIDTH, config.SCREEN_HEIGHT * 0.07))
            gr_img = transform.scale(image.load('ground.png'), (config.SCREEN_WIDTH * 0.8, config.SCREEN_HEIGHT * 0.07))
            ground1 = Sprite(gr_img1, (0, config.SCREEN_HEIGHT * 0.93))
            ground2 = Sprite(gr_img, (config.SCREEN_WIDTH * 0.2, config.SCREEN_HEIGHT * 0.65))
            ground3 = Sprite(gr_img, (0, config.SCREEN_HEIGHT * 0.40))

            if player.touches(ground1) or player.touches(ground2) or player.touches(ground3):
                if keys[K_SPACE]:
                    player.speedY -= player.jump_power
                else:
                    player.speedY = 0
            else:
                player.speedY += 0.6

            screen.fill((173, 133, 109))
            screen.blit(ground1.img, (ground1.x1, ground1.y1))
            screen.blit(ground2.img, (ground2.x1, ground2.y1))
            screen.blit(ground3.img, (ground3.x1, ground3.y1))
        case 2:
            pass
        case 3:
            pass
        case 4:
            pass
        case 5:
            pass


    screen.blit(player.img, (player.x1, player.y1))
    display.update()
    clock.tick(config.FPS)

quit()