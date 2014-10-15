funced-up-functions
===================

 .. image:: https://pypip.in/download/fuf/badge.svg
 .. image:: https://pypip.in/version/fuf/badge.svg
 .. image:: https://pypip.in/py_versions/fuf/badge.svg
 .. image:: https://pypip.in/implementation/fuf/badge.svg
 .. image:: https://pypip.in/format/fuf/badge.svg
 .. image:: https://pypip.in/license/fuf/badge.svg

Various function-related manipulators

This is meant to be a relatively simple library that adds support for miscellaneous tricks with functions.

Some of the tools include:

- Overload sets with argument constraints
- A slightly-improved version of functools.wraps, which also copies the signature of the function
- Set of functions that gets dispatched based on the first argument - proof of concept
- A dictionary class that dispatches to another dictionary if a lookup fails
