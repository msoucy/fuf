import sys # For module support
from wrapper import wrapper

_DoesNotExist_ = lambda:None

# Possible situations:
#@Overload
#@Overload()
#@Overload(args)
#@manual.reg
#@manual.reg()
#@manual.reg(args)

class OverloadSet(object):
    def __init__(self):
        self.members = []
    def __call__(self, *args, **kwargs):
        for cond, kcond, func in self.members:
            print(args)
            print(cond)
            print(kcond)
            if all((len(cond) <= len(args),
                    all(c(arg) for c, arg in zip(cond, args)),
                    all(kcond.get(name, _)(kwargs.get(name, _DoesNotExist_)) for name in kcond)
                )):
                return func(*args, **kwargs)
    def reg(self, func, *constraints, **kwconstraints):
        self.members.append((constraints, kwconstraints, func))

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

_ = AnyArgument  = constraint(lambda arg: True)
lt = lambda value: constraint(lambda arg: arg < value)
le = lambda value: constraint(lambda arg: arg <= value)
gt = lambda value: constraint(lambda arg: arg > value)
ge = lambda value: constraint(lambda arg: arg >= value)
eq = lambda value: constraint(lambda arg: arg == value)
ne = lambda value: constraint(lambda arg: arg != value)

Or  = lambda lpred, rpred: constraint(lambda arg: (lpred(arg) or rpred(arg)))
And = lambda lpred, rpred: constraint(lambda arg: (lpred(arg) and rpred(arg)))
Not = lambda pred: constraint(lambda arg: not pred(arg))
Is  = lambda t: constraint(lambda arg: isinstance(arg, t))

Exists = constraint(lambda arg: arg is not _DoesNotExist_)

# Testing out

def test_abs():

    @Overload(ge(0))
    def foo(x):
        return x

    @Overload(lt(0))
    def foo(x):
        return -x

    assert foo(10) == 10
    assert foo(-10) == 10

def test_sum():
    @Overload(len)
    def sumlist(lst):
        return lst[0] + sumlist(lst[1:])

    @Overload()
    def sumlist(lst):
        return 0

    assert sumlist(range(6)) == 15

def test_is():
    @Overload(Is(int))
    def typetest(x):
        return True

    @Overload()
    def typetest(x):
        return False

    assert typetest(5)
    assert not typetest(5.0)

def test_manual():
    manual = OverloadSet()

    @manual.reg(lt(2))
    def fact(x):
        return 1

    @manual.reg
    def fact(x):
        return x * fact(x-1)

    assert fact(6) == 720

tests = [
        test_abs,
        test_sum,
        test_is,
        test_manual,
]

for test in tests:
    test()
