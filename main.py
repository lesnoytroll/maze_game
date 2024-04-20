from pygame import *
import config

init()  # инициальзировать Pygame
mixer.init()
jump_sound = mixer.Sound('jump.wav')
punch_sound = mixer.Sound('punch.wav')
player_hit_sound = mixer.Sound('player_hit.wav')
portal_sound = mixer.Sound('portal.wav')

ambient_music = 'ambient.mp3'
mixer.music.load(ambient_music)
mixer.music.set_volume(config.MUSIC_VOLUME)

# play(), pause(), unpause(), stop()

class Sprite:
    img: image
    x1: float
    x2: float
    y1: float
    y2: float
    def __init__(self, img, coords):
        self.img = img
        self.x1, self.y1 = coords
        self.width, self.height = img.get_size()
        self.x2 = self.x1 + self.width
        self.y2 = self.y1 + self.height
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

    def touchL(self, target):
        return ((target.y2 > self.y1 > target.y1) or (target.y2 > self.y2 > target.y1)) and (target.x1 < self.x1 < target.x2)

    def touchR(self, target):
        return ((target.y2 > self.y1 > target.y1) or (target.y2 > self.y2 > target.y1)) and (target.x1 < self.x2 < target.x2)

    def touches(self, target):
        return self.stands_on(target) or self.head_bump(target) or self.touchL(target) or self.touchR(target)

class Player(Sprite):
    speedX: float
    speedY: float
    jump_power = 9
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

enemy_png = transform.scale(image.load('enemy.png'), (30, 30))
enemy = Sprite(enemy_png, (1000, 1000))
jump_buff = Buff(image.load('jump_buff.png'), (config.SCREEN_WIDTH * 0.11, config.SCREEN_HEIGHT * 0.86), 5, 1)
jump_timer = 0

clock = time.Clock()
in_menu = True
in_game = False
in_settings = False
door_level2_open = False
enemy2_timer = 0
enemy2_direction = 'R'

start_button = Sprite(transform.scale(image.load('start.png'), (260, 50)), (220, 150))
settings_button = Sprite(transform.scale(image.load('settings.png'), (400, 50)), (150, 225))
exit_button = Sprite(transform.scale(image.load('exit.png'), (190, 50)), (255, 300))

while in_menu:
    current_level = 1
    player = Player(image.load('king.png'), (config.SCREEN_WIDTH * 0.3, config.SCREEN_HEIGHT * 0.20), 6, 1)
    for ev in event.get():
        if ev.type == QUIT:
            in_menu = False
        if ev.type == MOUSEBUTTONDOWN:
            x, y = mouse.get_pos()
            if start_button.x1 <= x <= start_button.x2 and start_button.y1 <= y <= start_button.y2:
                in_game = True
                mixer.music.play(-1)
            if settings_button.x1 < x < settings_button.x2 and settings_button.y1 < y < settings_button.y2:
                in_settings = True
            elif exit_button.x1 < x < exit_button.x2 and exit_button.y1 < y < exit_button.y2:
                in_menu = False

    while in_game:
        for ev in event.get():
            if ev.type == QUIT:
                in_game = False
                mixer.music.stop()

        player.move(0, player.speedY)

        match current_level:
            case 1:
                keys = key.get_pressed()
                if keys[K_a] or keys[K_LEFT]:
                    if player.x1 > 0:
                        player.move(-player.speedX, 0)
                if keys[K_d] or keys[K_RIGHT]:
                    if player.x2 < config.SCREEN_WIDTH:
                        player.move(player.speedX, 0)

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
                        jump_sound.play()
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

                # переход на след. уровень
                if player.stands_on(portal) or player.head_bump(portal):
                    current_level += 1
                    player.goto(config.SCREEN_WIDTH*0.03, config.SCREEN_HEIGHT*0.25)
                    enemy.goto(config.SCREEN_WIDTH*0.7, config.SCREEN_HEIGHT*0.88)
                    portal_sound.play()

                screen.fill((15, 15, 15))
                screen.blit(jump_buff.img, (jump_buff.x1, jump_buff.y1))
                screen.blit(ground1.img, (ground1.x1, ground1.y1))
                screen.blit(ground2.img, (ground2.x1, ground2.y1))
                screen.blit(ground3.img, (ground3.x1, ground3.y1))
                screen.blit(ground4.img, (ground4.x1, ground4.y1))
                screen.blit(portal.img, (portal.x1, portal.y1))

            case 2:
                floor_img = transform.scale(image.load('ground.png'), (config.SCREEN_WIDTH, config.SCREEN_HEIGHT*0.05))
                ground_img = image.load('ground.png')
                ground1 = Sprite(transform.scale(ground_img, (config.SCREEN_WIDTH*0.5, config.SCREEN_HEIGHT*0.05)),
                                 (0, config.SCREEN_HEIGHT*0.3))
                ground2 = Sprite(transform.scale(ground_img, (config.SCREEN_WIDTH*0.3, config.SCREEN_HEIGHT*0.05)),
                                 (config.SCREEN_WIDTH*0.7, config.SCREEN_HEIGHT*0.3))
                ground3 = Sprite(transform.scale(ground_img, (config.SCREEN_WIDTH*0.2, config.SCREEN_HEIGHT*0.05)),
                                 (config.SCREEN_WIDTH*0.5, config.SCREEN_HEIGHT*0.5))
                ground4 = Sprite(transform.scale(ground_img, (config.SCREEN_WIDTH*0.2, config.SCREEN_HEIGHT*0.05)),
                                 (0, config.SCREEN_HEIGHT*0.7))
                floor = Sprite(floor_img, (0, config.SCREEN_HEIGHT*0.95))

                portal = Sprite(image.load('portal.png'), (config.SCREEN_WIDTH * 0.03, config.SCREEN_HEIGHT * 0.87))
                door = Sprite(transform.scale(image.load('door.png'), (config.SCREEN_WIDTH*0.05, config.SCREEN_HEIGHT*0.2)),
                              (config.SCREEN_WIDTH * 0.15, config.SCREEN_HEIGHT * 0.75))

                if enemy2_direction == 'L':
                    enemy.move(-3, 0)
                    enemy2_timer += 1
                    if enemy2_timer % 60 == 0:
                        enemy2_direction = 'R'
                        enemy2_timer = 0
                else:
                    enemy.move(3, 0)
                    enemy2_timer += 1
                    if enemy2_timer % 60 == 0:
                        enemy2_direction = 'L'
                        enemy2_timer = 0
                if enemy.touches(player):
                    player_hit_sound.play()
                    time.wait(350)
                    in_game = False

                keys = key.get_pressed()
                if keys[K_a] or keys[K_LEFT]:
                    if player.x1 > 0:
                        if not player.touchL(door):
                            player.move(-player.speedX, 0)
                        else:
                            if door_level2_open:
                                player.move(-player.speedX, 0)
                if keys[K_d] or keys[K_RIGHT]:
                    if player.x2 < config.SCREEN_WIDTH:
                        player.move(player.speedX, 0)

                if (player.stands_on(ground1) or player.stands_on(ground2) or player.stands_on(ground3) or
                        player.stands_on(floor) or player.stands_on(ground4)):
                    if keys[K_SPACE]:
                        jump_sound.play()
                        player.speedY -= player.jump_power
                    else:
                        player.speedY = 0
                elif (player.head_bump(ground1) or player.head_bump(ground2) or player.head_bump(ground3) or
                      player.head_bump(ground4)):
                    player.speedY = 1
                else:
                    player.speedY += config.GRAVITY

                if player.stands_on(portal) or player.head_bump(portal) or player.touchR(portal) or player.touchL(portal):
                    player.goto(config.SCREEN_WIDTH*0.5, config.SCREEN_HEIGHT*0.5)
                    current_level = 3

                if keys[K_r]:
                    punch_sound.play()
                    i = transform.scale(image.load('hitbox.png'), (player.width*2, player.height*2))
                    attack_range = Sprite(i, (player.x1-player.width/2, player.y1-player.height/2))
                    if enemy.touches(attack_range):
                        enemy.goto(1000, 1000)
                        door.goto(1000, 1000)
                        door_level2_open = True
                    del attack_range


                screen.fill((25, 5, 15))
                screen.blit(ground1.img, (ground1.x1, ground1.y1))
                screen.blit(ground2.img, (ground2.x1, ground2.y1))
                screen.blit(ground3.img, (ground3.x1, ground3.y1))
                screen.blit(ground4.img, (ground4.x1, ground4.y1))
                screen.blit(floor.img, (floor.x1, floor.y1))
                screen.blit(portal.img, (portal.x1, portal.y1))
                if not door_level2_open:
                    screen.blit(door.img, (door.x1, door.y1))
                screen.blit(enemy.img, (enemy.x1, enemy.y1))

            case 3:
                ground_img = image.load('ground.png')
                platform = Sprite(transform.scale(ground_img, (config.SCREEN_WIDTH*0.5, config.SCREEN_HEIGHT*0.05)),
                                 (config.SCREEN_HEIGHT*0.3, config.SCREEN_HEIGHT*0.475))
                boss = Enemy(image.load('boss.png'),
                             (config.SCREEN_WIDTH*0.1, config.SCREEN_HEIGHT*0.1))


                screen.fill((5, 5, 5))
                screen.blit(platform.img, (platform.x1, platform.y1))
                screen.blit(boss.img, (boss.x1, boss.y1))

        screen.blit(player.img, (player.x1, player.y1))
        display.update()
        clock.tick(config.FPS)

    while in_settings:
        volume = Sprite(transform.scale(image.load(f'volume_{int(config.MUSIC_VOLUME * 100)}.png'), (700, 460)), (0, 0))
        for ev in event.get():
            if ev.type == QUIT:
                in_settings = False
                mixer.music.set_volume(config.MUSIC_VOLUME)
            if ev.type == MOUSEBUTTONDOWN:
                x, y = mouse.get_pos()
                if 63 < x < 98 and 285 < y < 320:
                    if config.MUSIC_VOLUME > 0:
                        config.MUSIC_VOLUME -= 0.25
                if 605 < x < 641 and 285 < y < 320:
                    if config.MUSIC_VOLUME < 1.0:
                        config.MUSIC_VOLUME += 0.25

        screen.fill((117, 111, 67))
        screen.blit(volume.img, (volume.x1, volume.y1))
        display.update()
        clock.tick(config.FPS)


    screen.fill((6, 31, 13))
    screen.blit(start_button.img, (start_button.x1, start_button.y1))
    screen.blit(settings_button.img, (settings_button.x1, settings_button.y1))
    screen.blit(exit_button.img, (exit_button.x1, exit_button.y1))
    display.update()
    clock.tick(config.FPS)

quit()
