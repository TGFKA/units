from .dimension import Dimension as Dim

# Unit("e", 1.602e-19, (a, 1), (s, 1)) with a, s as units or dimensions
# string input in later version with parser

'''
import uneats as u
m = u.Dim("m")
s = u.Dim("s")
v0 = u.Unit("v0", 1, [(m, 1), (s, -1)])
v1 = u.Unit("v0", 2, [(m, 1), (s, -1)])
v0sq_m = u.Unit("v0sq_m", 2, [(v1, 2), (m, 1)])
y = u.Unit("y", 1, ((v0sq_m, -2), (s, 1)))
'''


class Unit:
    def __init__(self, name, val, *units, fullname=None, baseunits=True):
        self.name = name
        self.fullname = fullname
        self.val = val
        self.units = {}

        if len(units) == 0: return

        # (unit1, pow1), (unit2, pow2), ...
        if type(units[0]) != dict:
            for unit, power in units:
                if baseunits:
                    (self.incoorp_dim if unit.__class__ is Dim else self.incoorp_unit)(unit, power)
                else: self.incoorp_dim(unit, power)

        # {unit1: pow1, unit2: pow2, ...}
        else:
            units = units[0]  # reverse tuple from * in params
            if baseunits:
                self.incoorp_unit(Unit("temporary", 1, units, baseunits=False))
            else:
                self.units = units

    def incoorp_unit(self, unit, power=1):
        self.val *= unit.val**power
        for u_unit in unit.units:
            incoorp_func = self.incoorp_dim if (u_unit.__class__ is Dim) else self.incoorp_unit
            incoorp_func(u_unit, power*unit.units[u_unit])

    def incoorp_dim(self, dim, power=1):
        self.units.setdefault(dim, 0)
        self.units[dim] += power
