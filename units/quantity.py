from collections import defaultdict
from fractions import Fraction
from numbers import Number
from functools import wraps, total_ordering, reduce
from operator import xor

import warnings

from .exceptions import *

__all__ = 'Quantity',


def _convert_if_dict(factors):
    """
    Utility Method for Quantity
    Expects Iterables of the form ((k, v), (k2, v2), ...),
    or dictionaries. If a dictionary is passed, it will
    be converted to the Iterable form
    """
    if isinstance(factors, dict):  # not very safe FIXME
        yield from factors.items()

    else:
        yield from factors


def _ensure_fraction(arg):
    """
    Utility Method for Quantity
    Converts numeric types and (numerator, denominator) 
    pairs into "Fraction"s
    Warns when there might be precision problems caused
    by a floating-point input
    """
    if isinstance(arg, float):
        message = "We strongly advice not to use floats as " \
            "exponents due to floating point precision. Consider " \
            "using 'a/b' or (a, b) instead."
        warnings.warn(message, RuntimeWarning, stacklevel=3)

    try:
        return Fraction(*arg)

    except (TypeError, ValueError):
        return Fraction(arg)


def _repr_fraction(f: Fraction):
    """
    Utility Method for Quantity
    Stringifies Fractions
    """
    if f.denominator == 1:
        return str(f.numerator)

    return f'{f.numerator}/{f.denominator}'


def _repr_power(item):
    """
    Utility Method for Quantity
    Stringifies pairs of dimensions and exponents
    """
    dim, exp = item
    if exp == 1:
        return repr(dim)

    return f'{dim!r}^{_repr_fraction(exp)}'


def quantity_operator(method):
    """
    Utility Decorator for Quantity
    Decorates member methods to ensure that all
    arguments are instances of Quantity
    """
    @wraps(method)
    def wrapper(self, *args):
        return method(self, *map(Quantity._ensure_instance, args))

    return wrapper


def restrictive_operator(method):
    """
    Utility Decorator for Quantity
    Decorates member methods to ensure that the
    passed quantities' have the same unit dimensions

    A restrictive_operator is also a quantity_operator
    """
    @wraps(method)
    @quantity_operator
    def wrapper(a, b):
        if not a.same_unit(b):
            raise UnitError(
                f'operation not supported for units "{a}" and "{b}"')

        return method(a, b)

    return wrapper


@total_ordering
class Quantity:
    """
    Quantity Class
    Represent a value with a unit
    """

    def __init__(self, *args, factors=None, value=None):
        factors, value = Quantity._parse_args(args, factors, value)
        self.value = value
        self.vector = defaultdict(Fraction)

        for factor, exponent in _convert_if_dict(factors):
            self._update_vector(
                factor,
                _ensure_fraction(exponent))

        self._remove_zeroes()

    @staticmethod
    def _parse_args(args, factors, value):
        # TODO factors can be Quantity too
        factors = {} if factors is None else factors
        value = 1 if value is None else value
        if not args:
            return factors, value

        if len(args) == 1:
            if isinstance(*args, Number):
                return (factors, *args)

            return (*args, value)

        if len(args) == 2:
            if isinstance(args[0], Number):
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

    @classmethod
    def _ensure_instance(cls, arg):
        if isinstance(arg, cls):
            return arg

        return cls(arg)

    def __repr__(self):
        if self.is_scalar:
            return repr(self.value)

        unitstr = '*'.join(map(_repr_power, self.vector.items()))
        return f'{self.value!r} {unitstr}'

    @quantity_operator
    def same_unit(self, other):
        return self.vector == other.vector

    def __pow__(self, exponent):
        if isinstance(exponent, Quantity):
            if not exponent.is_scalar:
                raise UnitError(f'expected scalar exponent, got "{exponent}"')

            exponent = exponent.value

        if self.is_scalar:
            return Quantity(value=self.value**exponent)

        return Quantity(factors=[(self, exponent)])
    
    def __rpow__(self, base):
        if not self.is_scalar:
            raise UnitError(f'expected scalar exponent, got "{self}"')

        return base ** self.value


    @quantity_operator
    def __mul__(self, other):
        return Quantity(factors=[(self, 1), (other, 1)])

    __rmul__ = __mul__

    @quantity_operator
    def __truediv__(self, other):
        return Quantity(factors=[(self, 1), (other, -1)])

    @quantity_operator
    def __rtruediv__(self, other):
        return other.__truediv__(self)

    @restrictive_operator
    def __add__(self, other):
        return Quantity(
            value=self.value + other.value,
            factors=self.vector)

    __radd__ = __add__

    @restrictive_operator
    def __sub__(self, other):
        return Quantity(
            value=self.value - other.value,
            factors=self.vector)

    @restrictive_operator
    def __rsub__(self, other):
        return Quantity(
            value=other.value - self.value,
            factors=self.vector)

    def __neg__(self):
        return Quantity(value=-self.value, factors=self.vector)

    @quantity_operator
    def __eq__(self, other):
        return self.same_unit(other) and self.value == other.value

    @restrictive_operator
    def __lt__(self, other):
        return self.value < other.value

    def __round__(self, places):
        return Quantity(value=round(self.value, places), factors=self.vector)

    def __abs__(self):
        return Quantity(value=abs(self.value), factors=self.vector)

    def __hash__(self):
        vector_hash = reduce(xor,
            (hash(dim) ^ hash(exp) for dim, exp in self.vector.items()))

        return hash(self.value) ^ vector_hash
