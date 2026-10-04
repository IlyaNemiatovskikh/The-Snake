"""Игра Змейка на Pygame."""

import sys
from random import choice

import pygame as pg

# Задаем параметры для размеров поля и сетки:
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
START_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Вводим цвета игрового поля и объектов на нём:
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BOARD_BACKGROUND_COLOR = BLACK
BORDER_COLOR = BLACK
APPLE_COLOR = RED
SNAKE_COLOR = GREEN

# Определяем скорость змейки в клетках в секунду:
SPEED = 20

# Перечисляем направления движения: смещение (X, Y) в клетках:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Задаем противоположные направления для запрета разворота на 180 градусов:
REVERSE_DIRECTIONS = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
DIRECTION_BY_KEY = {
    pg.K_UP: UP,
    pg.K_DOWN: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_RIGHT: RIGHT,
}

# Инициализация всех модулей Pygame:
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый класс игровых объектов с позицией и цветом."""

    def __init__(self, position=START_POSITION, body_color=None):
        """Создаёт объект с заданными положением и цветом."""
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position, color, border_color=BORDER_COLOR):
        """Заливает клетку и при необходимости рисует рамку."""
        rectangle = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rectangle)
        if border_color is not None:
            pg.draw.rect(screen, border_color, rectangle, 1)

    def draw(self):
        """Заготовка отрисовки для переопределения в подклассах."""


class Apple(GameObject):
    """Яблоко, с случайным появлением в свободной клетке поля."""

    def __init__(self, body_color=APPLE_COLOR, occupied_positions=()):
        """Создаёт яблоко с заданным цветом в случайной свободной клетке."""
        super().__init__(body_color=body_color)
        if not self.randomize_position(occupied_positions):
            raise ValueError('Для яблока нет свободной клетки.')

    def randomize_position(self, occupied_positions=()):
        """Перемещает яблоко в случайную свободную клетку игрового поля."""
        occupied = set(occupied_positions)
        free_positions = [
            (column * GRID_SIZE, row * GRID_SIZE)
            for row in range(GRID_HEIGHT)
            for column in range(GRID_WIDTH)
            if (column * GRID_SIZE, row * GRID_SIZE) not in occupied
        ]
        if not free_positions:
            return False
        self.position = choice(free_positions)
        return True

    def draw(self):
        """Рисует яблоко и рамку вокруг его клетки."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Змейка и её состояние во время движения по полю."""

    def __init__(self, body_color=SNAKE_COLOR, position=START_POSITION):
        """Создаёт змейку из одной клетки, движущуюся вправо."""
        super().__init__(position=position, body_color=body_color)
        self.reset()
        self.direction = RIGHT

    def update_direction(self):
        """Применяет сохранённое направление, если оно задано."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Сдвигает голову на одну клетку с переходом через края поля."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        # Остаток от деления переносит голову через край поля.
        new_head = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        self.last = (
            self.positions.pop() if len(self.positions) > self.length else None
        )

    def draw(self):
        """Стирает хвост и рисует голову, сохраняя остальные сегменты."""
        # Голова остаётся видимой, когда занимает клетку ушедшего хвоста.
        if self.last is not None:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, None)
        self.draw_cell(self.get_head_position(), self.body_color)

    def get_head_position(self):
        """Возвращает координаты клетки головы змейки в пикселях."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку до одной клетки в начальной позиции."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None


def handle_keys(snake):
    """Обрабатывает выход из игры и сохраняет новое направление змейки."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        if event.type != pg.KEYDOWN:
            continue
        if event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()

        new_direction = DIRECTION_BY_KEY.get(event.key)
        if (
            new_direction is not None
            and new_direction != REVERSE_DIRECTIONS[snake.direction]
        ):
            # Все нажатия за кадр сравниваются с текущим направлением.
            snake.next_direction = new_direction


def main():
    """Запускает игровой цикл и обновляет состояние объектов."""
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)
    snake.draw()
    apple.draw()
    pg.display.update()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        # После еды хвост сохранится при следующем вызове move().
        if snake.get_head_position() == apple.position:
            snake.length += 1
            if not apple.randomize_position(
                occupied_positions=snake.positions
            ):
                # Если свободных клеток нет, начинаем игру заново.
                snake.reset()
                apple.randomize_position(occupied_positions=snake.positions)
                screen.fill(BOARD_BACKGROUND_COLOR)

        # Проверяем голову после удаления освобождённого хвоста.
        elif snake.get_head_position() in snake.positions[4:]:
            snake.reset()
            if apple.position in snake.positions:
                apple.randomize_position(occupied_positions=snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
