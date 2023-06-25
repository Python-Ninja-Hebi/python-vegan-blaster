import math
import random

from wonderzero import *

SIZE_WIDTH = 15
SIZE_HEIGHT = 11
TILE_SIZE = 40

WIDTH = SIZE_WIDTH * TILE_SIZE
HEIGHT = SIZE_HEIGHT * TILE_SIZE

GROUND = 0
WALL = 1
BRICK = 2
BOMB = 3
EXPLOSION = 4
DOORC = 5
FIRE = 6
DOORO = 7

IMAGE_PATH = 'assets/images/'
TILE_IMAGES = ['ground.png', 'wall.png', 'brick.png',
               ['tomato_0.png', 'tomato_1.png'],
               {"CENTER": ["explosion_center_0.png", "explosion_center_1.png", "explosion_center_2.png",
                           "explosion_center_3.png", "explosion_center_4.png", "explosion_center_5.png",
                           "explosion_center_6.png"],
                "LEFTRIGHT": ["explosion_left_right_0.png", "explosion_left_right_1.png", "explosion_left_right_2.png",
                              "explosion_left_right_3.png", "explosion_left_right_4.png", "explosion_left_right_5.png",
                              "explosion_left_right_6.png"],
                "UPDOWN": ["explosion_up_down_0.png", "explosion_up_down_1.png", "explosion_up_down_2.png",
                           "explosion_up_down_3.png", "explosion_up_down_4.png", "explosion_up_down_5.png",
                           "explosion_up_down_6.png"],
                "RIGHT": ["explosion_right_0.png", "explosion_right_1.png", "explosion_right_2.png",
                          "explosion_right_3.png", "explosion_right_4.png", "explosion_right_5.png",
                          "explosion_right_6.png"],
                "LEFT": ["explosion_left_0.png", "explosion_left_1.png", "explosion_left_2.png",
                         "explosion_left_3.png", "explosion_left_4.png", "explosion_left_5.png",
                         "explosion_left_6.png"],
                "DOWN": ["explosion_down_0.png", "explosion_down_1.png", "explosion_down_2.png",
                         "explosion_down_3.png", "explosion_down_4.png", "explosion_down_5.png",
                         "explosion_down_6.png"],
                "UP": ["explosion_up_0.png", "explosion_up_1.png", "explosion_up_2.png",
                       "explosion_up_3.png", "explosion_up_4.png", "explosion_up_5.png",
                       "explosion_up_6.png"]
                },
               "door_closed.png",
               "fire.png",
               "door_open.png"]

DEFAULT_TIME = 0.4
BOMB_TIME = 2.4
NUMBER_OF_BRICK = 20
NUMBER_OF_OPPONENTS = 4

ITEMS: dict[int, Vector2] = {FIRE: None,
                             DOORC: None}

PIXELS_PER_SECOND = 56
PLAYER_WIDTH = 25
PLAYER_HEIGHT = 35


class Image:
    def __init__(self, image, start_slot="DEFAULT", time=None):
        self._default_time: float = time
        self._images = {}
        self._slot: str = start_slot
        self._next = 0
        if isinstance(image, str):
            self._images[self._slot] = [pygame.image.load(f"{IMAGE_PATH}{image}")]
        elif isinstance(image, list):
            l1 = []
            for i in image:
                l1.append(pygame.image.load(f"{IMAGE_PATH}{i}"))
            self._images[self._slot] = l1
            self._default_time = DEFAULT_TIME
        elif isinstance(image, dict):
            for key, items in image.items():
                l2 = []
                for i in items:
                    l2.append(pygame.image.load(f"{IMAGE_PATH}{i}"))
                self._images[key] = l2

        self._animation_time: float = self._default_time

    def get(self) -> Surface:
        return self._images[self._slot][self._next]

    def update(self, delta_time: float, slot: str = None):
        if slot:
            if slot != self._slot:
                self._slot = slot
                self._animation_time = self._default_time
                self._next = 0
        if self._animation_time:
            self._animation_time -= delta_time
            if self._animation_time < 0:
                self._animation_time = self._default_time
                self._next += 1
                if self._next >= len(self._images[self._slot]):
                    self._next = 0


class Tile:
    def __init__(self, tile_type: int):
        self.set(tile_type)

    def set(self, tile_type: int, slot=None, time=None) -> None:
        self.tile_type: int = tile_type
        self.timer: float = 0
        if self.tile_type == BOMB:
            self.timer = BOMB_TIME
        self.image: Image = Image(TILE_IMAGES[self.tile_type], slot, time)


def on_ground(who, pos: Vector2) -> (bool, int, Vector2):
    ground = [GROUND]
    if not isinstance(who, Opponent):
        ground.append(BOMB)

    map = pixel_to_map(pos)
    tile = tilemap.tiles[int(map.x)][int(map.y)]
    if tile.tile_type not in ground:
        return False, tile.tile_type, map

    map = pixel_to_map(Vector2(pos.x + PLAYER_WIDTH - 1, pos.y))
    tile = tilemap.tiles[int(map.x)][int(map.y)]
    if tile.tile_type not in ground:
        return False, tile.tile_type, map

    map = pixel_to_map(Vector2(pos.x + PLAYER_WIDTH - 1, pos.y + PLAYER_HEIGHT - 1))
    tile = tilemap.tiles[int(map.x)][int(map.y)]
    if tile.tile_type not in ground:
        return False, tile.tile_type, map

    map = pixel_to_map(Vector2(pos.x, pos.y + PLAYER_HEIGHT - 1))
    tile = tilemap.tiles[int(map.x)][int(map.y)]
    if tile.tile_type not in ground:
        return False, tile.tile_type, map

    return True, None, None


opponents = []

OPPONENT_PIXELS_PER_SECOND = 56
OPPONENT_TIME_TO_CHANGE_DIRECTION = 2.0


class Opponent(GameInterface):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

    def __init__(self, pos: Vector2):
        self.active: bool = True
        self.directions = [self.RIGHT, self.LEFT, self.UP, self.DOWN]
        self.direction = self.RIGHT
        self.direction_time = OPPONENT_TIME_TO_CHANGE_DIRECTION
        self.image: Image = Image("burger.png")
        self.pos: Vector2 = map_to_pixel(pos)
        self.pos.x = self.pos.x + (TILE_SIZE - PLAYER_WIDTH) / 2

    def update(self, delta_time: float):
        if self.active:
            self.move(delta_time)

    def move(self, delta_time):

        self.direction_time -= delta_time
        if self.direction_time <= 0:
            self.direction_time = OPPONENT_TIME_TO_CHANGE_DIRECTION
            self.direction = random.randint(1, len(self.directions))

        new_pos = self.pos.copy()

        if self.direction == self.RIGHT:
            new_pos.x += PIXELS_PER_SECOND * delta_time
        elif self.direction == self.LEFT:
            new_pos.x -= PIXELS_PER_SECOND * delta_time
        elif self.direction == self.UP:
            new_pos.y -= PIXELS_PER_SECOND * delta_time
        elif self.direction == self.DOWN:
            new_pos.y += PIXELS_PER_SECOND * delta_time

        is_on_ground, item, item_pos = on_ground(self, new_pos)
        if is_on_ground:
            self.pos = new_pos
        else:
            if item == EXPLOSION:
                self.active = False
                gui.points += 100
                gui.opponents_minus(1)
            else:
                self.direction += 1
                if self.direction >= len(self.directions):
                    self.direction = 1

    def draw(self, screen: Surface):
        if self.active:
            screen.blit(self.image.get(), self.pos)

    def rect(self) -> pygame.rect:
        return pygame.Rect(self.pos.x, self.pos.y, PLAYER_WIDTH, PLAYER_HEIGHT)


class Tilemap(GameInterface):
    def __init__(self, opponents):
        self.tiles = [[Tile(WALL) if x == 0 or y == 0 or x == SIZE_WIDTH - 1 or y == SIZE_HEIGHT - 1
                       else Tile(WALL) if x % 2 == 0 and y % 2 == 0
        else Tile(GROUND) for y in range(SIZE_HEIGHT)] for x in range(SIZE_WIDTH)]
        items = list(ITEMS.keys())
        for i in range(NUMBER_OF_BRICK):
            while True:
                pos = Vector2(random.randint(2, SIZE_WIDTH - 1), random.randint(2, SIZE_HEIGHT - 1))
                tile = self.tiles[int(pos.x)][int(pos.y)]
                if tile.tile_type == GROUND:
                    tile.set(BRICK)
                    if len(items) > 0:
                        item = items.pop(0)
                        ITEMS[item] = Vector2(int(pos.x), int(pos.y))
                    break
        for i in range(NUMBER_OF_OPPONENTS):
            while True:
                pos = Vector2(random.randint(2, SIZE_WIDTH - 1), random.randint(2, SIZE_HEIGHT - 1))
                tile = self.tiles[int(pos.x)][int(pos.y)]
                if tile.tile_type == GROUND:
                    opponents.append(Opponent(pos))
                    break

    def update(self, delta_time: float):
        for i in range(SIZE_WIDTH):
            for j in range(SIZE_HEIGHT):
                tile = self.tiles[i][j]
                if tile.tile_type == BOMB:
                    tile.timer -= delta_time
                    if tile.timer <= 0:
                        timer = DEFAULT_TIME * 7
                        tile.set(EXPLOSION, "CENTER", DEFAULT_TIME)
                        tile.timer = timer

                        explosion_direction = [Vector2(1, 0), Vector2(-1, 0), Vector2(0, -1), Vector2(0, 1)]
                        explosion_image_slot = ["LEFTRIGHT", "LEFTRIGHT", "UPDOWN", "UPDOWN"]
                        explosion_image_end_slot = ["RIGHT", "LEFT", "UP", "DOWN"]

                        for k, direction in enumerate(explosion_direction):

                            pos = Vector2(i, j)
                            real_length = 0

                            for l in range(player.explosion_length):
                                pos = pos + direction
                                next_tile = self.tiles[int(pos.x)][int(pos.y)]
                                if next_tile.tile_type == GROUND:
                                    real_length += 1
                                elif next_tile.tile_type == BRICK:
                                    found = False
                                    for key, value in ITEMS.items():
                                        if value:
                                            if value.x == int(pos.x) and value.y == int(pos.y):
                                                found = True
                                                if key == DOORC and gui.opponents == 0:
                                                    next_tile.set(DOORO)
                                                next_tile.set(key)
                                    if not found:
                                        real_length += 1
                                        next_tile.set(GROUND)
                                    break
                                else:
                                    break

                            pos = Vector2(i, j)

                            for l in range(real_length):
                                pos = pos + direction
                                next_tile = self.tiles[int(pos.x)][int(pos.y)]
                                slot = explosion_image_end_slot[k] if l == real_length - 1 else explosion_image_slot[k]
                                next_tile.set(EXPLOSION, slot, DEFAULT_TIME)
                                next_tile.timer = timer

                    else:
                        tile.image.update(delta_time)
                elif tile.tile_type == EXPLOSION:
                    tile.timer -= delta_time
                    if tile.timer <= 0:
                        tile.set(GROUND)
                    else:
                        tile.image.update(delta_time)

    def draw(self, screen: Surface):
        for i in range(SIZE_WIDTH):
            for j in range(SIZE_HEIGHT):
                screen.blit(self.tiles[i][j].image.get(), (i * TILE_SIZE, j * TILE_SIZE))


def map_to_pixel(map: Vector2) -> Vector2:
    return Vector2(map.x * TILE_SIZE, map.y * TILE_SIZE)


def pixel_to_map(pixel: Vector2) -> Vector2:
    return Vector2(math.floor(pixel.x / TILE_SIZE), math.floor(pixel.y / TILE_SIZE))


tilemap = Tilemap(opponents)

class Message(GameInterface):
    def __init__(self):
        self.text:str = ''
        self.show:bool = False
    def draw(self, screen:Surface):
        if self.show:
            draw_text(screen,self.text,40,WHITE,Vector2(WIDTH/2,HEIGHT/2),TEXT_ALIGNMENT_MID)

class Player(GameInterface):
    def __init__(self):
        self.image: Image = Image({"FRONT": ["player_front.png"],
                                   "LEFT": ["player_left_0.png", "player_left_1.png"],
                                   "RIGHT": ["player_right_0.png", "player_right_1.png"],
                                   "UP": ["player_up_0.png", "player_up_1.png"],
                                   "DOWN": ["player_down_0.png", "player_down_1.png"]
                                   },
                                  "FRONT", 0.2)
        self.image_slot = "FRONT"
        self.explosion_length = 1
        self.pos: Vector2 = map_to_pixel(Vector2(1, 1))
        self.pos.x = self.pos.x + (TILE_SIZE - PLAYER_WIDTH) / 2

    def update(self, delta_time: float):
        keys = pygame.key.get_pressed()
        self.image_slot = "FRONT"

        if keys[pygame.K_SPACE]:
            map = pixel_to_map(Vector2(self.pos.x + TILE_SIZE / 2, self.pos.y + TILE_SIZE / 2))
            tilemap.tiles[int(map.x)][int(map.y)].set(BOMB)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_LEFT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            self.move(keys, delta_time)

        self.image.update(delta_time, self.image_slot)

    def move(self, keys, delta_time):

        new_pos = self.pos.copy()

        if keys[pygame.K_RIGHT]:
            new_pos.x += PIXELS_PER_SECOND * delta_time
            self.image_slot = "RIGHT"
        elif keys[pygame.K_LEFT]:
            new_pos.x -= PIXELS_PER_SECOND * delta_time
            self.image_slot = "LEFT"
        elif keys[pygame.K_UP]:
            new_pos.y -= PIXELS_PER_SECOND * delta_time
            self.image_slot = "UP"
        if keys[pygame.K_DOWN]:
            new_pos.y += PIXELS_PER_SECOND * delta_time
            self.image_slot = "DOWN"

        is_on_ground, item, item_pos = on_ground(self, new_pos)
        if is_on_ground:
            self.pos = new_pos
            if self.collides():
                gui.health -= 10 * delta_time
        else:
            if item == FIRE:
                self.explosion_length += 1
                tilemap.tiles[int(item_pos.x)][int(item_pos.y)].set(GROUND)
            elif item == EXPLOSION:
                gui.health -= 2 * delta_time
            elif item == DOORO:
                message.text = "You win. Next Level"
                message.show = True

    def rect(self) -> pygame.rect:
        return pygame.Rect(self.pos.x, self.pos.y, PLAYER_WIDTH, PLAYER_HEIGHT)

    def collides(self) -> bool:
        for i in opponents:
            if self.rect().colliderect(i.rect()):
                return True
        return False

    def draw(self, screen: Surface):
        screen.blit(self.image.get(), self.pos)


player = Player()


class Gui(GameInterface):
    def __init__(self):
        self.time: float = 200
        self.points: int = 0
        self.health: float = 100
        self.opponents: int = NUMBER_OF_OPPONENTS

    def opponents_minus(self, value: float) -> None:
        self.opponents -= 1
        if self.opponents == 0:
            pos = ITEMS[DOORC]
            tile = tilemap.tiles[int(pos.x)][int(pos.y)]
            if tile.tile_type == DOORC:
               tile.set(DOORO)

    def update(self, delta_time: float):
        if self.time <= 0:
            self.time = 0
        else:
            self.time -= delta_time

    def draw(self, screen: Surface):
        draw_text(screen, f'TIME {self.time:.0f}', 36, WHITE, Vector2(24, 10))
        draw_text(screen, f'{self.points}', 36, WHITE, Vector2(300, 10))
        draw_text(screen, f'HEALTH {self.health:.0f}', 36, WHITE, Vector2(420, 10))

message = Message()

gui = Gui()


def draw(screen: Surface):
    tilemap.draw(screen)
    player.draw(screen)
    gui.draw(screen)
    for i in opponents:
        i.draw(screen)
    message.draw(screen)


def update(delta_time: float):
    if not message.show:
        tilemap.update(delta_time)
        player.update(delta_time)
        gui.update(delta_time)
        for i in opponents:
            i.update(delta_time)

# run on desktop
#if __name__ == "__main__":
#    game = Game(width=WIDTH, height=HEIGHT, name='Vegan Blaster')
#    game.background_color = GRAY
#    game.run()
#    game.quit()

# run in web
async def main():
    game = Game(width=WIDTH, height=HEIGHT, name='Vegan Blaster')
    game.background_color = GRAY
    await game.run_async()
    game.quit()

asyncio.run(main())