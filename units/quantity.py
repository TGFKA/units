from collections import defaultdict
from fractions import Fraction
from numbers import Real
from functools import wraps, total_ordering, reduce
from operator import xor

import warnings


__all__ = 'Quantity', 'UnitError'

# --- TODO get it out of here ---
def repr_fraction(f: Fraction):
    if f.denominator == 1:
        return str(f.numerator)

    return f'{f.numerator}/{f.denominator}'

def repr_factor(item):
    dim, exp = item
    if exp == 1:
        return repr(dim)

    return f'{dim}^{repr_fraction(exp)}'

class UnitError(Exception):
    pass
# ------

@total_ordering
class Quantity:
    def __init__(self, *args, factors=None, value=None):
        factors, value = Quantity._parse_args(args, factors, value)
        self.value = value
        self.vector = defaultdict(Fraction)

        for factor, exponent in Quantity._convert_if_dict(factors):
            self._update_vector(
                factor,
                Quantity._ensure_fraction(exponent))

        self._remove_zeroes()

    @staticmethod
    def _parse_args(args, factors, value):
        # TODO factors can be Quantity too
        factors = {} if factors is None else factors
        value = 1 if value is None else value
        if not args:
            return factors, value

        if len(args) == 1:
            if isinstance(*args, Real):
                return (factors, *args)

            return (*args, value)

        if len(args) == 2:
            if isinstance(args[0], Real):
                return reversed(args)
            return args

        raise ValueError(f'Expected at most two arguments, got {len(args)}')

    def _update_vector(self, qty, exponent=1):
        self.value *= qty.value**exponent
        for dimension, dim_exponent in qty.vector.items():
            self.vector[dimension] += exponent*dim_exponent

    @property
    def is_scalar(self):
        return not self.vector

    def __float__(self):
        if not self.is_scalar:
            raise UnitError(f'Unit "{self}" is not scalar')

        return self.value

    def _remove_zeroes(self):
        for dimension in self.vector.copy():
            if self.vector[dimension] == 0:
                self.vector.pop(dimension)

    @staticmethod
    def _convert_if_dict(factors):
        if isinstance(factors, dict):  # not very safe FIXME
            yield from factors.items()

        else:
            yield from factors

    @staticmethod
    def _ensure_fraction(arg):
        if isinstance(arg, float):
            message = """
We strongly advice not to use floats as exponents due to
floating point precision. Use 'a/b' or (a, b) instead."""
            warnings.warn(message, RuntimeWarning)

        try:
            return Fraction(*arg)
        
        except (TypeError, ValueError):
            return Fraction(arg)

    @classmethod
    def ensure_qty(cls, arg):
        if isinstance(arg, cls):
            return arg

        return cls(arg)

    def quantity_operator(method):
        @wraps(method)
        def wrapped(self, *args):
            return method(self, *map(Quantity.ensure_qty, args))

        return wrapped

    def restictive_operator(method):
        @wraps(method)
        def wrapped(a, b):
            if not a.same_unit(b):
                raise UnitError(
                    f'operation not supported for units "{a}" and "{b}"')

            return method(a, b)

        return wrapped

    def __repr__(self):
        if self.is_scalar:
            return repr(self.value)

        unitstr = '*'.join(map(repr_factor, self.vector.items()))
        return f'{self.value} {unitstr}'

    @quantity_operator
    def same_unit(a, b):
        return a.vector == b.vector

    def __pow__(self, exponent):
        if isinstance(exponent, Quantity):
            if not exponent.is_scalar:
                raise UnitError(f'expected scalar exponent, got "{exponent}"')

            exponent = exponent.value

        if self.is_scalar:
            return Quantity(value=self.value**exponent)

        return Quantity(factors=[(self, exponent)])

    @quantity_operator
    def __mul__(a, b):
        return Quantity(factors=[(a, 1), (b, 1)])

    __rmul__ = __mul__

    @quantity_operator
    def __truediv__(a, b):
        return Quantity(factors=[(a, 1), (b, -1)])

    @quantity_operator
    def __rtruediv__(a, b):
        return b.__truediv__(a)

    @quantity_operator
    @restictive_operator
    def __add__(a, b):
        return Quantity(
            value=(a.value + b.value),
            factors=a.vector)

    __radd__ = __add__

    @quantity_operator
    @restictive_operator
    def __sub__(a, b):
        return Quantity(
            value=(a.value - b.value),
            factors=a.vector)

    @quantity_operator
    @restictive_operator
    def __rsub__(b, a):
        return Quantity(
            value=(a.value - b.value),
            factors=b.vector)

    def __neg__(self):
        return Quantity(value=-self.value, factors=self.factors)

    @quantity_operator
    def __eq__(a, b):
        return a.same_unit(b) and a.value == b.value

    @quantity_operator
    @restictive_operator
    def __lt__(a, b):
        return a.value < b.value

    def __hash__(self):
        # credit goes to Tim Gerlach
        vector_hash = reduce(xor,
            (hash(dim)^hash(exp) for dim, exp in self.vector.items()))

        return hash(self.value) ^ vector_hash
