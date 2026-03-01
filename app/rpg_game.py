class Hero:

    def __init__(self, name, hp=100):
        self.name = name
        self.max_hp = hp
        self.current_hp = hp
        self.level = 1
        self.xp = 0
        self.is_alive = True

    def take_damage(self, amount):
        if amount < 0:
            raise ValueError("Damage cannot be negative")
        self.current_hp -= amount
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False

    def heal(self, amount):
        if not self.is_alive:
            raise RuntimeError("Cannot heal a dead hero")
        self.current_hp += amount
        self.current_hp = min(self.current_hp, self.max_hp)

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= 100:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.xp -= 100
        self.max_hp += 20
        self.current_hp = self.max_hp
