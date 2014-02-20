from __future__ import print_function

from fuf.action import ActionSet

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
