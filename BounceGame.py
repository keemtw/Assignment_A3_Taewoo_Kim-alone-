# Theme: Cat vs Snoopdogg
# Player is a cat avoiding Snoopdogg heads and collecting boost-up cats (powerups).
# Creative element: Every 5 seconds, one random enemy speeds up, making the game harder.

import pygame, sys, math, random

# Test if two sprite masks overlap
def pixel_collision(mask1, rect1, mask2, rect2):
    offset_x = rect2[0] - rect1[0]
    offset_y = rect2[1] - rect1[1]
    overlap = mask1.overlap(mask2, (offset_x, offset_y))
    return overlap is not None

class Sprite:
    def __init__(self, image):
        self.image = image
        self.rectangle = image.get_rect()
        self.mask = pygame.mask.from_surface(image)

    def set_position(self, new_position):
        self.rectangle.center = new_position

    def draw(self, screen):
        screen.blit(self.image, self.rectangle)

    def is_colliding(self, other_sprite):
        return pixel_collision(self.mask, self.rectangle, other_sprite.mask, other_sprite.rectangle)

class Enemy(Sprite):
    def __init__(self, image, width, height):
        super().__init__(image)
        self.rectangle.center = (
            random.randint(0, width),
            random.randint(0, height)
        )
        vx, vy = random.randint(-5, 5), random.randint(-5, 5)
        while vx == 0 and vy == 0:
            vx, vy = random.randint(-5, 5), random.randint(-5, 5)
        self.speed = (vx, vy)
        self.has_collided = False  # 👈 여기에 추가

    def move(self):
        vx, vy = self.speed
        self.rectangle.move_ip(vx, vy)

    def bounce(self, width, height):
        vx, vy = self.speed
        if self.rectangle.left < 0 or self.rectangle.right > width:
            vx = -vx
        if self.rectangle.top < 0 or self.rectangle.bottom > height:
            vy = -vy
        self.speed = (vx, vy)

class PowerUp(Sprite):
    def __init__(self, image, width, height):
        super().__init__(image)
        self.rectangle.center = (
            random.randint(0, width - self.rectangle.width),
            random.randint(0, height - self.rectangle.height)
        )

class Player(Sprite):
    def __init__(self, image):
        super().__init__(image)

    def set_position(self, new_position):
        self.rectangle.center = new_position

class PlatformEnemy(Enemy):
    def __init__(self, image, width, height):
        super().__init__(image, width, height)
        vx, _ = self.speed
        self.speed = (vx, 0) # y-direction is fixed, which makes the game easy, since the game is difficult to play right now.

class RotatingPowerUp(PowerUp):
    def __init__(self, image, width, height):
        super().__init__(image, width, height)
        self.angle = 0
        self.original_image = image

    def draw(self, screen):
        self.angle += 5
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        old_center = self.rectangle.center
        self.rectangle = self.image.get_rect()
        self.rectangle.center = old_center
        self.mask = pygame.mask.from_surface(self.image)
        super().draw(screen)


def main():
    pygame.init()
    myfont = pygame.font.SysFont('monospace', 24)

    width, height = 600, 400
    screen = pygame.display.set_mode((width, height))

    # Load image assets
    enemy = pygame.image.load("snoopdogg.png").convert_alpha()
    enemy_image = pygame.transform.smoothscale(enemy, (50, 50))

    enemy_sprites = []
    for _ in range(4):
        enemy_sprite = Enemy(enemy_image, width, height)
        enemy_sprites.append(enemy_sprite)

    for _ in range(3):
        platform_enemy = PlatformEnemy(enemy_image, width, height)
        enemy_sprites.append(platform_enemy)

    # Player image scaled to same size as enemies
    player_raw = pygame.image.load("cat.png").convert_alpha()
    player_image = pygame.transform.smoothscale(player_raw, (50, 50))
    player_sprite = Player(player_image)
    life = 3

    powerup_image = pygame.image.load("boost up cat.png").convert_alpha()
    raw_powerup = pygame.image.load("boost up cat.png").convert_alpha()
    powerup_image = pygame.transform.smoothscale(raw_powerup, (50, 50))

    powerups = []

    game_ticks = 0

    is_playing = True
    while is_playing:
        if life <= 0:
            is_playing = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_playing = False

        pos = pygame.mouse.get_pos()
        player_sprite.set_position(pos)

        for enemy_sprite in enemy_sprites:
            if player_sprite.is_colliding(enemy_sprite):
                if not enemy_sprite.has_collided:
                    life -= 1
                    life = max(life, 0)
                    enemy_sprite.has_collided = True
            else:
                enemy_sprite.has_collided = False

        for powerup in powerups:
            if player_sprite.is_colliding(powerup):
                if isinstance(powerup, RotatingPowerUp):
                    life += 2
                else:
                    life += 1

        powerups = [p for p in powerups if not player_sprite.is_colliding(p)]

        for enemy_sprite in enemy_sprites:
            enemy_sprite.move()
            enemy_sprite.bounce(width, height)

        # Creative element: every 5 seconds (250 ticks), randomly boost one enemy
        game_ticks += 1
        if game_ticks % 250 == 0:
            random_enemy = random.choice(enemy_sprites)
            vx, vy = random_enemy.speed
            vx *= 1.2
            vy *= 1.2
            vx = max(min(vx, 10), -10)
            vy = max(min(vy, 10), -10)
            random_enemy.speed = (vx, vy)

        if random.randint(1, 100) == 1:
            if random.random() < 0.5:
                new_powerup = PowerUp(powerup_image, width, height)
            else:
                new_powerup = RotatingPowerUp(powerup_image, width, height)
            powerups.append(new_powerup)

        screen.fill((0, 100, 50))

        for enemy_sprite in enemy_sprites:
            enemy_sprite.draw(screen)
        for powerup_sprite in powerups:
            powerup_sprite.draw(screen)

        player_sprite.draw(screen)

        text = "Life: " + str(life)
        life_banner = myfont.render(text, True, (255, 255, 0))
        screen.blit(life_banner, (20, 20))

        pygame.display.update()
        pygame.time.wait(20)

    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

