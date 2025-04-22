from direction import Direction

class Elevator:
    def __init__(self, id):
        self.id = id
        self.current_floor = 0
        self.up_destinations = set()
        self.down_destinations = set()
        self.direction = Direction.STAY
        self.open_doors = False
        self.is_emergency = False

    def __str__(self):
        return f'| id: {self.id}, floor: {self.current_floor}, dest: {self.destinations()}, dir: {self.direction.name}' + (', DOOR OPEN |' if self.open_doors else ' |')

    def move(self):
        if self.is_emergency:
            self.open_doors = True
            return
        self.open_doors = False
        self.current_floor += self.direction.value
        self.check_open_doors()
        self.update_direction()

    def check_open_doors(self):
        if not self.direction is Direction.UP and self.current_floor in self.down_destinations:
            self.down_destinations.remove(self.current_floor)
            self.open_doors = True
        if not self.direction is Direction.DOWN and self.current_floor in self.up_destinations:
            self.up_destinations.remove(self.current_floor)
            self.open_doors = True

    def update_direction(self):
        destinations = self.destinations()
        if destinations:
            if self.direction is Direction.UP and max(destinations) == self.current_floor:
                self.direction = Direction.STAY
                self.check_open_doors()
            elif self.direction is Direction.DOWN and min(destinations) == self.current_floor:
                self.direction = Direction.STAY
                self.check_open_doors()
            elif self.direction is Direction.DOWN:
                if min(destinations) >= self.current_floor:
                    self.direction = Direction.UP
            elif self.direction is Direction.UP:
                if max(destinations) <= self.current_floor:
                    self.direction = Direction.DOWN
            else:
                if max(destinations) > self.current_floor:
                    self.direction = Direction.UP
                else:
                    self.direction = Direction.DOWN
        else:
            self.direction = Direction.STAY

    def destinations(self):
        return self.up_destinations | self.down_destinations

    def get_status(self):
        return self.id, self.current_floor, self.destinations()

    def get_destination_count(self):
        return len(self.destinations())

    def add_destination(self, destination, direction):
        if self.is_emergency:
            return
        if direction is Direction.UP:
            self.up_destinations.add(destination)
        elif direction is Direction.DOWN:
            self.down_destinations.add(destination)
        self.update_direction()
