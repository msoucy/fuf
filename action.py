#!/usr/bin/env python
"""
Action Set class and demonstration
Matt Soucy

The main purpose of this file is to demonstrate some of the fun things
that can be done with functions in Python.

Particularly interesting are:
- `copyfunction`: Duplicates a function perfectly down to the signature
   that is stored internally and printed with using help()
- `ActionSet().__call__`: uses magic for wrapping a function and hiding metadata
- `ActionSet`: Shows how easy it can be to inherit from `dict`
"""
from __future__ import print_function
from functools import wraps

def copyfunction(func):
    '''Creates an exact duplicate of the given function
    This includes the signature and help message'''
    # We use type(func) because there's no convenient way
    # to access the function type otherwise
    return wraps(func)(type(func)(func.__code__, func.__globals__,
                                  func.__name__, func.__defaults__,
                                  func.__closure__))


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
        # Also (should) handle Python 3 properly
        if hasattr(name, '__call__') and helpmsg is None:
            # Call ourself again with the default parameters, and pretend
            # that the layer of indirection doesn't exist
            return self(None, None)(name)

        def make_action(oldfunc):
            '''Set up the wrapper
            Adds attributes to a simple wrapper function
            Could modify the wrapper directly, but if other decorators or functions
            use a similar trick it could cause interference'''

            # Create the wrapper
            func = copyfunction(oldfunc)

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
