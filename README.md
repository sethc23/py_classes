
### PROBLEM:

Many might have experienced as a software project develops:

- sparse lines of codes become functions,
- functions become classes,
- classes become modules/files,
- files/directories become libraries,
- etc \.\.\.

(hereinafter "*Project Maturation*")

In addition to the substantive challenges raised by the particularities of a project, *Project Maturation* begets it's own type of complexity in a number of ways, some of which currently include:

- interoperability;
- function/class/module inter-dependencies, developments and unit-testing;
- code clarity, re-usability and community utility.

### SOLUTION PROPOSED:

A method for developing and maintaining a project that:

1. easily integrates into existing projects;
2. provides, at each system level, access points to reach any other system level ("*Access Points*");
3. uses a common syntax for connecting with *Access Points*; and
4. increases code execution efficiency in most cases or otherwise imposes negligible overhead.

### CURRENT IMPLEMENTATION:

Where a module has classes configured similar to the following:

[INSERT GIST LINK HERE](http://)

This solution allows the following:

``` python
from example import Start
x = Start()
print x.T.guid,'first guid'
print x.T.user,'user defined by environmental variable'
new_guid = str(get_guid().hex)[:7]
x.T.guid = new_guid
print x.T.guid,'new guid replacing previous guid'
x.T.guid_2 = str(get_guid().hex)[:7]
print x.T.guid_2,'another new guid, this time as new object'

# Convert dictionary to class object
d = {'one':1,'two':2}
x.T.new_dictionary = d
print x.T.one
```

Running the following illustrates methods for accessing components of other objects:
``` python
from example import Start
x = Start()
x.One.Alpha.funct_1()
x.Two.Bravo.funct_1()
```



