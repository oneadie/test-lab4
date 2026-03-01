import unittest
from app.rpg_game import Hero

class TestHeroRPG(unittest.TestCase):
    def setUp(self):
        self.hero = Hero("Witcher", hp=100)

    def test_initial_state(self):
        self.assertEqual(self.hero.name, "Witcher")
        self.assertEqual(self.hero.current_hp, 100)
        self.assertTrue(self.hero.is_alive)

    def test_take_damage(self):
        self.hero.take_damage(30)
        self.assertEqual(self.hero.current_hp, 70)

    def test_hero_death(self):
        self.hero.take_damage(150)
        self.assertEqual(self.hero.current_hp, 0)
        self.assertFalse(self.hero.is_alive)

    def test_negative_damage_error(self):
        with self.assertRaises(ValueError):
            self.hero.take_damage(-10)

    def test_healing(self):
        self.hero.take_damage(50)
        self.hero.heal(20)
        self.assertEqual(self.hero.current_hp, 70)

    def test_healing_over_max(self):
        self.hero.take_damage(10)
        self.hero.heal(50)
        self.assertEqual(self.hero.current_hp, 100)

    def test_heal_dead_hero(self):
        self.hero.take_damage(100)
        with self.assertRaises(RuntimeError):
            self.hero.heal(10)

    def test_gain_xp_simple(self):
        self.hero.gain_xp(50)
        self.assertEqual(self.hero.xp, 50)
        self.assertEqual(self.hero.level, 1)

    def test_level_up_mechanic(self):
        self.hero.gain_xp(100)
        self.assertEqual(self.hero.level, 2)
        self.assertEqual(self.hero.xp, 0)
        self.assertEqual(self.hero.max_hp, 120)

    def test_level_up_heals_fully(self):
        self.hero.take_damage(90)
        self.hero.gain_xp(120)
        self.assertEqual(self.hero.level, 2)
        self.assertEqual(self.hero.current_hp, 120)
        self.assertEqual(self.hero.xp, 20)

if __name__ == '__main__':
    unittest.main()