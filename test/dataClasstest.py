from dataclasses import dataclass, replace, asdict

@dataclass
class Base:
    key: str

class Data(Base):

    def __init__(self, base: Base):
        super().__init__(base.key)
        self.id = 0

    def print(self):
        print(self.key, " ", self.id)


    def to_dict(self):
        dict = asdict(self)
        dict["id"] = self.id
        return dict

class NextData(Data):
    def f1(self):
        self.id += 1

act = Base("act")
dummy = Data(act)
act.key = "next"
print(dummy.to_dict())

next = NextData(act)
print(next.to_dict())

next.f1()
print(next.to_dict())

