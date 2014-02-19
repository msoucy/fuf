#!/usr/bin/env python
"""
Action Set class and demonstration
Matt Soucy

The main purpose of this file is to demonstrate some of the fun things
that can be done with functions in Python.

Particularly interesting are:
- `wrapper`: Duplicates a function perfectly down to the signature
   that is stored internally and printed with using help()
- `wwrapper`: Wrapper wrapper - apply as a decorator to a decorator to produce
   a decorator that generates perfect-forwarded functions
- `ActionSet().__call__`: uses magic for wrapping a function and hiding metadata
- `ActionSet`: Shows how easy it can be to inherit from `dict`

Ideas taken from:
- http://numericalrecipes.wordpress.com/2009/05/25/signature-preserving-function-decorators/
- http://github.com/msoucy/RepBot
"""
from __future__ import print_function
import inspect  # Used to create our duplicate
from functools import update_wrapper  # Convenience to update the metadata
import sys # Used to get rid of py2/3 differences

# Blatantly stolen from the excellent `six` library
# Allows the same calls between python2 and python3
if sys.version_info[0] == 3:
    exec_ = getattr(__builtins__, "exec")
    raw_input = input
else:
    def exec_(_code_, _globs_=None, _locs_=None):
        """Execute code in a namespace."""
        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")


def wwrapper(_wrap_):
    '''Wrap a decorator with support for the perfect wrapper decorator'''
    def wrapper(_func_):
        '''Create a perfect wrapper (including signature) around a function'''
        # convert bar(f)(*args, **kwargs)
        # into    f(*args, **kwargs)
        src = r'def {0}{1}: return _wrap_(func){1}'.format(
            _func_.__name__,
            inspect.formatargspec(*inspect.getargspec(_func_))
        )
        evaldict = {'_wrap_': _wrap_, 'func': _func_}
        exec_(src, evaldict)
        ret = evaldict[_func_.__name__]
        update_wrapper(ret, _func_)
        return ret
    return wrapper

wrapper = wwrapper((lambda func:(lambda *_a, **_kw: func(*_a, **_kw))))

class ActionSet(dict):

    '''Specifies a set of actions
    It's possible to have more than one set at a time
    Derives from dict to allow the user to perform useful actions on it'''

    def __init__(self, prefix=None):
        '''Setup
        If a prefix is specified, then it attempts to remove that prefix from
        the names of functions when creating actions'''
        dict.__init__(self)
        self._prefix = prefix

    def __call__(self, name=None, helpmsg=None):
        '''Create the actual wrapper'''

        # OK kids, this is where it gets complicated
        # Special case
        # If they try to decorate without passing any arguments,
        # this allows them to not even need the parenthesis.
        # Works on callables, not just functions
        # Also handles Python 3 properly
        if hasattr(name, '__call__') and helpmsg is None:
            # Call ourself again with the default parameters, and pretend
            # that the layer of indirection doesn't exist
            return self(None, None)(name)

        def make_action(func):
            '''Set up the wrapper
            Adds attributes to a simple wrapper function
            Could modify the wrapper directly, but if other decorators or functions
            use a similar trick it could cause interference'''

            # Create the wrapper
            func = wrapper(func)

            # Simpler accessor to action name
            func.name = name or func.__name__
            if self._prefix and func.name.startswith(self._prefix):
                func.name = func.name.replace(self._prefix, "", 1)

            # Simpler accessor to help message
            func.helpmsg = helpmsg or func.__doc__.split("\n")[0]

            # Regiser action into the action set
            self[func.name] = func
            return func

        return make_action

    def perform(self, msg):
        'Perform an action based on a simplistic CLI-like argument splitting'
        if not msg.strip():
            return
        args = msg.split()
        command = args.pop(0)
        if command in self:
            return self[command](args)
        else:
            raise KeyError('Invalid action "%s"' % command)


# Create a simple action set
action = ActionSet()


# Full decorator
# Nothing is gathered implicitly
@action("help", "List command help")
def action_help(args):
    "List command help"
    if args:
        for arg in args:
            if arg in action:
                print("{0.name}:\t{0.helpmsg}".format(action[arg]))
    else:
        print("Available commands:", ", ".join(a for a in action))


# Partially applied
# The name is specified, but the help is pulled from the docstring
@action("verify")
def action_verify(args):
    "Confirm access"
    print("Authentication valid")


# Implicit
# The name of the command and the help are pulled from
# the function name and docstring
@action
def say(args):
    "Say a message"
    print(" ".join(args))


# Testing driver
if __name__ == '__main__':
    def get_input():
        try:
            return raw_input(">> ")
        except EOFError:
            return ""
    inp = get_input()
    while inp:
        try:
            action.perform(inp)
        except KeyError as e:
            print("Key error:", e)
        inp = get_input()
