import pygame
import random,time,os

#常量：
W,H=800 ,765  #背景图大小
FPS=30
#设置
pygame.init()
SCREEN=pygame.display.set_mode((W,H))
pygame.display.set_caption('小女警极限穿越')#游戏框名字
CLOCK=pygame.time.Clock()
#引用字典
IMAGES = {}
for image in os.listdir('assets/sprites'):
    name, extension = os.path.splitext(image)  #文件名和后缀分开检索
    path = os.path.join('assets/sprites',image)
    IMAGES[name]  = pygame.image.load(path)  #引用方法及贴入
#音频文件设置和调用
AUDIO = {}                                
for audio in os.listdir('assets/audio'):
    name, extension = os.path.splitext(audio)
    path = os.path.join('assets/audio',audio)
    AUDIO[name] = pygame.mixer.Sound(path)


#主函数
def main():
    
    while True:
        # 播放全程音乐
        AUDIO['1'].play()
        #定义水管
        pipe=IMAGES['pipe']
        IMAGES['pipes']=[pipe,pygame.transform.flip(pipe,False,True)]

        menu_window()
        result=game_window()
        if result['score'] < 20:
             end_fail_window(result)
        else:
            end_success_window(result)
        
def menu_window():
        
    while True:
        #获取按键信息并作出改变
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                quit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_SPACE:
                return
        SCREEN.blit(IMAGES['bgpic1'],(0,0))
        SCREEN.blit(IMAGES['birds'],(W*0.2,H*0.4))
        pygame.display.update() #刷新窗口
        CLOCK.tick(FPS)


def game_window():

    score = 0
    
    AUDIO['flap'].play()
    
    bird = Bird(W*0.2,H*0.4)

    #出现水管组
    distance = random.randint(315,415)
    n = 4
    pipe_gap = random.randint(220,250)   #水管上下距离
    pipe_group = pygame.sprite.Group()
    for i in range(n):
        pipe_y = random.randint(int(H*0.55),int(H*0.9))          #第一组下水管长
        pipe_up = Pipe(W + i * distance, pipe_y,True)
        pipe_down = Pipe(W + i * distance, pipe_y - pipe_gap,False)
        pipe_group.add(pipe_up)
        pipe_group.add(pipe_down)

    while True:
        flap=False
        #获取按键信息并作出改变
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:      #按键飞行
                if event.key== pygame.K_SPACE:
                    flap = True
                    AUDIO['flap'].play()

        #更新小鸟
        bird.update(flap)

        #更新水管
        first_pipe_up = pipe_group.sprites()[0]
        first_pipe_down = pipe_group.sprites()[1]
        if first_pipe_up.rect.right < 0:
            pipe_y = random.randint(int(H*0.55),int(H*0.90))            #下水管长
            new_pipe_up = Pipe(first_pipe_up.rect.x + n * distance, pipe_y, True)
            new_pipe_down = Pipe(first_pipe_down.rect.x + n * distance, pipe_y-pipe_gap, False)
            pipe_group.add(new_pipe_up)
            pipe_group.add(new_pipe_down)
            first_pipe_up.kill()
            first_pipe_down.kill()
        pipe_group.update()


        #输赢判断
        if bird.rect.y > H-90 or bird.rect.y < 0 or pygame.sprite.spritecollideany(bird, pipe_group):
            #碰到边框死亡,以及碰到水管死亡
            bird.dying = True
            AUDIO['1'].stop()
            AUDIO['hit'].play()
            AUDIO['die'].play()
            result = {'bird':bird, 'pipe_group':pipe_group, 'score':score}
            return result

        if score == 20:
            AUDIO['1'].stop()
            AUDIO['success'].play()
            result = {'bird':bird, 'pipe_group':pipe_group, 'score':score}
            return result

        #记录得分
        if bird.rect.left + first_pipe_up.x_vel < first_pipe_up.rect.centerx < bird.rect.left: #以水管中心为界，两帧位置在线前后
            AUDIO['score'].play()
            score += 1



        #屏幕显示
        SCREEN.blit(IMAGES['bgpic2'],(0,0))
        pipe_group.draw(SCREEN)
        show_score(score)
        SCREEN.blit(bird.image,bird.rect)


        pygame.display.update()
        CLOCK.tick(FPS)

        

def end_fail_window(result):
    bird = result['bird']
    pipe_group = result['pipe_group']
    score = result['score']

    while True:

        if bird.dying:
            bird.go_die()
        else:
            #获取按键信息并作出改变
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return

        bird.go_die()
        SCREEN.blit(IMAGES['bgpic3'],(0,0))
        pipe_group.draw(SCREEN)
        SCREEN.blit(IMAGES['gameover'],(W * 0.1, H * 0.5))
        show_score(score)
        SCREEN.blit(bird.image,bird.rect)
        pygame.display.update()
        CLOCK.tick(FPS)

def end_success_window(result):
    bird = result['bird']
    pipe_group = result['pipe_group']
    score = result['score']
    while True:
        #获取按键信息并作出改变
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        SCREEN.blit(IMAGES['bgpic4'], (0, 0))
        pipe_group.draw(SCREEN)
        show_score(score)
        SCREEN.blit(bird.image, bird.rect)
        pygame.display.update()
        CLOCK.tick(FPS)

def show_score(score):
    score_str = str(score)
    n = len(score_str)
    w = IMAGES['0'].get_width() * 2
    x = (W - n * w) /2
    y = H *0.1
    for number in score_str:
        SCREEN.blit(IMAGES[number],(x,y))
        x += w

class Bird:
    def __init__(self,x,y):
        self.image=IMAGES['birds']
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.y_vel = -10     #小鸟初始速度向上
        self.max_y_vel = 10  #y方向上的小鸟能到达的最大速度
        self.gravity = 1     #引入重力加速度

        self.rotate=20       #初始角度（pygame中水平向右为0度）
        self.max_rotate=-20  #最大角度
        self.rotate_vel=-2   #角度每帧向下变化角度

        self.y_vel_after_flap=-10   #拍打翅膀后的初速度
        self.rotate_after_flap=20   #拍打出榜后的初角度

        self.dying = False



    def update(self,flap=False):
        if flap:
            self.y_vel=self.y_vel_after_flap
            self.rotate=self.rotate_after_flap

        self.y_vel=min(self.y_vel+self.gravity,self.max_y_vel)
        self.rect.y+=self.y_vel         #改变y速度
        self.rotate=max(self.rotate+self.rotate_vel,self.max_rotate)  #改变角度

        self.image=IMAGES['birds']
        self.image=pygame.transform.rotate(self.image,self.rotate)

    def go_die(self):
        if self.rect.y < H-90:
            self.rect.y += self.max_y_vel
            self.rotate = -90
            self.image = IMAGES['birds']
            self.image=pygame.transform.rotate(self.image,self.rotate)
        else:
            self.dying = False

class Pipe(pygame.sprite.Sprite):
    def __init__(self,x,y,upwards=True):
        pygame.sprite.Sprite.__init__(self)
        if upwards:
            self.image = IMAGES['pipes'][0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.top = y
        else:
            self.image = IMAGES['pipes'][1]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.bottom = y
        self.x_vel = -4
    def update(self):
        self.rect.x += self.x_vel

main()