#!/usr/bin/env python
from __future__ import print_function

# Possible enhancements may include:
# Deriving from dict (remove need to specify some magic functions)

class ActionSet(object):

    '''Specifies a set of actions
    It's possible to have more than one set at a time'''

    def __init__(self, prefix=None):
        '''Setup
        If a prefix is specified, then it attempts to remove that prefix from
        the names of functions when creating actions'''
        self._actions = {}
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

        def make_action(func):
            'Set up the wrapper'
            # Simpler accessor to action name
            func.name = name or func.__name__
            if self._prefix and func.name.startswith(self._prefix):
                func.name = func.name.replace(self._prefix, "", 1)

            # Simpler accessor to help message
            func.helpmsg = helpmsg or func.__doc__.split("\n")[0]

            # Regiser action into the action set
            self._actions[func.name] = func
            return func

        return make_action

    def __getitem__(self, name):
        'Allow dictionary-like subscripting'
        return self._actions[name]

    def __iter__(self):
        'Allow iteration over the available actions'
        return self._actions.__iter__()

    def __contains__(self, name):
        'Allow using "in" to detect items'
        return name in self._actions

    def perform(self, msg):
        'Perform an action based on a simplistic CLI-like argument splitting'
        if not msg.strip():
            return
        args = msg.split()
        command = args.pop(0).lower()
        if command in self._actions:
            return self._actions[command](args)
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
        try: return raw_input(">> ")
        except EOFError: return ""
    inp = get_input()
    while inp:
        try: action.perform(inp)
        except KeyError as e:
            print("Key error:", e)
        inp = get_input()
