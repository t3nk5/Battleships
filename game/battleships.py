from pandas import Series
from pydantic.dataclasses import dataclass, overload


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
        Index: int | None
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
    def case_data(uuid: float) -> 'Ship.Data':
        value = abs(uuid)
        return Ship.Data(
            Alive=uuid > 0,
            Size=(value // 100) % 100,
            Type=(value // 10) % 10,
            Index=int(value) % 10,
            ID=int(value * 100 % 100)
        )

    @staticmethod
    def ship_data(ship: Series) -> 'Ship.Data':
        ship = ship[ship.notna()].apply(lambda x: Ship.case_data(x))
        return Ship.Data(
            Alive=any(s.Alive for s in ship),
            Size=(lambda s: s.iloc[0] if s.nunique() == 1 else (_ for _ in ()).throw(
                ValueError(f'the Size attribute is not unique : {s.unique()}')))(ship.map(lambda d: d.Size)),
            Type=(lambda s: s.iloc[0] if s.nunique() == 1 else (_ for _ in ()).throw(
                ValueError(f'the Type attribute is not unique : {s.unique()}')))(ship.map(lambda d: d.Type)),
            Index=None,
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
    Carrier: 1,
    Battleship: 2,
    Destroyer: 3,
    Submarine: 4,
    PatrolBoat: 5,
}
