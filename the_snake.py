"""Игра «Змейка» на Pygame."""

from random import choice, randint

import pygame

# Задаем параметры для размеров поля и сетки:
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Вводим цвета игрового поля и объектов на нём:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (0, 0, 0)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Определяем скорость змейки в клектах в секунду:
SPEED = 20

# Перечисляем направления движения - смещение (X, Y) в клетках:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Инициализация всех модулей Pygame:
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# Заголовок окна игрового поля:
pygame.display.set_caption("Змейка")
clock = pygame.time.Clock()


class GameObject:
    """Общий набор атрибутов для объектов на игровом поле."""

    def __init__(self):
        """Задаёт объекту начальную позицию и цвет."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = None

    def draw(self):
        """Оставляет заготовку отрисовки для дочерних классов."""


class Apple(GameObject):
    """Яблоко, которое появляется в случайной клетке поля."""

    def __init__(self):
        """Создаёт яблоко и выбирает его начальную позицию."""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def randomize_position(self):
        """Перемещает яблоко в случайную клетку игрового поля."""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )

    def draw(self):
        """Рисует яблоко и рамку вокруг его клетки."""
        rectangle = (self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rectangle)
        pygame.draw.rect(screen, BORDER_COLOR, rectangle, 1)


class Snake(GameObject):
    """Змейка и её состояние во время движения по полю."""

    def __init__(self):
        """Создаёт короткую змейку, движущуюся вправо."""
        super().__init__()
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None

    def update_direction(self):
        """Применяет сохранённое направление, если оно задано."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает голову и обновляет хвост змейки."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        # Остаток от деления переносит голову через край поля.
        new_head = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Рисует сегменты змейки и стирает ушедший хвост."""
        # Стираем хвост до отрисовки, чтобы голова не заняла клетку.
        if self.last is not None:
            rectangle = (self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rectangle)

        for position in self.positions:
            rectangle = (position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rectangle)
            pygame.draw.rect(screen, BORDER_COLOR, rectangle, 1)

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Возвращает змейку к одной клетке в центре поля."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None


def handle_keys(snake):
    """Обрабатывает закрытие окна и смену направления змейки."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type != pygame.KEYDOWN:
            continue

        # Запрещаем разворот за кадр при серии нажатий.
        reverse_directions = {
            UP: DOWN,
            DOWN: UP,
            LEFT: RIGHT,
            RIGHT: LEFT,
        }
        direction_by_key = {
            pygame.K_UP: UP,
            pygame.K_DOWN: DOWN,
            pygame.K_LEFT: LEFT,
            pygame.K_RIGHT: RIGHT,
        }
        new_direction = direction_by_key.get(event.key)
        if (
            new_direction is not None
            and new_direction != reverse_directions[snake.direction]
        ):
            snake.next_direction = new_direction


def main():
    """Запускает игровой цикл и обновляет состояние объектов."""
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Сохраняем прибавленную длину при следующем ходе.
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()

        # Проверяем голову после удаления освобождённого хвоста.
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        # Очищаем следы прошлого кадра перед новой отрисовкой.
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == "__main__":
    main()
