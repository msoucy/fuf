import sys # For module support
from .wrapper import wrapper

_DoesNotExist_ = object()

class OverloadSet(object):
    def __init__(self):
        self._overloads = []
    def __call__(self, *args, **kwargs):
        for cond, kcond, func in self._overloads:
            if all((
                    len(cond) <= len(args),
                    all(c(arg) for c, arg in zip(cond, args)),
                    all(kcond.get(name, _)(kwargs.get(name, _DoesNotExist_)) for name in kcond)
                )):
                return func(*args, **kwargs)
        raise RuntimeError("No match found for arguments %s %s" % (args, kwargs))

def Overload(*constraints, **kconstraints):
    def wrap(f):
        name = f.__name__
        mod = sys.modules[f.__module__]
        if not hasattr(mod, name):
            setattr(mod, name, OverloadSet())
        getattr(mod, name).reg(f, *constraints, **kconstraints)
        return getattr(mod, name)
    return wrap

# Constraints

@wrapper
def constraint(func):
    return lambda arg: func(arg)

_ = Anything     = constraint(lambda arg: True)
lt = lambda value: constraint(lambda arg: arg < value)
le = lambda value: constraint(lambda arg: arg <= value)
gt = lambda value: constraint(lambda arg: arg > value)
ge = lambda value: constraint(lambda arg: arg >= value)
eq = lambda value: constraint(lambda arg: arg == value)
ne = lambda value: constraint(lambda arg: arg != value)
between = lambda low, high: constraint(lambda arg: low <= arg < high)

Or  = lambda lpred, rpred: constraint(lambda arg: (lpred(arg) or rpred(arg)))
And = lambda lpred, rpred: constraint(lambda arg: (lpred(arg) and rpred(arg)))
Not = lambda pred: constraint(lambda arg: not pred(arg))
Is  = lambda t: constraint(lambda arg: isinstance(arg, t))

Exists = constraint(lambda arg: arg is not _DoesNotExist_)
