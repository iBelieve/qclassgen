#!/usr/bin/env python

# Class Generator - Automatically generate parts of Qt classes.
# Copyright (C) 2013  Michael Spencer <spencers1993@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

def search(text):
	p = re.compile('^(\\s*?)#include \"(.*)\\.gen\"\\s*$', re.MULTILINE)
	m = p.search(text)
	while m:
		indent = m.group(1)
		name = m.group(2)
		#replacement = open(name + '.gen').read()
		# Quicker: assume file just generated
		replacement = header
		replacement = indent + replacement.replace('\n', indent)
		#print replacement
		text = text.replace(m.group(0), replacement)
		m = p.search(text, m.pos)
	return text

def replace():
	print 'Including generated code...'
	output = search(input)
	f_out = open(sys.argv[3], 'w')
	f_out.write(output)

def process(lines, line):
	global public, public_slots, protected, private, signals

	if not(line.startswith('Q_PROPERTY')):
		return
	
	print line

	# Extract the name and type
	p = re.compile('Q_PROPERTY\\((\\w*[\\s\\*]*)(\\w*)\\s*READ\\s*(\\w*)')
	m = p.match(line)
	if not(m):
		raise BaseException('Invalid property: ' + line)
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

	if not(find_start(lines, type + 'm_' + name)):
		func =  '\t' + type + 'm_' + name;
		if type.endswith('*'):
			func += ' = 0'
		func += ';\n'
		if write: private += func
		else: protected += func

	if not(find_start(lines, type + read + '(')):
		public += ('\t' + type + read + '() {\n' + 
				'\t\treturn m_' + name + ';\n' +
				'\t}\n')

	if write and not(find_start(lines, 'void ' + write + '(')):
		public_slots += ('\tvoid ' + write + '(' + type + name + ') {\n' +
				'\t\tm_' + name + ' = ' + name + ';\n' +
				'\t}\n')

	if not(find_start(lines, 'void ' + notify + '(')):
		signals += '\tvoid ' + notify + '(' + type + name + ');\n'

	return

def generate():
	global input, header
	f_in = open(sys.argv[1])
	print 'Processing...'
	f_gen = open(sys.argv[2], 'w')
	input = f_in.read()
	lines = [line.strip() for line in input.split('\n')]
	[process(lines, line) for line in lines]
	header = public + '\n' + public_slots + '\n' + protected + '\n' + private + '\n' + signals
	f_gen.write(header)

if __name__=='__main__':
	help = 'classgen header gen [out]'
	
	generate()
	replace()