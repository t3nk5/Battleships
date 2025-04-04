import re
from typing import Literal, cast

from utils.prompt import Prompt

directions = Literal['horizontal', 'h', 'vertical', 'v']


def select_direction() -> directions:
    return cast(directions,
                Prompt.select('Which way do you want to position your ship?',
                              ['horizontal', 'vertical'],
                              lambda x: x).element.lower())


class Coordinate:
    Values: list

    def __init__(self, value):
        if not self.valid(value):
            raise ValueError(f"Invalid value for this coordinate: {value}. expected: {self.Values}")
        self.value = value

    def __add__(self, added: int):
        return self.Values[self.Values.index(self.value) + added]

    def __str__(self):
        return str(self.value)

    def valid(self, value) -> bool:
        return value in self.Values


class Coordinates:
    class Vertical(Coordinate):
        Values = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        Type = Literal['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

        def __init__(self, value: Type):
            super().__init__(value)

    class Horizontal(Coordinate):
        Values = [i + 1 for i in range(10)]
        Type = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        def __init__(self, value: Type):
            super().__init__(value)

    def __init__(self,
                 x: 'Coordinates.Vertical.Type',
                 y: 'Coordinates.Horizontal.Type'):
        self.x: Coordinates.Vertical = Coordinates.Vertical(x)
        self.y: Coordinates.Horizontal = Coordinates.Horizontal(y)

    def __getitem__(self, direction: directions) -> Coordinate:
        if direction == 'vertical' or direction == 'v':
            return self.y
        elif direction == 'horizontal' or direction == 'h':
            return self.x
        else:
            raise ValueError(f"Invalid direction: {direction}")

    def __str__(self):
        return f'{self.x} {self.y}'

    @staticmethod
    def select() -> 'Coordinates':
        def parse_input(user_input: str):
            match = re.fullmatch(r"\s*([A-Za-z]?)\s*(-?\d+|\d+)?\s*", user_input)
            if match:
                x = (match.group(1) if match.group(1) in Coordinates.Vertical.Values else None) or None
                y = match.group(2)
                if y:
                    if re.fullmatch(r"-?\d+", y):
                        y = abs(int(y)) if abs(int(y)) in Coordinates.Horizontal.Values else None
                    else:
                        return x, None
                return x, y
            return None, None

        coordinates = parse_input(Prompt.get('Select coordinates:', expected_type=str, formated=lambda x: x.upper()))

        return Coordinates(
            x=coordinates[0] or Prompt.get(
                f'Incorrect X value, select correct X coordinate (between {Coordinates.Vertical.Values[0]} and {Coordinates.Vertical.Values[-1]}):',
                expected_type=str,
                excluded_condition=lambda x: x.upper() not in Coordinates.Vertical.Values,
                formated=lambda x: x.upper()
            ),
            y=coordinates[1] or Prompt.get(
                f'Incorrect Y value, select correct Y coordinate (between {Coordinates.Horizontal.Values[0]} and {Coordinates.Horizontal.Values[-1]}):',
                expected_type=int,
                excluded_condition=lambda x: x not in Coordinates.Horizontal.Values
            ),
        )
