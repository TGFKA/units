import unittest
from unittest import TestCase
from units import Quantity, Dimension, UnitError


m = Dimension('m', 'meter')
s = Dimension('s', 'second')
kg = Dimension('kg', 'kilogram')


class TestQuantity(TestCase):
    def test(self):
        N = Quantity({kg: 1, m: 1, s: -2})
        h = Quantity({s: 1}, 3600)
        km = Quantity({m: 1}, 1e3)
        kmh = Quantity({km: 1, h: -1})
        l = Quantity({m: 3}, 1e-3)
        J = Quantity({N: 1, km: 1}, 1e-3)

        self.assertDictEqual(N.vector, {kg: 1, m: 1, s: -2})
        self.assertEqual(N.value, 1)
        self.assertDictEqual(J.vector, {kg: 1, m: 2, s: -2})
        self.assertEqual(kmh.value, 1000/3600)
        self.assertDictEqual(l.vector, {m: 3})
        self.assertEqual(km.value, 1000)
        self.assertDictEqual(km.vector, {m: 1})

        l3 = l**3
        self.assertDictEqual(l3.vector, {m: 9})
        self.assertEqual(l3.value, 1e-9)

        Nh = N * h
        hN = h * N
        self.assertEqual(Nh, hN)
        self.assertDictEqual(Nh.vector, {kg: 1, m: 1, s: -1})
        self.assertEqual(Nh.value, 3600)
        self.assertNotEqual(Nh, N)
        self.assertNotEqual(Nh, h)
        self.assertEqual((3 * Nh).value, 3*3600)
        self.assertEqual(3 * Nh, hN * 3)

        zero = m - m
        self.assertEqual(zero, 0*m)
        self.assertDictEqual(zero.vector, {m: 1})
        self.assertEqual(zero.value, 0)

        length = km + 2*m - 0.5*km
        self.assertEqual(length.value, 502)
        self.assertDictEqual(length.vector, km.vector)

        one = h/h
        self.assertEqual(one.value, 1)
        self.assertDictEqual(one.vector, {})
        self.assertEqual(one, Quantity())

        self.assertEqual(2, Quantity(2))
        self.assertNotEqual(2*m, Quantity(2))
        self.assertEqual(2*m, 2*Quantity({m: 1}))

        Hz = Quantity({h: -1}, 3600)
        self.assertEqual(1/s, Hz)
        
        self.assertEqual(m, km/1000)
        self.assertNotEqual(m, km/100)
        self.assertNotEqual(m, m * km/1000)

        self.assertAlmostEqual(0.1*m, l**(1, 3))
        self.assertAlmostEqual(0.1*m, l**'1/3')
        self.assertNotEqual(0.11*m, l**'1/3')

        self.assertEqual(0, 1 - Quantity(1))
        self.assertEqual(zero, 1 - Quantity(1))

        self.assertAlmostEqual(Quantity(2) ** 3.5, 11.31370, delta=0.001)

        self.assertEqual(1e3*m, km)

        self.assertEqual(1 * m, m)
        self.assertEqual(hash(1*m), hash(m))
        self.assertEqual(1.0 * m, m)
        self.assertEqual(hash(1.0*m), hash(m))

        self.assertRaises(UnitError, lambda: m + s)
        self.assertRaises(UnitError, lambda: m + h)
        self.assertRaises(UnitError, lambda: m**3 + m)
        self.assertRaises(UnitError, lambda: N + J)

        with self.assertWarns(Warning):
            c = Quantity({m: 0.3})



class TestDimension(TestCase):
    def test_constructor(self):
        m = Dimension('m', 'meter')

        self.assertEqual(m.name, 'm')
        self.assertEqual(m.fullname, 'meter')
        self.assertTrue(m in m.vector)
        self.assertEqual(m.vector[m], 1)
        self.assertEqual(hash(m), id(m))



if __name__ == '__main__':
    unittest.main()