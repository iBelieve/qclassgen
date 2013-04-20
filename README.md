QProperty Maker - Qt property generator
================================

Generates missing functions, signals, and variables based on `Q_PROPERTY` definitions.

### Licensing ###

QProperty Maker is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

### How to Use ###

In your class definition, include the generated code:

    class Test {
        Q_OBJECT

        Q_PROPERTY(int test READ test)
    
    #include "test.gen"
    }

Then, you need to run `mkprop` on it:

    mkprop test.h build/test.gen build/test.h

Because `moc` doesn't search the include path, the source file needs to be in the same directory as the generated header:

    cp test.cpp build/test.cpp
    
`build/test.h` and `build/test.cpp` will be the actual code used by `moc`. Make sure you add `build` to your list of include directories, and add `build.test.cpp` to the list of source files.