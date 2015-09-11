# Created by STC at 9/11/15

"""
Concepts/Goals:

  When first initiating a class ("base object"),
    all nested sub-classes of all depths (hereinafter "all sub-classes"),
      and all functions of all sub-classes,
    become immediately and readily accessible.

  All functions in all sub-classes are readily available, and
    a shared library is accessible using a common syntax.

  Base objects are readily accessible from within all sub-classes.

  Enabling structure and features of this framework requires only a single, readily understandable, command.

Challenges:

  It is true that all object and sub-objects can be consolidated and directly available from a single object,
    but utility of the single object is inversely related to the growth and maturation of
    functions, classes, and systems (hereinafter collectively referred to as "a System").

  Assuming some structure is necessary, one way to extend utility is by generating a simple structure
    and provide methods for navigating said structure that
    (1) are accessible at every level of a System, and
    (2) are accessed using a common syntax.




"""


@framework
Feature: Sub Classes Immediately Accessible
  # From within any nested sub class, at any depth,
  #   provide quick access to most top-level class

  # when first initiating class ("base object"),
  #   all nested sub-classes of all depths (hereinafter "all sub-classes"),
  #     and all functions of all sub-classes,
  #   become immediately accessible.
  # all functions in all sub-classes are readily available.
  # in any sub-classes, a shared library is accessible using a common syntax.
  # base objects are readily accessible from within all sub-classes
  # enabling structure and features of this framework requires only a single, readily understandable, command

  Scenario: Access Object from most top-level class

  Scenario: Access Object from first top-level class
