#!/usr/bin/python

import re
import os
import shutil
import argparse
from zipfile import ZipFile
from tempfile import mkdtemp


files = {}

def banned(entry):
	ban_list = [r'.*__MACOSX/.*', r'.*\.DS_Store.*']
	for word in ban_list:
		if re.match(word, entry):
			return True
	return False
	
def on_student_list(entry, student_pattern):
	match = student_pattern.search(entry)
	if match:
		#print 'Found CaseID: %s' % match.group(0)
		return match.group(0)
	return False	
	
def extract_zip2(caseid, filename):
	file_list = []
	
	input_file = ZipFile(filename, 'r')
	for zipped_file in input_file.namelist():
		if not banned(zipped_file):
			zipped_filename = zipped_file
			if zipped_filename.startswith('\\') or zipped_filename.startswith('/'):
				zipped_filename = zipped_filename[1:]
			if zipped_filename.endswith('/'):
				print 'This is a folder: %s' % zipped_filename
				os.makedirs(os.path.join(os.path.dirname(filename), zipped_filename))	
			else:
				print 'Extract Filename: %s, Zipped Filename: %s' % (os.path.dirname(filename), os.path.basename(zipped_filename))
				filename = os.path.join(os.path.dirname(filename), os.path.basename(zipped_filename))
				file_list.append(filename)
				output_file = open(filename, 'w')
				zipped_file_obj = input_file.open(zipped_file)
				shutil.copyfileobj(zipped_file_obj, output_file)
			
	return file_list	
	
def prepare(input_file, output_dir, student_list):
	if not os.path.isdir(output_dir):
		os.mkdir(output_dir)
	
	students = open(student_list, 'r')
	students = students.read().splitlines()
	student_pattern = ''
	for id in students:
		 student_pattern = student_pattern + id + '|'
	student_pattern = student_pattern[:-1] + ''
	print 'Pattern To Match: %s' %student_pattern	 
	student_pattern = re.compile(student_pattern)
	
	tmp_path = mkdtemp()
	print 'Creating /tmp/ folder: %s' % tmp_path
	input_zip = ZipFile(input_file, 'r')	
	for entry in input_zip.namelist():
		if entry.endswith('.zip'):
			caseid = on_student_list(entry, student_pattern)
			if caseid:
				if caseid not in files:
					files[caseid] = []
				files[caseid].append(os.path.join(tmp_path, entry))
				input_zip.extract(entry, tmp_path)
				
	for caseid in files.iterkeys():
		if not os.path.isdir(os.path.join(output_dir, caseid)):
			os.mkdir(os.path.join(output_dir, caseid))
			
		while files[caseid]:
			filename = files[caseid].pop()
			print 'Filename: %s' % filename
			if filename.endswith('.zip'):
				files[caseid] = files[caseid] + extract_zip2(caseid, filename)
			else:
				shutil.copy2(filename, os.path.join(output_dir, caseid))
										
def parse():
	parser = argparse.ArgumentParser(description='Processes BB Files')
	parser.add_argument('input_file', metavar='input_file', help='Input file to process')
	parser.add_argument('output_dir', metavar='output_dir', help='Directory to output to')
	parser.add_argument('--list', dest='student_list', default='students', help='List of student ids to process')

	args = parser.parse_args()

	prepare(args.input_file, args.output_dir, args.student_list)			
if __name__ == '__main__':			
	parse()
