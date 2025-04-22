from enum import Enum


class Direction(Enum):
    UP = 1
    STAY = 0
    DOWN = -1

    @staticmethod
    def opposite(dir):
        if dir == Direction.UP:
            return Direction.DOWN
        if dir == Direction.DOWN:
            return Direction.UP
