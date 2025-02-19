import os
import pygame
import time
import random

import menu
import end
import methods
import pause_menu

import datetime

shots_count = 0


pygame.init()
width, height = 1000, 750
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Space Shooter')


WIDTH = 115  # Длина корабля
HEIGHT = 155  # Ширина корабля
ENEMY_RELOAD = 20

score = 0
money = 0
startTime = time.time()

laser_timestamps = []
pauses = []

fone_image = pygame.image.load('images/fone2.jpg')  # Загрузка фона
fone_image = pygame.transform.scale(fone_image, (width, height))

star_image = pygame.Surface((width, height), pygame.SRCALPHA)
for _ in range(100):  # Создаем 100 случайных звезд
    x = random.randint(0, width)
    y = random.randint(0, height)
    pygame.draw.circle(star_image, (255, 255, 255), (x, y), random.randint(1, 3))

# Параметры движения фона
background_speed = 1 # Скорость движения фона
y_offset = 1  # Смещение по вертикали для эффекта движения

fps = 120  # Кадры в секунду

class StockProperties:
    enemiesSpeed, enemiesHp = 1, 100
    playerSpeed = 15
    timerEnemies = 670

class Properties: 
    def __init__(self):
        lvl = methods.getLvlDiff()
        coff, coffTimer = 0.05, 0.5
        self.enemiesSpeed = StockProperties.enemiesSpeed + (lvl * coff) if lvl > 1 else StockProperties.enemiesSpeed
        self.enemiesHp = StockProperties.enemiesHp + (lvl * coff) if lvl > 1 else StockProperties.enemiesHp
        self.timerEnemies = int(round(StockProperties.timerEnemies + (lvl * coffTimer) if lvl > 1 else StockProperties.timerEnemies, 0))
        self.needScore = int(round(20 * lvl * 1.25, 0))

        self.reloadTime = methods.getStatsElem('Cooldown')
        self.playerHealth = methods.getStatsElem('Health')
        self.fireRate = methods.getStatsElem('FireRate')

properties = Properties()


class Enemy(pygame.sprite.Sprite):  # Класс противников
    def __init__(self, enemy_x, image, hp, offsetY):
        super().__init__()
        self.image = pygame.image.load(f'images/{image}')
        self.image = pygame.transform.scale(self.image, (90, 90))
        self.rect = self.image.get_rect()
        self.rect.x = enemy_x
        self.rect.y = 100
        self.offsetY = offsetY
        self.enemy_speed = properties.enemiesSpeed
        self.hp = properties.enemiesHp
        self.indexContusion = 0

    def update(self):  # Движение противников в функции update
        if contusion:
            self.indexContusion = (self.indexContusion + 1) % 4
            if self.indexContusion != 3:
                return
        self.rect.y += self.enemy_speed
        self.rect.x += self.offsetY
        if self.rect.x < 0 or self.rect.x + self.image.get_width() > width:
            self.offsetY = -self.offsetY


class Laser(pygame.sprite.Sprite):  # Класс снаряда
    def __init__(self, laser_x, laser_y):
        super().__init__()
        self.image = pygame.image.load(f'images/bullet_{methods.getBulletCount()}.png')
        self.image = pygame.transform.scale(self.image, (20, 38))
        self.rect = self.image.get_rect()
        self.rect.x = laser_x
        self.rect.y = laser_y
        self.laser_speed = 8

    def update(self):  # Движение снаряда в функции update
        self.rect.y -= self.laser_speed

        

class Player(pygame.sprite.Sprite):  # Класс игрока
    def __init__(self, player_x):
        super().__init__()
        self.image = pygame.image.load(methods.getSpaceship() if methods.getLvl() <= 20 else "Ships/ship_lvl_20.png")
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = 550
        self.player_speed = 15

        self.fires_sizes = {
            '1, 2, 3, 4, 5, 6, 7, 8, 9': (25, 50),
            '10, 11, 12, 13, 14': (40, 70),
             f'{", ".join([str(i) for i in range(15, 500)])}': (40, 70)
        }
        self.fire_images = []
        for i in range(8):
            img = pygame.image.load(os.path.join('fires', f'00{i}.png'))
            for i, j in self.fires_sizes.items():
                if methods.getIndexShip() in list(map(int, i.split(', '))):
                    img = pygame.transform.scale(pygame.transform.rotate(img, 180), j)
            self.fire_images.append(img)
        
        self.frame_index = 0
        self.frame_count = len(self.fire_images)

        self.reloadFire = time.time()

    def update(self):
        self.fires_rect = {
            '1, 2, 3, 4': [(self.rect.x + self.image.get_width() // 2.5, 
                            self.rect.y + self.image.get_height() - 12)],

            '5, 6, 7, 8, 9': [(self.rect.x + self.image.get_width() // 8, 
                               self.rect.y + self.image.get_height() + 3),
                              (self.rect.x + self.image.get_width() // 1.5, 
                               self.rect.y + self.image.get_height() + 3)],

            '10, 11, 12, 13, 14': [(self.rect.x + self.image.get_width() // 3, 
                                    self.rect.y + self.image.get_height() - 10)],

            f'{", ".join([str(i) for i in range(15, 500)])}': [(self.rect.x + self.image.get_width() // 8,
                               self.rect.y + self.image.get_height() + 3),
                              (self.rect.x + self.image.get_width() // 1.5,
                               self.rect.y + self.image.get_height() + 3)]
        }
        if time.time() >= self.reloadFire:
            self.frame_index = (self.frame_index + 1) % self.frame_count
            for i, j in self.fires_rect.items():
                if methods.getIndexShip() in list(map(int, i.split(', '))):
                    for x in j:
                        screen.blit(self.fire_images[self.frame_index], x)
            self.reloadFire = time.time() + 0.01
        
        
        


class BorderUp(pygame.sprite.Sprite):  # Класс, создающий верхнюю границу, чтобы при столкновении с ней противники
    def __init__(self, x1, y1, x2, y2):  # отнимали жизнь и удалялись из группы спрайтов противников.
        super().__init__()
        self.add(horizontal_border_up)
        self.image = pygame.Surface([x2 - x1, 1])
        self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class BorderDown(pygame.sprite.Sprite):  # Класс, создающий нижнюю границу, чтобы при столкновении с ней снаряды
    def __init__(self, x1, y1, x2, y2):  # удалялись из группы спрайтов снарядов.
        super().__init__()
        self.add(horizontal_border_down)
        self.image = pygame.Surface([x2 - x1, 1])
        self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


def getDuration():
    duration = int(round(time.time() - startTime - sum(pauses)))
    return (duration // 60, duration - (60 * (duration // 60)))


def draw():
    enemiesSprites.update()  # .            Она также обновляет положение объектов, а также
    lasersSprites.update()  # .             отображает счёт и количество жизней.
    spaceShips.update()
    enemiesSprites.draw(screen)
    lasersSprites.draw(screen)
    spaceShips.draw(screen)
    renderHealth()
    renderScore()
    renderMoney()
    renderBackrounds()
    renderLvl()
    renderTime()
    pygame.display.flip()


def renderScore():  # Функция, которая создает надпись со счётом.
    font = pygame.font.Font(methods.load_font("PressStart2P-Regular"), 20)
    text = font.render(f"Счет: {score}/{properties.needScore}", 1, (255, 255, 255))
    text_x = 730
    text_y = 20
    screen.blit(text, (text_x, text_y))


def renderMoney():  # Функция, которая создает надпись с монетами.
    font = pygame.font.Font(methods.load_font("PressStart2P-Regular"), 20)
    text = font.render(f"Монеты: {money}", 1, (255, 255, 255))
    text_x = 730
    text_y = 80
    screen.blit(text, (text_x, text_y))


def renderBackrounds():  # Функция, которая создает фоны.
    pass

def renderHealth():  # Функция, которая создает полосу здоровья
    hbrWidth, hbrHeight = 250, 10
    pygame.draw.rect(screen, (255, 0, 0), (70, 30, hbrWidth, hbrHeight), border_radius=10)
    hRatio = curHealth / maxHealth
    curHbrWidth = hbrWidth * hRatio
    pygame.draw.rect(screen, (0, 255, 0), (70, 30, curHbrWidth, hbrHeight), border_radius=10)


def renderReload():  # Функция, которая создает полосу перезарядки
    relWidth, relHeight = 250, 10
    pygame.draw.rect(screen, (181, 184, 177), (70, 50, relWidth, relHeight), border_radius=10)
    hRatio = (reloadTime - time.time()) / properties.reloadTime
    curRelWidth = relWidth * hRatio
    pygame.draw.rect(screen, (66, 170, 255), (70, 50, curRelWidth, relHeight), border_radius=10)

def renderSuper(index):  # Функция, которая создает полосу супера
    if index == 1:
        rectY, color = 70, (251, 0, 255)
    else:
        rectY, color = 90, (255, 200, 0)
    supWidth, supHeight = 250, 10
    pygame.draw.rect(screen, (181, 184, 177), (70, rectY, supWidth, supHeight), border_radius=10)
    hRatio = (supers[index][1] - time.time()) / 5
    curSupWidth = supWidth * hRatio
    pygame.draw.rect(screen, color, (70, rectY, curSupWidth, supHeight), border_radius=10)


def renderLvl():
    font = pygame.font.Font(methods.load_font("PressStart2P-Regular"), 20)
    text = font.render(f"Уровень: {methods.getLvlDiff()}", 1, (255, 255, 255))
    text_x = 400
    text_y = 80
    screen.blit(text, (text_x, text_y))

def renderTime():
    duration = getDuration()
    font = pygame.font.Font(methods.load_font("PressStart2P-Regular"), 20)
    text = font.render(f"{duration[0]}:{duration[1]}", 1, (255, 255, 255))
    text_x = 460
    text_y = 20
    screen.blit(text, (text_x, text_y))


def play_shot_sound():
    # shotSound = pygame.mixer.Sound(os.path.join("Sounds", "Shot.mp3"))
    # shotSound.play()
    pass

def shot(num_lasers):
    global shots_count

    # Убеждаемся, что laser_timestamps имеет правильное количество списков для отслеживания каждого лазера
    while len(laser_timestamps) < num_lasers:
        laser_timestamps.append([])
    while len(laser_timestamps) > num_lasers:
        laser_timestamps.pop()

    fire_rate = properties.fireRate

    if num_lasers == 1:
        # Обработка одного лазера:
        x_offset = 55  # Горизонтальный сдвиг от центра корабля для позиции лазера
        if len(laser_timestamps[0]) == 0: #Если еще не было выстрелов для этого лазера
            lasersSprites.add(Laser(spaceship.rect.x + x_offset, spaceship.rect.y)) # Создание и добавление нового лазера
            laser_timestamps[0].append(time.time()) #Запись метки времени выстрела
            play_shot_sound()
        else:
            #Проверка, прошло ли достаточно времени с момента последнего выстрела
            if (time.time() - laser_timestamps[0][-1]) > fire_rate:
                shots_count += 1 # Увеличение счетчика выстрелов
                lasersSprites.add(Laser(spaceship.rect.x + x_offset, spaceship.rect.y)) # Создание и добавление нового лазера
                laser_timestamps[0].append(time.time()) #Запись метки времени выстрела
                play_shot_sound()

    else:
        # Обработка нескольких лазеров:
        total_width = 75 - 35  # Общая ширина, доступная для размещения лазеров
        base_offset = 35  # Начальный сдвиг от корабля
        spacing_multiplier = 2.5  # Множитель для регулировки расстояния между лазерами

        spacing = (total_width / (num_lasers + 1)) * spacing_multiplier # Расчет расстояния между лазерами

        # Расчет начального смещения для центрирования лазеров
        start_offset = base_offset + (total_width - spacing * (num_lasers - 1)) / 2 if num_lasers > 1 else base_offset

        for i in range(num_lasers):
            x_offset = start_offset + spacing * i #Расчет x-смещения для каждого лазера

            if len(laser_timestamps[i]) == 0: #Если еще не было выстрелов для этого лазера
                lasersSprites.add(Laser(spaceship.rect.x + x_offset, spaceship.rect.y)) #Создание и добавление нового лазера.
                laser_timestamps[i].append(time.time()) #Запись метки времени выстрела
                play_shot_sound()
            else:
                #Проверка, прошло ли достаточно времени с момента последнего выстрела для этого конкретного лазера
                if (time.time() - laser_timestamps[i][-1]) > fire_rate:
                    shots_count += 1 / num_lasers # Увеличение счетчика выстрелов (деленное на num_lasers, потому что это многократный выстрел)
                    lasersSprites.add(Laser(spaceship.rect.x + x_offset, spaceship.rect.y)) #Создание и добавление нового лазера
                    laser_timestamps[i].append(time.time()) #Запись метки времени выстрела
                    play_shot_sound()


def looseGame():
    duration = getDuration()
    methods.addNoteHistory(datetime.datetime.now().strftime('%d.%m.%Y'), f'{duration[0]} m {duration[1]} s', 0)
    pygame.mixer.music.stop()

    pygame.mixer.music.load(os.path.join("Sounds", "Lose theme.mp3"))
    pygame.mixer.music.play()

    end.End_screen(screen, "defeat", money, startNewGame, width=width, height=height)


def winGame():
    duration = getDuration()
    methods.addNoteHistory(datetime.datetime.now().strftime('%d.%m.%Y'), f'{duration[0]} m {duration[1]} s', 1)
    pygame.mixer.music.stop()

    pygame.mixer.music.load(os.path.join("Sounds", "Victory theme.mp3"))
    pygame.mixer.music.play()

    methods.up_lvl_of_difficulty()

    end.End_screen(screen, "victory", money, startNewGame, width=width, height=height)

# Группы всех спрайтов.
enemiesSprites = pygame.sprite.Group()
lasersSprites = pygame.sprite.Group()
spaceShips = pygame.sprite.Group()

horizontal_border_up = pygame.sprite.Group()  # Создание группы верхней границы и экземпляра верхней границы.
BorderUp(0, 0, 1000, 0)


horizontal_border_down = pygame.sprite.Group()  # Создание группы нижней границы и экземпляра нижней границы.
BorderDown(0, 1000, 1000, 1000)


spaceship = Player(1000 / 2 - 64)  # Создание группы игрока и экземпляра самого игрока.
shipW, shipH = spaceship.image.get_width(), spaceship.image.get_height()
spaceShips.add(spaceship)

clock = pygame.time.Clock()  # Отсчёт кол-ва миллисекунд для задержки отрисовки.

run = True

pygame.time.set_timer(ENEMY_RELOAD, properties.timerEnemies)  # Таймер для отсчёта времени, после окончания которого появляется противник.


enemies = {
    1: {
        'image': 'enemy1.png',
        'hp': 100
    },
    2: {
        'image': 'enemy2.png',
        'hp': 100
    },
    3: {
        'image': 'enemy3.png',
        'hp': 100
    },
    4: {
        'image': 'enemy4.png',
        'hp': 100
    },
    5: {
        'image': 'enemy5.png',
        'hp': 100
    }
}

maxHealth = properties.playerHealth
curHealth = maxHealth

def updateHealth():
    global maxHealth, curHealth
    maxHealth = properties.playerHealth
    curHealth = maxHealth

def startNewGame():
    spaceship.rect.x = 1000 / 2 - 64
    spaceship.rect.y = 550

    for i in enemiesSprites:
        enemiesSprites.remove(i)
        
    for i in lasersSprites:
        lasersSprites.remove(i)

    pauses.clear()

    updateHealth()
    global score, rel, money, startTime, properties
    score = 0
    money = 0
    startTime = time.time()
    rel = False
    properties = Properties()
    supers[1] = [False]
    supers[2] = [False]

    pygame.time.set_timer(ENEMY_RELOAD, properties.timerEnemies)

def disablePause():
    pauses.append(int(round(time.time() - pauseTime, 0)))

dragging = False

mainMenu = menu.Menu(screen, startNewGame, width=width, height=height)
mainMenu.menu.enable()

pauseMenu = pause_menu.Menu(screen, startNewGame, disablePause, width=width, height=height)
pauseMenu.menu.disable()

rel = False
reloadTime = time.time()

pause_button = pygame.transform.scale(pygame.image.load('menu_images/pause_button.png'), (45, 45))
pauseTime = 0

super1 = pygame.transform.scale(pygame.image.load('menu_images/super1.png'), (50, 50))
super2 = pygame.transform.scale(pygame.image.load('menu_images/super2.png'), (50, 50))

loading = True

contusion = False

supers = {
    1: [False],
    2: [False]
}

def renderLoadPerc(perc):
    font = pygame.font.Font(methods.load_font("PressStart2P-Regular"), 25)
    text = font.render(f"{perc}%", 1, (255, 255, 255))
    screen.blit(text, (850, height // 2 + 35))

def startLoading():
    global loading, run

    font = pygame.font.Font(methods.load_font('PressStart2P-Regular'), 60)

    clock = pygame.time.Clock()
    progress = 0
    dots = 0
    timeRend = time.time()
    while loading and run:
        for event in pygame.event.get():
            run = False if event.type == pygame.QUIT else run

        # Заполнение фона
        screen.blit(pygame.transform.scale(pygame.image.load('images/fone3.jpg'), (width, height)), (0, 0))

        # Отображение текста "Загрузка..."
        if time.time() >= timeRend:
            dots += 1 if dots < 3 else -3
            timeRend = time.time() + 0.3
        loading_text = font.render(f"Загрузка{''.join(['.' for i in range(dots)])}", True, (255, 255, 255))
        screen.blit(loading_text, (width // 2 - loading_text.get_width() // 2,
                                   height // 2 - loading_text.get_height() // 2 - 50))


        # Рисуем лоад бар
        bar_width = 600
        bar_height = 50
        bar_x = (width - bar_width) // 2
        bar_y = height // 2 + 20
        
        # Рисуем рамку для лоад бара
        pygame.draw.rect(screen, (31, 12, 242), (bar_x, bar_y, bar_width, bar_height), 2)

        # Рисуем заполненную часть лоад бара
        pygame.draw.rect(screen, (98, 0, 255), (bar_x + 2, bar_y + 2, (bar_width - 4) * (progress / 100), bar_height - 4))

        if progress < 100:
            progress += 0.5
            renderLoadPerc(int(round(progress, 0)))
        else:
            loading = False
        clock.tick(120)
        pygame.display.flip()




if __name__ == '__main__':
    while run:
        if mainMenu.menu.is_enabled():
            mainMenu.menu.mainloop(screen)
            
        elif pauseMenu.menu.is_enabled():
            pauseMenu.menu.mainloop(screen)

        if loading:
            startLoading()
            if not run:
                continue

        keys = pygame.key.get_pressed()
        if keys[pygame.K_z] and 1 in supers and len(supers[1]) == 1:
            properties.fireRate *= 0.5
            supers[1].append(time.time() + 5)
            supers[1][0] = True
            
        elif keys[pygame.K_x] and 2 in supers and len(supers[2]) == 1:
            contusion = True
            supers[2].append(time.time() + 5)
            supers[2][0] = True

        clock.tick(fps)
        y_offset += background_speed
        y_offset = 0 if y_offset >= 750 else y_offset

        # Отрисовка фона
        screen.blit(fone_image, (0, -y_offset))  # Верхняя часть изображения
        screen.blit(fone_image, (0, height - y_offset))  # Нижняя часть изображения

        # Отрисовка звёзд
        screen.blit(star_image, (0, -y_offset))  # Звезды тоже двигаются с фоном
        screen.blit(star_image, (0, height - y_offset))  # Нижняя часть звёзд

        screen.blit(pause_button, (10, 10))

        if 1 in supers:
            screen.blit(super1, (width - 150, 120))
            if supers[1][0]:
                if time.time() >= supers[1][1]:
                    properties.fireRate = Properties().fireRate
                    del supers[1]
                else:
                    renderSuper(1)

        if 2 in supers:
            screen.blit(super2, (width - 90, 120))
            if supers[2][0]:
                if time.time() >= supers[2][1]:
                    contusion = False
                    del supers[2]
                else:
                    renderSuper(2)

        for event in pygame.event.get():
            run = False if event.type == pygame.QUIT else run

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if pause_button.get_rect().collidepoint(event.pos):
                        pauseTime = time.time()
                        pauseMenu.menu.enable()

                    mouse_x, mouse_y = event.pos
                    rX, rY = spaceship.rect.x, spaceship.rect.y
                    dragging = True if rX <= mouse_x <= rX + shipW and rY <= mouse_y <= rY + shipH else dragging
            
            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False if event.button == 1 else dragging  # ЛКМ

            
            # Обработка перемещения мыши
            if event.type == pygame.MOUSEMOTION:
                if dragging:
                    mouseX, mouseY = event.pos
                    if mouseX < shipW // 2:
                        spaceship.rect.x = 0  # Левый край окна
                    elif mouseX > width - shipW // 2:
                        spaceship.rect.x = width - shipW  # Правый край окна
                    else:
                        spaceship.rect.x = mouseX - shipW // 2
                    
                    # Ограничение перемещения по оси Y
                    if mouseY < shipH // 2:
                        spaceship.rect.y = 0  # Верхний край окна
                    elif mouseY > height - shipH // 2:
                        spaceship.rect.y = height - shipH  # Нижний край окна
                    else:
                        spaceship.rect.y = mouseY - shipH // 2

            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                reloading = False

            if event.type == ENEMY_RELOAD:  # При срабатывании таймера в группу спрайтов противников добавляется новый.
                randEnemy = enemies[random.choice(list(enemies.keys()))]
                image, hp = randEnemy['image'], randEnemy['hp']
                enemiesSprites.add(Enemy(random.randint(20, 1000 - 20 - 128), image, hp, random.choice([-properties.enemiesSpeed, properties.enemiesSpeed])))  # Появляется в случайном месте относительно горизонтали.

        if not rel:
            shot(methods.getBulletCount())
            if shots_count >= 60:
                rel = True
                reloadTime = time.time() + properties.reloadTime
                shots_count = 0
        else:
            renderReload()
            if time.time() >= reloadTime:
                rel = False

                
        for element in enemiesSprites:
            if pygame.sprite.spritecollideany(element, spaceShips):
                curHealth -= 10
                enemiesSprites.remove(element)
                if curHealth <= 0:
                    looseGame()

            for element_1 in lasersSprites:  # Проверка каждого лазера и каждого корабля на столкновение друг с другом.
                if pygame.sprite.spritecollideany(element, lasersSprites):
                    element.hp -= methods.getData()["stats"]["Damage"]
                    if element.hp <= 0:
                        enemiesSprites.remove(element)  # Килл врага
                        score += 1
                        money += round(random.randint(1, 5))
                        if score >= properties.needScore:
                            winGame()
                    lasersSprites.remove(element_1)
                    
            if element.rect.bottom - (element.image.get_height() // 2) > height:
                fine = int(round(properties.enemiesHp * 0.1, 0))
                score -= fine if (score - fine) > 0 else score
                enemiesSprites.remove(element)  # При столкновении противника с нижней границей отнимаются очки.

        for element in lasersSprites:  # При столкновении лазера с границей лазер удаляется из группы спрайтов.
            if pygame.sprite.spritecollideany(element, horizontal_border_up):
                lasersSprites.remove(element)

        renderHealth()

        draw()  # В конце цикла отрисовываются все объекты.

    pygame.quit()
