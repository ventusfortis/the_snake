from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центр игрового поля (координата ячейки):
SCREEN_CENTER = (
    (GRID_WIDTH // 2) * GRID_SIZE,
    (GRID_HEIGHT // 2) * GRID_SIZE,
)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Противоположные направления (для запрета разворота на 180°):
OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

# Соответствие клавиш направлениям:
KEY_DIRECTIONS = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT,
}

# Цвет фона — чёрный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки:
BORDER_COLOR = (93, 216, 228)

# Цвет яблока:
APPLE_COLOR = (255, 0, 0)

# Цвет змейки:
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки (итераций в секунду):
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """
    Базовый класс игрового объекта.
    Хранит позицию объекта на поле и его цвет. Дочерние классы
    переопределяют метод ``draw``.
    """

    def __init__(self, body_color=None):
        """Инициализировать объект в центре экрана с заданным цветом"""
        self.position = SCREEN_CENTER
        self.body_color = body_color

    def draw(self):
        """Отрисовать объект, переопределяется в дочерних классах"""

    def draw_cell(self, position, color=None):
        """
        Отрисовать одну ячейку поля по указанным координатам.
        Если цвет не передан, используется ``body_color`` объекта.
        Рамка рисуется только для «живых» ячеек, а не для затирания фона.
        """
        color = color or self.body_color
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        if color != BOARD_BACKGROUND_COLOR:
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Яблоко — квадрат размером в одну ячейку в случайном месте поля"""

    def __init__(self, occupied_positions=None, body_color=APPLE_COLOR):
        """Задать цвет яблока и его случайную начальную позицию"""
        super().__init__(body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """
        Установить яблоку случайную позицию в пределах поля.
        Позиция не должна совпадать ни с одной из ``occupied_positions``
        (например, с сегментами змейки).
        """
        occupied = set(occupied_positions or ())
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in occupied:
                break

    def draw(self):
        """Отрисовать яблоко на игровой поверхности"""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка: список сегментов, движение, отрисовка и сброс"""

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализировать начальное состояние змейки"""
        super().__init__(body_color)
        self.reset()
        self.direction = RIGHT

    def reset(self):
        """Сбросить игру в начальное состояние"""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None
        screen.fill(BOARD_BACKGROUND_COLOR)

    def update_direction(self):
        """Применить направление, выбранное после нажатия клавиши"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Вернуть позицию головы змейки (первый элемент списка."""
        return self.positions[0]

    def move(self):
        """Сдвинуть змейку на одну ячейку в текущем направлении.

        В начало списка добавляется новая голова, а последний сегмент
        удаляется, если длина змейки не увеличилась. Выход за границу
        поля переносит змейку на противоположную сторону.
        """
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовать змейку и затереть след от хвоста"""
        # Отрисовка головы (остальное тело уже нарисовано ранее).
        self.draw_cell(self.get_head_position())

        # Затирание последнего сегмента.
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Обработать нажатия клавиш и закрытие окна.

    Стрелки задают ``next_direction`` змейки, разворот на 180° запрещён.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            new_direction = KEY_DIRECTIONS.get(event.key)
            forbidden = OPPOSITE_DIRECTIONS[game_object.direction]
            if new_direction and new_direction != forbidden:
                game_object.next_direction = new_direction


def main():
    """Запустить игру: создать объекты и выполнять основной цикл"""
    # Инициализация PyGame:
    pygame.init()

    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Змейка съела яблоко: растём и переносим яблоко.
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        # Столкновение с собой: сброс игры.
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
