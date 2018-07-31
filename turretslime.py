import pygame
import random

class Sprite:
    def __init__(self, sprite_type, pos, double = False, flip_lengthwise = False, flip_heightwise = False, direction = 0, num_o_animation_cycles = 1):
        self.orig_img = pygame.image.load(sprite_type).convert_alpha()
        self.direction = direction
        self.what_to_blit = img_splitter(num_o_animation_cycles, self.orig_img)
        self.position = pos
        self.flip_horizontally = flip_lengthwise
        self.flip_vertically = flip_heightwise
        self.animation_timer = 0
        self.time_between_animations = 10
        self.animation_index = 0
        self.img = self.next_img()
        for x in range(len(self.what_to_blit)):
            if direction != 0:
                self.what_to_blit[x] = pygame.transform.rotate(self.what_to_blit[x], direction)
            if flip_lengthwise or flip_heightwise:
                self.what_to_blit[x] = pygame.transform.flip(self.what_to_blit[x], self.flip_horizontally, self.flip_vertically)
            if double:
                self.what_to_blit[x] = pygame.transform.scale2x(self.what_to_blit[x])
    def blitme(self, screen):
        screen.blit(self.next_img(), self.position)
        self.img = self.next_img()
        img_rect = self.img.get_rect()
        if self.get_health() is not None:
            pygame.draw.line(screen, (255,0,0),(self.position[0], self.img.get_rect().height + self.position[1]), (self.position[0] + (self.get_health() * img_rect.width / 100), self.img.get_rect().height + self.position[1]))
    def get_rect(self):
        rect = self.img.get_rect()
        return rect.move(self.position)
    def off_screen(self, screen):
        screen_rect = screen.get_rect()
        my_rect = self.get_rect()
        return not screen_rect.colliderect(my_rect)
    def get_health(self):
        return None
    def next_img(self):
        next_img = self.what_to_blit[self.animation_index]
        if self.animation_timer == self.time_between_animations:
            self.animation_index += 1
            self.animation_timer = 0
        if self.animation_index == len(self.what_to_blit):
            self.animation_index = 0
        self.animation_timer +=1
        return next_img

class Turret(Sprite):
    def __init__(self, pos):
        super().__init__("assets/towers/matter/3_left.png", pos)
        self.counter = 1
        self.health = 100
    def update(self):
        if self.counter == 10:
            bullet = Bullet((self.position[0], self.position[1] + 10), 0)
            self.counter = 1
            return bullet
        else:
            self.counter += 1
    def get_health(self):
        return self.health
    def collide_taking_dmg(self, hurtful_obj):
        if type(hurtful_obj) == EnemyBlob:
            self.health -= 25
        if self.health <= 0:
            return [hurtful_obj, self]
        else:
            return [hurtful_obj]
            
class EnemyBlob(Sprite):
    def __init__(self, pos):
        super().__init__("assets/monster/slime1_side.png", pos, double = True, flip_lengthwise = True, num_o_animation_cycles = 4)
        self.health = 100
    def get_health(self):
        return self.health
    def collide_taking_dmg(self, hurtful_obj):
        if type(hurtful_obj) == Bullet:
            self.health -= 10
        elif type(hurtful_obj) == Missile:
            self.health -= 75
        if self.health <= 0:
            return [hurtful_obj,self]
        else:
            return [hurtful_obj]
    def update(self):
        self.position = (self.position[0] + 1, self.position[1])

class Bullet(Sprite):
    def __init__(self, pos, direction):
        super().__init__("assets/other/shockwave.png", pos, direction, num_o_animation_cycles = 9)
        self.what_to_blit = append_reverse(self.what_to_blit)
    def update(self):
        self.position = (self.position[0] - 10, self.position[1])
        
class Missile(Sprite):
    def __init__(self,pos):
        super().__init__("assets/other/rocket.png",pos, direction = 180)
    def update(self):
        self.position = (self.position[0] - 1, self.position[1])

def collision_detection(obj1, obj2):
    obj1_rect = obj1.get_rect()
    obj2_rect = obj2.get_rect()
    if obj1_rect.colliderect(obj2_rect):
        return True
    return False

def process_collision(list1, list2):
    dellist = []
    for obj1 in list1:
        for obj2 in list2:
            if collision_detection(obj1, obj2):
                dellist.extend(obj1.collide_taking_dmg(obj2))
    return dellist

def img_splitter(num_o_imgs, img):
    if type(img) == str:
        img = pygame.image.load(img).convert_alpha()
    list_of_imgs = []
    img_rect = img.get_rect()
    H_many_pixels_to_go = img_rect.width / num_o_imgs
    top_left_o_img = 0
    for timer in range(num_o_imgs):
        img_surface = pygame.Surface((H_many_pixels_to_go, img_rect.height), pygame.SRCALPHA, 32)
        individual_img = pygame.Rect((top_left_o_img, 0), (H_many_pixels_to_go, img_rect.height))
        img_surface.blit(img, (0,0), individual_img)
        top_left_o_img += H_many_pixels_to_go
        list_of_imgs.append(img_surface)
    return list_of_imgs

def append_reverse(flippin_list):
    other_list_nums = list(range(0, len(flippin_list)-2))
    list_nums = list(range(1, len(flippin_list)-1))
    completed_list = flippin_list
    flipped_list_nums = list(reversed(list_nums))
    for iterating in other_list_nums:
        completed_list.append(flippin_list[flipped_list_nums[iterating]])
    return completed_list

Clock = pygame.time.Clock()

(width, height) = (800, 600)
bg_surface = pygame.Surface((width,height))
pixel_grass = pygame.image.load("assets/background/rPixel_Grass_mirror.png")
pixel_grass_rect = pixel_grass.get_rect()
for x in range (0, 800, pixel_grass_rect.width):
    for y in range(0, 600, pixel_grass_rect.height):
        bg_surface.blit(pixel_grass, (x,y))

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pygame Tower Defense")

spritesOnScreen = []
running = True
enemyspawnrate = 50
enemyspawn = enemyspawnrate
while running:
    screen.blit(bg_surface, (0,0))
    new_sprites = []
    bullets = []
    enemies = []
    turrets = []
    delsprites = []
    if enemyspawn == enemyspawnrate:
        dada = EnemyBlob((10, 10))
        spritesOnScreen.append(dada)
        enemyspawn = 0
    else:
        enemyspawn += 1
    Clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            pos = event.pos
            missile = Missile(pos)
            spritesOnScreen.append(missile)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            ethan = Turret(pos)
            spritesOnScreen.append(ethan)
        elif event.type == pygame.QUIT:
            running = False
    for a in spritesOnScreen:
        b = a.update()
        if not a.off_screen(screen):
            if isinstance(a, Bullet) or isinstance(a, Missile):
                bullets.append(a)
            if isinstance(a, EnemyBlob):
                enemies.append(a)
            if isinstance(a, Turret):
                turrets.append(a)
        else:
            delsprites.append(a)
        if b:
            new_sprites.append(b)
        a.blitme(screen)
    delsprites.extend(process_collision(enemies, bullets))
    delsprites.extend(process_collision(turrets, enemies))
    spritesOnScreen.extend(new_sprites)
    for x in delsprites:
        if x in spritesOnScreen:
            spritesOnScreen.remove(x)
    pygame.display.flip()

pygame.display.quit()
pygame.quit()