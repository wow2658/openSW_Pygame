# game options/settings
TITLE = "Jumpy"
WIDTH = 480 #가로
HEIGHT = 600 #세로
FPS = 60
FONT_NAME = '' #나눔고딕
HS_FILE = "highscore.txt" #점수기록 txt
SPRITESHEET = "woowang.png" 

# Player properties
PLAYER_ACC = 1.5 # 플레이어 초기 가속도
PLAYER_FRICTION = -0.2 # 플레이어 초기 마찰계수
PLAYER_GRAVITY = 0.8 # 플레이어가 받는 중력계수
PLAYER_JUMP = 20

# Starting platforms 발판 크기와 위치 리스트
PLATFORM_LIST = [(0, HEIGHT - 60),
                 (WIDTH/2 - 50, HEIGHT*3/4),
                 (125, HEIGHT - 350),
                 (350, 200),
                 (175, 100)]

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 155)
BGCOLOR = WHITE