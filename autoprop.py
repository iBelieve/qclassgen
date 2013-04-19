#! /usr/bin/env python

import sys, re

private = 'private:\n'
protected = 'protected:\n'
public = 'public:\n'
public_slots = 'public slots:\n'
signals = 'signals:\n'

def find_start(lines, search):
    for line in lines:
        if line.startswith(search):
            return line


def process(lines, line):
    global public, public_slots, protected, private, signals

    if not(line.startswith('Q_PROPERTY')):
        return

    # Extract the name and type
    p = re.compile('Q_PROPERTY\\((\\w*)\\s*(\\w*)\\s*READ\\s*(\\w*)')
    m = p.match(line)
    if not(m):
        raise 'Invalid property!'
    type = m.group(1)
    name = m.group(2)
    read = m.group(3)

    # Extract the write function
    p = re.compile('WRITE\\s*(\\w*)')
    m = p.search(line)
    write = ""
    if m:
        write = m.group(1)

    # Extract the notify signal
    p = re.compile('NOTIFY\\s*(\\w*)')
    m = p.search(line)
    notify = ""
    if m:
        notify = m.group(1)

    if not(find_start(lines, type + ' m_' + name)):
        func =  '\t' + type + ' m_' + name;
        if type.endswith('*'):
            func += ' = 0'
        func += ';\n'
        if write: private += func
        else: protected += func

    if not(find_start(lines, type + ' ' + read + '(')):
        public += ('\t' + type + ' ' + read + '() {\n' + 
                '\t\treturn m_' + name + ';\n' +
                '\t}\n')

    if write and not(find_start(lines, 'void ' + write + '(')):
       public_slots += ('\tvoid ' + write + '(' + type + ' ' + name + ') {\n' +
                '\t\tm_' + name + ' = ' + name + ';\n' +
                '\t}\n')

    if not(find_start(lines, 'void ' + notify + '(')):
        signals += '\tvoid ' + notify + '(' + type + ' ' + name + ');\n'

#    print type, name, write, notify


if __name__=='__main__':
    f_in = open(sys.argv[1])
    if len(sys.argv) > 2:
        f_out = open(sys.argv[2])
    else:
        f_out = sys.stdout
    lines = [line.strip() for line in f_in.readlines()]
    [process(lines, line) for line in lines]
    f_out.write(public + '\n' + public_slots + '\n' + protected + '\n' + private + '\n' + signals)
