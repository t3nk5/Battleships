from pydantic.dataclasses import dataclass


class Ship:
    def __init__(self, ship_id: int, *, ship_type_id: int, size: int):
        self.id = ship_id
        self.type_id = ship_type_id
        self.size = size

    @property
    def uuid(self):
        return self.size * 100 + self.type_id * 10 + self.id * 0.01

    @dataclass
    class Data:
        Alive: bool
        Size: int
        Type: int
        Index: int
        ID: int

        def __repr__(self):
            return (f'Ship.Data(\n'
                    f'   Alive={self.Alive},\n'
                    f'   Size={self.Size},\n'
                    f'   Type={self.Type},\n'
                    f'   Index={self.Index},\n'
                    f'   ID={self.ID}\n'
                    f')')

    @staticmethod
    def get_data(uuid: float):
        value = abs(uuid)
        return Ship.Data(
            Alive=uuid > 0,
            Size=(value // 100) % 100,
            Type=(value // 10) % 10,
            Index=int(value) % 10,
            ID=int(value * 100 % 100)
        )


class Carrier(Ship):  # 1
    def __init__(self, ship_id: int):
        super().__init__(ship_id, size=5, ship_type_id=1)


class Battleship(Ship):  # 1
    def __init__(self, ship_id: int):
        super().__init__(ship_id, size=4, ship_type_id=2)


class Destroyer(Ship):  # 2
    def __init__(self, ship_id: int):
        super().__init__(ship_id, size=3, ship_type_id=3)


class Submarine(Ship):  # 1
    def __init__(self, ship_id: int):
        super().__init__(ship_id, size=3, ship_type_id=4)


class PatrolBoat(Ship):  # 1
    def __init__(self, ship_id: int):
        super().__init__(ship_id, size=2, ship_type_id=5)
