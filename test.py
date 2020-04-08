import unittest
from itertools import combinations
from units import Quantity, Dimension, UnitError


class TestQuantity(unittest.TestCase):
    def setUp(self):
        self.m = Dimension('m', 'meter')
        self.s = Dimension('s', 'second')
        self.kg = Dimension('kg', 'kilogram')

        self.N = Quantity({self.kg: 1, self.m: 1, self.s: -2})
        self.h = Quantity({self.s: 1}, 3600)
        self.km = Quantity({self.m: 1}, 1e3)
        self.kmh = Quantity({self.km: 1, self.h: -1})
        self.l = Quantity({self.m: 3}, 1e-3)
        self.J = Quantity({self.N: 1, self.km: 1}, 1e-3)

    def test_constructor_params(self):
        N = self.N
        arg_kwargs = (
                ((), dict(value=5, factors={N: 1})),
                ((5, {N: 1}), {}),
                (({N: 1}, 5), {}),
                (([(N, 1)], 5), {}),
                ((5, [(N, 1)]), {}),
                ((5,) , dict(factors={N: 1})),
                (({N: 1}, ), dict(value=5))
            )

        expected = 5*N
        for args, kwargs in arg_kwargs:
            with self.subTest(args=args, kwargs=kwargs):
                self.assertEqual(Quantity(*args, **kwargs), expected)


    def test_internal_values(self):
        m, s, kg, N, h, km, kmh, l, J = \
            self.m, self.s, self.kg, self.N, self.h, self.km, \
            self.kmh, self.l, self.J

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

    def test_multiplication(self):
        m, s, kg, N, h, km, kmh, l, J = \
            self.m, self.s, self.kg, self.N, self.h, self.km, \
            self.kmh, self.l, self.J

        hN = h * N
        Nh = N * h
        self.assertEqual(Nh, hN)
        self.assertDictEqual(Nh.vector, {kg: 1, m: 1, s: -1})
        self.assertEqual(Nh.value, 3600)
        self.assertNotEqual(Nh, N)
        self.assertNotEqual(Nh, h)
        self.assertEqual((3 * Nh).value, 3*3600)
        self.assertEqual(3 * Nh, hN * 3)

        self.assertEqual(2, Quantity(2))
        self.assertNotEqual(2*m, Quantity(2))
        self.assertEqual(2*m, 2*Quantity({m: 1}))

        Hz = Quantity({h: -1}, 3600)
        self.assertEqual(1/s, Hz)

        self.assertEqual(m, km/1000)
        self.assertNotEqual(m, km/100)
        self.assertNotEqual(m, m * km/1000)

        self.assertEqual(1e3*m, km)

    def test_zero(self):
        m, s = self.m, self.s
        zero = m - m
        self.assertEqual(zero, 0*m)
        self.assertDictEqual(zero.vector, {m: 1})
        self.assertEqual(zero.value, 0)
        self.assertNotEqual(zero, 0)
        self.assertRaises(UnitError, lambda: zero + s)
        self.assertRaises(UnitError, lambda: zero + 0)

    def test_addition_value(self):
        km, m = self.km, self.m

        length = km + 2*m - 0.5*km
        self.assertEqual(length.value, 502)
        self.assertDictEqual(length.vector, km.vector)

    def test_addition_error(self):
        m, s, h, N, J = self.m, self.s, self.h, self.N, self.J
        self.assertRaises(UnitError, lambda: m + s)
        self.assertRaises(UnitError, lambda: m + h)
        self.assertRaises(UnitError, lambda: m**3 + m)
        self.assertRaises(UnitError, lambda: N + J)

    def test_scalar(self):
        m = self.m
        one = m/m
        self.assertEqual(one.value, 1)
        self.assertDictEqual(one.vector, {})
        self.assertEqual(one, Quantity())

        zero = m - m
        self.assertEqual(0, 1 - Quantity(1))
        self.assertNotEqual(zero, 1 - Quantity(1))

    def test_fractional_exponent(self):
        m, l = self.m, self.l
        self.assertAlmostEqual(0.1*m, l**(1, 3), delta=0.001*m)
        self.assertAlmostEqual(0.1*m, l**'1/3', delta=0.001*m)
        self.assertNotEqual(0.11*m, l**'1/3')
        self.assertAlmostEqual(Quantity(2) ** 3.5, 11.31370, delta=0.001)
        self.assertWarns(Warning, lambda: Quantity({m: 0.3}))
        self.assertWarns(Warning, lambda: m**(3/2))

    def test_hash(self):
        m = self.m
        self.assertEqual(1 * m, m)
        self.assertEqual(hash(1*m), hash(m))
        self.assertEqual(1.0 * m, m)
        self.assertEqual(hash(1.0*m), hash(m))

    def test_compare(self):
        m, km, s = self.m, self.km, self.s
        self.assertTrue(m < km)
        self.assertTrue(3*m >= m)
        self.assertTrue(1 <= km/m)

        self.assertRaises(UnitError, lambda: m > s)
        self.assertRaises(UnitError, lambda: 0 > m)

    def test_compound(self):
        m, s, kg, N, h, km, kmh, l, J = \
            self.m, self.s, self.kg, self.N, self.h, self.km, \
            self.kmh, self.l, self.J

        inch = Quantity({m: 1}, 0.0254)
        sq_inch = Quantity({inch: 2})

        self.assertEqual(inch * inch, sq_inch)
        self.assertEqual(2* sq_inch**'1/2', 2*inch)


class TestDimension(unittest.TestCase):
    def test_constructor(self):
        m = Dimension('m', 'meter')

        self.assertEqual(m.name, 'm')
        self.assertEqual(m.fullname, 'meter')
        self.assertTrue(m in m.vector)
        self.assertEqual(m.vector[m], 1)
        self.assertEqual(hash(m), id(m))


if __name__ == '__main__':
    unittest.main()

