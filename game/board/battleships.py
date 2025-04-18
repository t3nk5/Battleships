from pandas import Series
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
        alive: bool
        size: int
        type: int
        index: int | None
        ID: int

        def __repr__(self):
            return (f'Ship.Data(\n'
                    f'   Alive={self.alive},\n'
                    f'   Size={self.size},\n'
                    f'   Type={self.type},\n'
                    f'   Index={self.index},\n'
                    f'   ID={self.ID}\n'
                    f')')

    @staticmethod
    def case_data(uuid: float) -> 'Ship.Data':
        value = abs(uuid)
        return Ship.Data(
            alive=uuid > 0,
            size=(value // 100) % 100,
            type=(value // 10) % 10,
            index=round(value, 0) % 10,
            ID=round(value * 100 % 100, 0)
        )

    @staticmethod
    def ship_data(ship: Series) -> 'Ship.Data':
        ship = ship[ship.notna()].apply(lambda x: Ship.case_data(x))
        return Ship.Data(
            alive=any(s.alive for s in ship),
            size=(lambda s: s.iloc[0] if s.nunique() == 1 else (_ for _ in ()).throw(
                ValueError(f'the Size attribute is not unique : {s.unique()}')))(ship.map(lambda d: d.size)),
            type=(lambda s: s.iloc[0] if s.nunique() == 1 else (_ for _ in ()).throw(
                ValueError(f'the Type attribute is not unique : {s.unique()}')))(ship.map(lambda d: d.type)),
            index=None,
            ID=(lambda s: s.iloc[0] if s.nunique() == 1 else (_ for _ in ()).throw(
                ValueError(f'the ID attribute is not unique : {s.unique()}')))(ship.map(lambda d: d.ID)),
        )


class Carrier(Ship):  # 1
    def __init__(self, ship_id: int):
        super().__init__(ship_id, size=5, ship_type_id=ship_ids[type(self)])


class Battleship(Ship):  # 1
    def __init__(self, ship_id: int):
        super().__init__(ship_id, size=4, ship_type_id=ship_ids[type(self)])


class Destroyer(Ship):  # 2
    def __init__(self, ship_id: int):
        super().__init__(ship_id, size=3, ship_type_id=ship_ids[type(self)])


class Submarine(Ship):  # 1
    def __init__(self, ship_id: int):
        super().__init__(ship_id, size=3, ship_type_id=ship_ids[type(self)])


class PatrolBoat(Ship):  # 1
    def __init__(self, ship_id: int):
        super().__init__(ship_id, size=2, ship_type_id=ship_ids[type(self)])


ship_ids = {
    Carrier: 1, # size: 5
    Battleship: 2, # size: 4
    Destroyer: 3, # size: 3
    Submarine: 4, # size: 3
    PatrolBoat: 5, # size: 2
}
