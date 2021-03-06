from .quantity import Quantity
from fractions import Fraction

__all__ = 'Dimension',

class Dimension(Quantity):
    def __init__(self, name, fullname):
        self.name = name
        self.fullname = fullname

        self.vector = {self: Fraction(1)}
        self.value = 1

    def __repr__(self):
        return self.name

    def __hash__(self):
        return id(self)
