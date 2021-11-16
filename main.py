import pygame as pg
import random
from settings import *
from sprites import *
from os import path


class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        # Load high score
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')
        try:
            with open(path.join(self.dir, HS_FILE), 'r') as f: #txt파일에서 highscore 값을 불러오기 세팅에서 정의
                self.highscore = int(f.read()) # 문자열을 정수형으로
        except FileNotFoundError:
            self.highscore = 0

        # load spritesheet image
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        # load sounds 
        self.snd_dir = path.join(self.dir, 'sound')
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Jump.wav'))
        self.jump_sound.set_volume(0.2)

    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pg.sprite.Group() # 모든 sprite
        self.platforms = pg.sprite.Group() # 땅만

        self.player = Player(self)
        self.all_sprites.add(self.player)

        for plat in PLATFORM_LIST: # setting.py에 있는 리스트 불러오기
            p = Platform(self, *plat) # *plat으로 번거로운 작업을 한번에
            self.all_sprites.add(p)
            self.platforms.add(p)
        pg.mixer.music.load(path.join(self.snd_dir,'WayBackthen.ogg'))
        self.run()

    def run(self):
        # Game Loop
        pg.mixer.music.play(-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

        pg.mixer.music.fadeout(500)

    def update(self):
        # Game Loop - Update
        self.all_sprites.update() # 게임의 모든 sprite 업데이트
        # check if player hits a platfrom
        if self.player.vel.y > 0: # 떨어지는 중일때
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.y < lowest.rect.centery:
                    self.player.pos.y = lowest.rect.top + 0.1
                    self.player.vel.y = 0
                    self.player.jumping = False                
        
        if self.player.rect.top <= HEIGHT/3 : # 만약 1/4 지점에 도달하면
            self.player.pos.y += max(abs(self.player.vel.y), 5) # 카메라를 이동해준다
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 5)
                if plat.rect.top >= HEIGHT: # 화면 밖으로 나간 땅은 제거
                    plat.kill()
                    self.score += 10

        #Die
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False
     

        while len(self.platforms) < 6: #남아있는 땅이 6미만일때
            width = random.randrange(50, 100)
            p = Platform(self, random.randrange(0, WIDTH - width),
                         random.randrange(-75, -30))
            self.platforms.add(p) # 땅 그룹에 추가하고
            self.all_sprites.add(p) # 모든 sprite 그룹에 추가한다.

    def events(self):
        # Game Loop - Events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT: # 창을 닫으면 게임종료
                if self.playing:
                    self.playing = False
                self.running = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE: # 스페이스바를 누르면 점프한다.
                    self.player.jump()
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut() 

    def draw(self):
        # Game Loop - Draw
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)
        self.draw_text(str(self.score), 22, BLACK, WIDTH/2, 15)

        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, BLACK, WIDTH/2, HEIGHT/4)
        self.draw_text("Arrows to move, Space to jump",
                       32, BLACK, WIDTH/2, HEIGHT/2)
        self.draw_text("아무키나 누르면 시작합니다",
                       32, BLACK, WIDTH/2, HEIGHT*3/4)
        self.draw_text("High Score : " + str(self.highscore), # 하이스코어 표시
                       32, BLACK, WIDTH/2, 15)                       
        pg.display.flip()
        self.wait_for_key() # 입력 대기

    def show_go_screen(self):
        # game over/continue
        if not self.running:
            return
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 48, BLACK, WIDTH/2, HEIGHT/4)
        self.draw_text("Score : " + str(self.score),
                       32, BLACK, WIDTH/2, HEIGHT/2)
        self.draw_text("Press a key to play again",
                       32, BLACK, WIDTH/2, HEIGHT*3/4)

        if self.score > self.highscore: # 점수를 갱신하면
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!",
                           32, BLACK, WIDTH/2, HEIGHT/2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f: # txt파일에도 업데이트
                f.write(str(self.score))
        else:
            self.draw_text("High Score : " + str(self.highscore),
                           32, BLACK, WIDTH/2, 15)

        pg.display.flip()
        self.wait_for_key()
    
    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

g = Game()
g.show_start_screen() # 게임시작화면 출력
while g.running:
    g.new()
    g.show_go_screen() # 게임오버화면 출력

pg.quit()