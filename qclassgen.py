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
	type = '[\\w:]+(\\<([\\w:]*(\\s*\\*)?\\s*)(\\,\\s*[\\w:]*(\\s*\\*)?\\s*)*\\>\\s*)?(\\s*\\*)?\\s*'
	p = re.compile('Q_PROPERTY\\((?P<type>' + type + ')(?P<name>\\w*)\\s*READ\\s*(?P<read>\\w*)')
	m = p.match(line)
	if not(m):
		raise BaseException('Invalid property: ' + line)
	type = m.group("type")
	name = m.group("name")
	read = m.group("read")

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
		code =  '\t' + type + 'm_' + name;
		if type.endswith('*') or type.startswith('int'):
			code += ' = 0'
		if type.startswith('bool'):
			code += ' = false'
		code += ';\n'
		if write or notify: private += code
		else: protected += code

	if not(find_start(lines, type + read + '()')):
		return_type = type; 
		if not(type.endswith('*')) and (
				type.startswith('QVariantMap') or type.startswith('QMap') or 
				type.startswith('QStringList') or type.startswith('QList')):
			print 'Modifyable property: ' + name
			return_type += "&";
		public += ('\t' + return_type + read + '() {\n' + 
				'\t\treturn m_' + name + ';\n' +
				'\t}\n')

	if write and not(find_start(lines, 'void ' + write + '(')):
		public_slots += ('\tvoid ' + write + '(' + type + name + ') {\n' +
				'\t\tm_' + name + ' = ' + name + ';\n')
		if notify:
			public_slots += '\t\temit ' + notify + '(' + name + ');\n'
		public_slots += '\t}\n'
		
	writeName = 'set' + name[0].upper() + name[1:]
	
	if not(write) and not(find_start(lines, 'void ' + writeName + '(')):
		protected += ('\tvoid ' + writeName + '(' + type + name + ') {\n' +
				'\t\tm_' + name + ' = ' + name + ';\n')
		if notify:
			protected += '\t\temit ' + notify + '(' + name + ');\n'
		protected += '\t}\n'

	if notify and not(find_start(lines, 'void ' + notify + '(')):
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
	help = ('Class Generator - Automatically generate parts of Qt classes.\n' +
			'\n' +
			'Usage: qclassgen header gen out\n' + 
			'\n' + 
			'Where the arguments are:\n' +
			'  header  The header to parse\n' +
			'  gen     The generated code, used by IDEs so it can be imported\n' +
			'  out     The finished header, with the generated code included')
	
	if len(sys.argv) == 4:
		generate()
		replace()
	else:
		print help
