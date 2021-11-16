import pygame as pg
from settings import *
from random import choice
vec = pg.math.Vector2


class Spritesheet:
    # Utility class for loading spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # Grab an image out of a lager spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width//2, height//2))
        return image


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game

        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0

        self.load_images()
        self.image = self.standing_frames[0]

        self.rect = self.image.get_rect()
        self.rect.center = (40, HEIGHT - 100)

        self.pos = vec(40, HEIGHT - 100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self): # 스프라이트 시트 적용
        self.standing_frames = [self.game.spritesheet.get_image(159, 303, 161, 196), # xml 좌표
                                self.game.spritesheet.get_image(144, 515, 138, 196)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)

        self.walk_frames_r = [self.game.spritesheet.get_image(384, 88, 159, 215),
                              self.game.spritesheet.get_image(0, 303, 159, 212)]
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)

        self.walk_frames_l = [pg.transform.flip(frame, True, False)
                              for frame in self.walk_frames_r]

        self.jump_frame = self.game.spritesheet.get_image(144, 515, 138, 196)
        self.jump_frame.set_colorkey(BLACK)

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

    def jump(self):
        # jump only if standing on a platform
        self.rect.y += 0.1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 0.1

        if hits and not self.jumping:
            self.game.jump_sound.play()# 충돌검사를 정확하게 하기 위해 캐릭터를 바닥을 살짝 뚫게 내림
            self.jumping = True
            self.vel.y = -PLAYER_JUMP    

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAVITY)
        keys = pg.key.get_pressed() # 키 입력

        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        self.acc.x += self.vel.x*PLAYER_FRICTION # 무한한 가속 방지 마찰계수
        self.vel += self.acc # 속도는 초기속도 + 가속도*시간 공식
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5*self.acc # 변위는 초기위치 + 1/2a^2 공식 

        #화면 가두기
        if self.pos.x > WIDTH - self.rect.width/2:
            self.pos.x = WIDTH - self.rect.width/2
        if self.pos.x < 0 + self.rect.width/2:
            self.pos.x = 0 + self.rect.width/2

        self.rect.midbottom = self.pos # 캐릭터 위치 갱신, midbottom으로 가운데아래로 피벗

    def animate(self):
        now = pg.time.get_ticks()

        if self.vel.x != 0: # 속도가 0이 아니라면
            self.walking = True # 움직이는 상태
        else:
            self.walking = False

        if self.walking: # 걷기 애니메이션
            if now - self.last_update > 200: # 200ms마다 이미지를 업데이트
                self.last_update = now
                self.current_frame = ((self.current_frame + 1) # 다음동작 업로드
                                      % len(self.walk_frames_l))

                bottom = self.rect.bottom
                if self.vel.x > 0: # 속도가 양수면 오른쪽
                    self.image = self.walk_frames_r[self.current_frame]
                else: # 음수면 왼쪽
                    self.image = self.walk_frames_l[self.current_frame]
                    self.rect = self.image.get_rect()
                    self.rect.bottom = bottom # 스프라이트 피벗을 캐릭터 발에

        if not self.jumping and not self.walking: # 서있는 애니메이션 IDLE
            if (now - self.last_update) > 350: # 350ms 마다
                self.last_update = now
                self.current_frame = ((self.current_frame + 1)
                                      % len(self.standing_frames))
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom



class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.game = game

        images = [self.game.spritesheet.get_image(0, 0, 384, 88),
                  self.game.spritesheet.get_image(384, 0, 202, 88)]


        self.image = choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y