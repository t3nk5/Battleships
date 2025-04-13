import re
from typing import Literal, cast, Union

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
        if value and not self.valid(value):
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

        def __init__(self, value: Type | None):
            super().__init__(value)

    class Horizontal(Coordinate):
        Values = [i + 1 for i in range(10)]
        Type = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        def __init__(self, value: Type | None):
            super().__init__(value)

    def __init__(self,
                 x: Union['Coordinates.Vertical.Type', None],
                 y: Union['Coordinates.Horizontal.Type', None]):
        self._x: Coordinates.Vertical = Coordinates.Vertical(x)
        self._y: Coordinates.Horizontal = Coordinates.Horizontal(y)

    def __getitem__(self, direction: directions) -> Coordinate:
        if direction == 'vertical' or direction == 'v':
            return self._y
        elif direction == 'horizontal' or direction == 'h':
            return self._x
        else:
            raise ValueError(f"Invalid direction: {direction}")

    def __str__(self):
        return f'{self._x}{self._y}'

    @property
    def x(self):
        return self._x.value

    @property
    def y(self):
        return self._y.value

    @staticmethod
    def select() -> 'Coordinates':
        coordinates = Coordinates.parse(
            Prompt.get('Select coordinates:', expected_type=str, formated=lambda x: x.upper()))

        return Coordinates(
            x=coordinates.x or Prompt.get(
                f'Incorrect X value, select correct X coordinate (between {Coordinates.Vertical.Values[0]} and {Coordinates.Vertical.Values[-1]}):',
                expected_type=str,
                excluded_condition=lambda x: x.upper() not in Coordinates.Vertical.Values,
                formated=lambda x: x.upper()
            ),
            y=coordinates.y or Prompt.get(
                f'Incorrect Y value, select correct Y coordinate (between {Coordinates.Horizontal.Values[0]} and {Coordinates.Horizontal.Values[-1]}):',
                expected_type=int,
                excluded_condition=lambda x: x not in Coordinates.Horizontal.Values
            ),
        )

    @staticmethod
    def parse(s: str) -> 'Coordinates':
        def parse_str(string: str) -> tuple[Coordinates.Vertical.Type | None, Coordinates.Horizontal.Type | None]:
            match = re.fullmatch(r"\s*([A-Za-z]?)\s*(-?\d+|\d+)?\s*", string)
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

        coordinates = parse_str(s)
        return Coordinates(coordinates[0], coordinates[1])
