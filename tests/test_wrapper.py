from __future__ import print_function

from fuf.wrapper import wwrapper


# Test the "decorator decorator"
@wwrapper
def myWrapper(f):
    def _wrapped(*args, **kwargs):
        print("Before", args, kwargs)
        ret = f(*args, **kwargs)
        print("After")
        return ret
    return _wrapped

# Sample usage of the custom wrapper
@myWrapper
def myAdd(a, b):
    return a+b

