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
    def goto(self, x, y):
        self.x1 = x
        self.y1 = y
        width, height = self.img.get_size()
        self.x2 = x + width
        self.y2 = y + height

    def stands_on(self, target):
        return ((target.x2 > self.x1 > target.x1) or (target.x2 > self.x2 > target.x1)) and (target.y2 > self.y2 > target.y1)

    def head_bump(self, target):
        return ((target.x2 > self.x1 > target.x1) or (target.x2 > self.x2 > target.x1)) and (target.y2 > self.y1 > target.y1)


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
    activated = False
    def __init__(self, img, coords, dur, eff):
        super().__init__(img, coords)
        self.duration = dur
        self.effect = eff
    def activate(self, target):
        match self.effect:
            case 1:
                config.GRAVITY = 0
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
                config.GRAVITY = 0.8
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
jump_buff = Buff(image.load('jump_buff.png'), (config.SCREEN_WIDTH * 0.11, config.SCREEN_HEIGHT * 0.86), 5, 1)
jump_timer = 0

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
            gr_img1 = transform.scale(image.load('ground.png'), (config.SCREEN_WIDTH, config.SCREEN_HEIGHT * 0.05))
            gr_img = transform.scale(image.load('ground.png'), (config.SCREEN_WIDTH * 0.7, config.SCREEN_HEIGHT * 0.05))
            ground1 = Sprite(gr_img1, (0, config.SCREEN_HEIGHT * 0.95))
            ground2 = Sprite(gr_img, (config.SCREEN_WIDTH * 0.3, config.SCREEN_HEIGHT * 0.75))
            ground3 = Sprite(gr_img, (0, config.SCREEN_HEIGHT * 0.55))
            ground4 = Sprite(gr_img1, (0, 0))

            portal = Sprite(image.load('portal.png'), (config.SCREEN_WIDTH * 0.1, config.SCREEN_HEIGHT * 0.475))

            if jump_buff.activated:
                jump_buff.goto(-1000, -1000)
                jump_timer += 1
                if jump_timer >= config.FPS * jump_buff.duration:
                    jump_buff.activated = False
                    jump_buff.deactivate(player)
                    jump_timer = 0
            else:
                jump_buff.goto(config.SCREEN_WIDTH * 0.11, config.SCREEN_HEIGHT * 0.86)

            if player.stands_on(ground1) or player.stands_on(ground2) or player.stands_on(ground3):
                if keys[K_SPACE]:
                    player.speedY -= player.jump_power
                else:
                    player.speedY = 0
            elif player.head_bump(ground1) or player.head_bump(ground2) or player.head_bump(ground3) or player.head_bump(ground4):
                player.speedY = 1
            else:
                player.speedY += config.GRAVITY

            # подбор баффа
            if player.stands_on(jump_buff) or player.head_bump(jump_buff):
                jump_buff.activate(player)
                jump_buff.activated = True

            if player.stands_on(portal) or player.head_bump(portal):
                current_level += 1

            screen.fill((15, 15, 15))
            screen.blit(jump_buff.img, (jump_buff.x1, jump_buff.y1))
            screen.blit(ground1.img, (ground1.x1, ground1.y1))
            screen.blit(ground2.img, (ground2.x1, ground2.y1))
            screen.blit(ground3.img, (ground3.x1, ground3.y1))
            screen.blit(ground4.img, (ground4.x1, ground4.y1))
            screen.blit(portal.img, (portal.x1, portal.y1))

        case 2:
            screen.fill((25, 5, 15))
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
