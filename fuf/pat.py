import sys # For module support
from inspect import isclass, isroutine

# Special simgleton value, used for testing if an argument exists
_DoesNotExist_ = object()

def try_condition(c, a):
    """ Perform the correct test depending on the type """
    # It's a class, so see if the argument has that type
    if isclass(c): return isinstance(a, c)
    # It's a function, so treat the return value as a predicate
    elif isroutine(c): return c(a)
    # It's a value, do a regular comparison for equality
    else: return c == a

class OverloadSet(object):
    """ Set of overloaded functions
    Overloads are based on arbitrary constraints """
    def __init__(self):
        """ Initialize an overload set """
        self._overloads = []
    def __call__(self, *args, **kwargs):
        """ Search for the best overload """

        for cond, kcond, func in self._overloads:
            if all((
                    len(cond) <= len(args),
                    all(try_condition(c, arg) for c, arg in zip(cond, args)),
                    all(kcond.get(name, _)(kwargs.get(name, _DoesNotExist_)) for name in kcond)
                )):
                return func(*args, **kwargs)
        raise RuntimeError("No match found for arguments %s %s" % (args, kwargs))

    def reg(self, *cond, **kwcond):
        """ Registration decorator
        Provides a method to register a function """
        def wrap(f):
            self._overloads.append((cond, kwcond, f))
            return self
        return wrap

def Overload(*constraints, **kconstraints):
    def wrap(f):
        f = getattr(f, "__lastreg__", f)
        name = f.__name__
        mod = sys.modules[f.__module__]
        if not hasattr(mod, name):
            setattr(mod, name, OverloadSet())
        newfunc = getattr(mod, name)
        newfunc.reg(*constraints, **kconstraints)(f)
        newfunc.__lastreg__ = f
        return newfunc
    return wrap


# Constraints
# These exist for convenience

def constraint(func):
    """
    Create a complex contraint out of a function
    A variation of partial application
    The first argument is the only non-fixed argument.
    That argument is the one being tested.
    constraint should only be used for predicates that require arguments
    """
    return lambda *args, **kwargs: (lambda arg: func(arg, *args, **kwargs))

# Any value is valid
Any = _ =            lambda arg: True
# Does the argument exist? (Use for keyword arguments)
Exists  =            lambda arg: arg is not _DoesNotExist_
Or      = constraint(lambda arg, lpred, rpred: (lpred(arg) or rpred(arg)))
And     = constraint(lambda arg, lpred, rpred: (lpred(arg) and rpred(arg)))
Not     = constraint(lambda arg, pred: not pred(arg))
Between = constraint(lambda arg, low, high: low <= arg < high)
# One of a set of values
In      = constraint(lambda arg, *args: arg in args)

import operator
for op in ["lt", "le", "gt", "ge", "eq", "ne"]:
    # Basic conditional operators
    globals()[op] = constraint(getattr(operator, op))
Has = constraint(operator.contains)
Is  = constraint(operator.is_)

'''
A few of the rules are solely in place for berevity:
Between = And(ge(a), lt(b))
No = Not(Yes)
'''
