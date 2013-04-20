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

You need to run `mkprop` in two stages. First, build the missing components:

    mkprop gen test.h test.gen
    mkprop replace test.h build/test.h

`build/test.h` will be the actual header used by `moc` and included by your program.
