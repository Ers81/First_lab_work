import sys # нужен для sys.exit при ошибках и при завершении
import os # нужен для проверки существования файла по пути
import pygame # графическая библиотека для отрисовки и обработки событий

CELL_SIZE = 64 # настраиваемый размер клетки
MAP_FILE = r"C:\Users\ivand\OneDrive\Рабочий стол\LabPython\map.txt"

# Папка скрипта и пути к изображениям (файлы рядом со скриптом)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYER_IMG_PATH = os.path.join(SCRIPT_DIR, "Player.jpeg")
WALL_IMG_PATH = os.path.join(SCRIPT_DIR, "Wall.jpeg")
FIELD_IMG_PATH = os.path.join(SCRIPT_DIR, "Field.jpeg")
EXIT_IMG_PATH = os.path.join(SCRIPT_DIR, "Exit.jpeg")
COLLECT_IMG_PATH = os.path.join(SCRIPT_DIR, "Collect.jpeg")

# ----- Работа с картой
# Читает карту из файла и возвращает сетку, состоящую из символов.
def load_map(file_path):
    if not os.path.exists(file_path): # проверяет, что файл существует
        raise FileNotFoundError("Файл карты не найден: " + file_path)
    with open(file_path, "r", encoding="utf-8") as f:
    # открывает файл на чтение, читает в строку и закрывает
        text = f.read()
    lines = text.strip().splitlines()
    # убирает пустые края и разбивает на строки
    if not lines: # если после очистки строк нет, то выдаёт ошибку
        raise ValueError("Файл карты пустой")
    grid = [] # сюда сложим строки как списки символов в виде сетки
    i = 0
    while i < len(lines):
        line = lines[i] # берёт все строки текста по одной
        row = list(line.rstrip("\n")) # превращает строку в список символов
        grid.append(row) # добавляет строку в сетку
        i += 1
    validate_map(grid)
    # запуск функции для проверки корректности карты (следующая функция)
    return grid

# Проверка карты (форма, использующиеся символы и их количество)
def validate_map(grid):
    expected_row = len(grid[0]) # ширина карты по первой строке
    row = 0
    while row < len(grid):
    # проверка формы карты (длинны строк должны быть одинаковыми)
        if len(grid[row]) != expected_row:
            raise ValueError("Карта должна быть прямоугольной")
        row += 1
    flat = [] # список всех символов каждой строки для удобства проверки
    row = 0
    while row < len(grid): # проходит по всем строкам
        col = 0
        while col < len(grid[row]): # проходит по всем символам в строке
            flat.append(grid[row][col]) # добавляет символ в общий список
            col += 1
        row += 1
    if flat.count("P") != 1: # проверяет, что ровно один игрок
        raise ValueError("На карте должен быть один игрок 'P'")
    if flat.count("C") < 1: # проверяет наличие хотя бы одного предмета
        raise ValueError("На карте должен быть хотя бы один 'C'")
    if flat.count("E") < 1: # проверяет наличие хотя бы одного выхода
        raise ValueError("На карте должен быть хотя бы один 'E'")
    allowed = {"0", "1", "C", "E", "P"} # разрешённые символы карты
    uniques = list(set(flat)) # список всех символов (по одному разу каждый)
    i = 0
    while i < len(uniques): # проходит по всем символам на карте
        ch = uniques[i]
        if ch not in allowed: # если встречает неизвестный символ
            raise ValueError("Неизвестные символы на карте: " + str(ch))
        i += 1

# находит и возвращает координаты игрока как (row, col).
def find_player_pos(grid):
    row = 0
    while row < len(grid): # проходит по всем строкам
        col = 0
        while col < len(grid[row]): # проходит по всем символам
            if grid[row][col] == "P": # если нашёл символ "P"
                return row, col # возвращает координаты
            col += 1
        row += 1

# ----- класс игры. хранит состояние игры: 
# карта, позиция игрока, счётчики и т.д.
class SimpleGame:

# вызывается афтоматически при создании нового объекта. self - ссылка на текущий объект класса.
    def __init__(self, grid):
        self.grid = grid # сохраняет карту как свойство объекта
        self.rows = len(grid) # сохраняет число строк на карте
        self.cols = len(grid[0]) # сохраняет число столбцов на карте
        self.player_row, self.player_col = find_player_pos(grid)
        # сохраняет начальную позицию игрока
        # делаем карту «статичной» — игрок рисуется отдельно
        self.grid[self.player_row][self.player_col] = "0"
        # заменяет P на 0 в сетке
        self.moves = 0 # сохраняет и обнуляет счётчик ходов
        self.collected = 0
        # сохраняет и обнуляет количество собранных коллекционных предметов
        total = 0
        row = 0
        while row < len(grid): # проходит по всем строкам
            col = 0
            while col < len(grid[row]): # проходит по всем символам
                if grid[row][col] == "C":
                # считает количество коллекционных предметов
                    total += 1
                col += 1
            row += 1
        self.total_collectibles = total
        # сохраняет общее количество предметов

# Возвращает True, если можно переместиться на клетку
    def can_move(self, row, col):
        if row < 0 or row >= self.rows:
            return False
        if col < 0 or col >= self.cols:
            return False
        if self.grid[row][col] == "1":
            return False
        return True

# выполнение движения: обновление позиции, сбор предметов, проверка выхода
    def do_move(self, drow, dcol):
        new_row = self.player_row + drow # новая строка после движения
        new_col = self.player_col + dcol # новый столбец после движения
        if not self.can_move(new_row, new_col):
            return
        # если двигаться нельзя - выходит из функции, ничего не меняя
        self.player_row = new_row # сохраняет новую строку игрока
        self.player_col = new_col # сохраняет новый столбец игрока
        self.moves += 1 # увеличивает счётчик ходов на единицу
        if self.grid[new_row][new_col] == "C":
            self.collected += 1
            self.grid[new_row][new_col] = "0"
        # если на клетке был предмет, "собирает" и удаляет его с карты
        if self.grid[new_row][new_col] == "E": # если игрок встал на выход
            if self.collected >= self.total_collectibles:
                print("Вы собрали все предметы и дошли до выхода!")
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            # если все предметы собраны - закрывает игру

# вычисляет ширину и высоту окна игры в пикселях
    def get_size_pixels(self):
        width = self.cols * CELL_SIZE
        height = self.rows * CELL_SIZE
        return width, height

# ----- Рендер и главный цикл
# Отрисовывает все элементы в окне
def draw_everything(surface, game, images):
    field_img, wall_img, collect_img, exit_img, player_img = images
    surface.fill((0, 0, 0)) # заливает фон чёрным
    row = 0
    while row < game.rows: # проходит по строкам карты
        col = 0
        while col < game.cols: # проходит по столбцам карты
            ch = game.grid[row][col] # получает символ клетки
            x = col * CELL_SIZE # вычисляет координату x для рисования
            y = row * CELL_SIZE # вычисляет координату y для рисования
            surface.blit(field_img, (x, y))
            # рисует пустое поле в позицию (x, y)
            if ch == "1":
                surface.blit(wall_img, (x, y)) # рисует стену
            elif ch == "C":
                surface.blit(collect_img, (x, y)) # рисует предмет
            elif ch == "E":
                surface.blit(exit_img, (x, y)) # рисует выход
            col += 1
        row += 1
    px = game.player_col * CELL_SIZE
    py = game.player_row * CELL_SIZE
    surface.blit(player_img, (px, py))
    # вычисляет позицию игрока и рисует его

# загрузка карты и главный цикл
def run_game(map_file_path):
    pygame.init()
    # Проверка картинок до загрузки
    for path in (
        PLAYER_IMG_PATH,
        WALL_IMG_PATH,
        FIELD_IMG_PATH,
        EXIT_IMG_PATH,
        COLLECT_IMG_PATH,
    ):
        if not os.path.exists(path):
            pygame.quit()
            raise FileNotFoundError("Отсутствует файл изображения: " + path)
    # Загружаем и масштабируем изображения после pygame.init()
    player_img = pygame.image.load(PLAYER_IMG_PATH)
    player_img = pygame.transform.scale(player_img, (CELL_SIZE, CELL_SIZE))
    wall_img = pygame.image.load(WALL_IMG_PATH)
    wall_img = pygame.transform.scale(wall_img, (CELL_SIZE, CELL_SIZE))
    field_img = pygame.image.load(FIELD_IMG_PATH)
    field_img = pygame.transform.scale(field_img, (CELL_SIZE, CELL_SIZE))
    exit_img = pygame.image.load(EXIT_IMG_PATH)
    exit_img = pygame.transform.scale(exit_img, (CELL_SIZE, CELL_SIZE))
    collect_img = pygame.image.load(COLLECT_IMG_PATH)
    collect_img = pygame.transform.scale(collect_img, (CELL_SIZE, CELL_SIZE))
    images = (field_img, wall_img, collect_img, exit_img, player_img)
    try:
        grid = load_map(map_file_path) # пробует загрузить карту
    except Exception as exc:
        print("Ошибка при загрузке карты:", exc)
        pygame.quit()
        sys.exit(1)
    # если что-то пошло не так, закрывает pygame и программу
    game = SimpleGame(grid) # создаёт объекты игры на основе карты
    width, height = game.get_size_pixels() # получает размеры окна
    screen = pygame.display.set_mode((width, height))
    # создаёт окно нужного размера
    pygame.display.set_caption("Ходов: 0") # задаёт заголовок окна
    clock = pygame.time.Clock() # объект для контроля кадров в секунду
    running = True
    while running: # главный цикл игры
        events = pygame.event.get()
        i = 0
        while i < len(events): # перебирает все события pygame
            event = events[i]
            if event.type == pygame.QUIT:
                running = False
                break
            # выход из программы, если нажали крестик вверху окна
            if event.type == pygame.KEYDOWN: # если была нажата клавиша
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                # если это был ESC, то завершает цикл и выходит из программы
                if event.key == pygame.K_w: # движение вверх ("W")
                    game.do_move(-1, 0)
                    print("Вы совершили ходов:", game.moves)
                    # записыввает количество сделланых ходов в консоль
                    pygame.display.set_caption("Вы совершили ходов:" + str(game.moves))
                    # записыввает количество сделланых ходов в заголовок
                elif event.key == pygame.K_s: # движение вниз ("S")
                    game.do_move(1, 0)
                    print("Вы совершили ходов:", game.moves)
                    pygame.display.set_caption("Вы совершили ходов:" + str(game.moves))
                elif event.key == pygame.K_a: # движение влево ("A")
                    game.do_move(0, -1)
                    print("Вы совершили ходов:", game.moves)
                    pygame.display.set_caption("Вы совершили ходов:" + str(game.moves))
                elif event.key == pygame.K_d: # движение вправо ("D")
                    game.do_move(0, 1)
                    print("Вы совершили ходов:", game.moves)
                    pygame.display.set_caption("Вы совершили ходов:" + str(game.moves))
            i += 1
        draw_everything(screen, game, images) # перерисовывает всё на экране
        pygame.display.flip() # обновляет и показывает содержимое экрана
        clock.tick(60) # ограничивает цикл до 60 кадров в секунду
    pygame.quit() # завершает работу pygame

# ----- Запуск
if __name__ == "__main__": # если запущено как скрипт
    run_game(MAP_FILE) # запускает игру с прямым путём к map.txt