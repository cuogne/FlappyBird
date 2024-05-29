import pygame
from pygame.locals import *
import random

#pygame.mixer.pre_init(44100, -16, 2, 4096)

pygame.init()

# fps
clock = pygame.time.Clock()
fps = 60

# size of window
screen_width = 864//2
screen_height = 768

#load images
bg_morning = pygame.image.load('img/background/bg_morning.png')
bg_shine = pygame.image.load('img/background/shine.jpeg')
bg_city = pygame.image.load('img/background/city.jpeg')

#bg = pygame.transform.scale2x(pygame.image.load('img/bg_game.jpeg'))
ground_img = pygame.image.load('img/object/ground.png') #(900x168)
ground_size = ground_img.get_size() 

icon_game = pygame.image.load("img/object/bird2.png")

button_img = pygame.image.load('img/button/restart.png')
button_size = button_img.get_size() # tra ve 1 tuple [0,1] gom width va height (120x42)

game_over_img = pygame.transform.scale2x(pygame.image.load("img/button/gameover.png")) # (192x42 => 384x84)
game_start_img = pygame.transform.scale(pygame.image.load("img/button/start.png"),(145*2.6, 210*2.6)) # (377,546)
'''-----------------------------------------------------------------------------------------------------'''

#sound
hit_sound = pygame.mixer.Sound('sound/sfx_hit.wav') # va cham
hit_sound.set_volume(0.4) # set volume (0,0 -> 1.0) (min and max of volume)
wing_sound = pygame.mixer.Sound('sound/sfx_wing.wav') #vo canh
wing_sound.set_volume(0.4) 
ping_sound = pygame.mixer.Sound('sound/sfx_point.wav') # co diem
ping_sound.set_volume(0.4) 

music_bg = pygame.mixer.Sound('sound/music_background.wav') # nhac nen

''' if add file .mp3
 - <name_variable> = pygame.mixer.music.load('file_name.mp3')
 - play music : pygame.mixer.<name_variable>.play()
 - change volume : pygame.mixer.<name_variable>.get_volume((0.0 -> 1.0))
'''
music = pygame.mixer.music.load('sound/the-flashback_60sec-1-174161.mp3')
'''-----------------------------------------------------------------------------------------------------'''

# create new screen window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')
pygame.display.set_icon(icon_game)

#define font
#font = pygame.font.SysFont('Bauhaus 93', 60)
font = pygame.font.Font('04B_19.TTF',40) # set font cho score

#color
white = (255, 255, 255)
black = (0,0,0)

# variable value game
ground_scroll = 0 # vi tri mat dat di chuyen
scroll_speed = 4 # toc do cuon cua mat dat
pipe_gap = 150 # khoang cach giua 2 pipe tren va duoi
pipe_frequency = 1500 #milliseconds, tan so xuat hien cua ong
last_pipe = pygame.time.get_ticks() - pipe_frequency # thoi diem xuat hien ong cuoi cung
score = 0 # diem so
high_score = 0
#time_click = 1000
#time_reset = 0
'''-----------------------------------------------------------------------------------------------------'''

# variable check status game
run = True
flying = False # trang thai con chim ban dau
game_start = False # check trang thai start game
game_over = False # trang thai endgame
checkSound = False # check am thanh hieu ung hit,wing
pass_pipe = False # trang thai co vuot qua ong hay chua
check_music_bg = False # trang thai cua nhac nen
'''-----------------------------------------------------------------------------------------------------'''

# class and function execute
class Bird(pygame.sprite.Sprite):
    # ham khoi tao
    # x va y xac dinh vi tri xuat phat cua bird
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self) # goi ham khoi tao cua lop co so
		self.list_images = [] # danh sach luu tru hinh anh bird
		self.index = 0 # chi so cua hinh anh
		self.counter = 0 # bien dem de thay doi tao hieu ung animation

		# vong lap duyet qua tung tam hinh va dua vao list_images
		for num in range (1, 4):
			img = pygame.image.load(f"img/object/bird{num}.png")
			self.list_images.append(img)

		self.image = self.list_images[self.index] # hinh anh hien tai cua bird
		self.rect = self.image.get_rect() # set hinh chu nhat xung quanh cho image
		self.rect.center = [x, y] # vi tri cua hcn
		self.vel = 0 # velocity : toc do cua con chim / trong luc
		self.clicked = False # check xem da click chuot hay chua

	def update(self):

		if flying == True: # neu dang trong trang thai bay
			# gravity
			self.vel += 0.5
			if self.vel > 8: # toi da la 8
				self.vel = 8
			if self.rect.bottom < screen_height - ground_size[1]: # vi tri hinh chu nhat duoi 600 (height_window)
				self.rect.y += int(self.vel) # tang theo truoc Oy

		if game_over == False:
			#jump
			# kiem tra xem co click chuot trai hoac an phim space khong
			keys = pygame.key.get_pressed() 
			if (pygame.mouse.get_pressed()[0] == 1 or keys[pygame.K_SPACE]) and self.clicked == False:
				self.clicked = True
				wing_sound.play()
				self.vel = -10 # dich bird len phia tren 10 don vi theo truc Oy

			# khong nhan chuot hoac khong nhan
			if pygame.mouse.get_pressed()[0] == 0 and not keys[pygame.K_SPACE]:
				self.clicked = False

			#handle the animation
			flap_cooldown = 5 # cooldown vo canh cua bird
			self.counter += 1

			if self.counter > flap_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.list_images):
					self.index = 0
				self.image = self.list_images[self.index]

			#rotate the bird
			# goc quay cua con chim se phu thuoc vao toc do cua no
			# => tao hieu ung nhap nho khi nhap chuot
			self.image = pygame.transform.rotate(self.list_images[self.index], self.vel * -2)
		else:
			# xoay dau con chim 90 do de no cam xuong dat
			self.image = pygame.transform.rotate(self.list_images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
	# ham khoi tao
	def __init__(self, x, y, position):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/object/pipe.png")
		self.rect = self.image.get_rect()

		#position variable determines if the pipe is coming from the bottom or top
		#position 1 is from the top, -1 is from the bottom
		# 1 la o tren, -1 la o duoi
		if position == 1 :
			# su dung ham pygame.transform.flip de lat nguoc hinh pipe
			self.image = pygame.transform.flip(self.image, False, True)
			self.rect.bottomleft = [x, y - int(pipe_gap / 2)] # khoang cach giua ong phia tren va duoi

		# neu tu duoi len khi khong can lat hinh
		elif position == -1:
			self.rect.topleft = [x, y + int(pipe_gap / 2)]


	def update(self):
		# dich chuyen ong sang trai dua theo toc do cuon
		self.rect.x -= scroll_speed
		if self.rect.right < 0:
			self.kill()

class ButtonRestart():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

	def draw(self):
		action = False # gia su chua click vao button

		# lay vi tri cua chuot
		pos_mouse = pygame.mouse.get_pos()
  
		# kiem tra xem chuot da nhan vao button chua
		if self.rect.collidepoint(pos_mouse):
			# kiem tra xem bird da cham mat dat chua
			if flappy.rect.bottom >= (screen_height - ground_size[1]):
				if pygame.mouse.get_pressed()[0] == 1 :
					action = True

		#draw button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action

pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height/2))

bird_group.add(flappy)

# function write text
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

# function start game and display screen
def startGame() :
	global run,game_start,flying,check_music_bg
	clock.tick(fps)  # set fps 60
	
	# set background dua theo score
	if score < 3 :
		screen.blit(bg_morning, (0,0)) 
	elif score >= 3 and score < 7 :
		screen.blit(bg_shine,(0,0))
	else :
		screen.blit(bg_city,(-20,-200))

	pipe_group.draw(screen) # ve ong nuoc
	bird_group.draw(screen) # ve chim
	bird_group.update() # cap nhat

	# ve mat dat cuon
	screen.blit(ground_img, (ground_scroll, screen_height - ground_size[1]))
 
	if game_start == False :
		#time_reset += clock.get_rawtime()
		screen.blit(game_start_img, ((screen_width - 377)/2, 140))
		# khi click chuot thi game_start = true => man hinh nay bien mat
		# xu li click trong ham phia ben duoi
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

		# ban dau bird dung yen, an space or click chuot trai moi flying
		keys = pygame.key.get_pressed() 
		if event.type == pygame.MOUSEBUTTONDOWN or keys[pygame.K_SPACE] and not (flying or game_over):
			flying = True
			game_start = True

		# bat nhac nen
		if check_music_bg == False :
			'''loops= -1 => lap lai 1 bai hat'''
			music_bg.play(loops= -1) 
			#pygame.mixer.music.play(loops= -1)
			check_music_bg = True

# function reset game while click on button restart
def reset_game():
	pipe_group.empty()
	flappy.rect.x = 100
	flappy.rect.y = int(screen_height/2)
	score = 0
	return score

# function create object barrier
def createRandomPipe() :
	global last_pipe,ground_scroll
	
 	# flying dc xu li boi startGame() 
	# game_over dc xu li boi checkCollision()
	
	if flying == True and game_over == False:
		#generate new pipes
		time_now = pygame.time.get_ticks()
		if time_now - last_pipe > pipe_frequency:
			pipe_height = random.randint(-100, 100) # chieu cao thanh pipe
			bottom_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1) # random pipe phia duoi
			top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1) # random pipe phia tren
			pipe_group.add(bottom_pipe)
			pipe_group.add(top_pipe)
			last_pipe = time_now

		pipe_group.update()

		ground_scroll -= scroll_speed
		if abs(ground_scroll) > 35:
			ground_scroll = 0

# function check and add score
def checkAndIncreaseScore() :
	global pass_pipe,score
	if len(pipe_group) > 0:
		if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
			and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
			and pass_pipe == False:
			pass_pipe = True
   
		if pass_pipe == True:
			if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
				ping_sound.play()
				score += 1
				pass_pipe = False

# function check collision of bird   
def checkCollision () :
	global game_over,flying
	# dung ham gruopcollide de check va cham voi pipe
	if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0 :
		game_over = True
  
	# neu bird cham san ben duoi (ground_img 600)
	if flappy.rect.bottom >= (screen_height - ground_size[1]): # (768 - 168)
		game_over = True
		flying = False

# function check gameover and display notice gameover  
def checkAndDrawGameOver() :
	global high_score,checkSound,game_start,game_over,score
	
	if game_over == False :
		draw_text(f'Score : {str(score)}', font, white, 20, 20)
	
	else : # (game_over == True)
		screen.blit(game_over_img,((screen_width - 384)/2,120))

		if checkSound == False :
			hit_sound.play()
			checkSound = True

		if score > high_score :
			high_score = score

		draw_text(f'Score : {str(score)}', font, white, (screen_width)/2 - 90, screen_height/2 - 100)
		draw_text(f'High Score : {str(high_score)}', font, white, (screen_width)/2 - 135, screen_height/2 + 25)

		button = ButtonRestart((screen_width - button_size[0])/2, screen_height/2 + 150, button_img)

		if button.draw():
			game_over = False
			checkSound = False
			game_start = False
			score = reset_game()

while run:
	startGame()
	createRandomPipe()
	checkAndIncreaseScore()
	checkCollision()
	checkAndDrawGameOver()
	pygame.display.update()
pygame.quit()