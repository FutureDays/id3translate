#!/usr/bin/env python
'''
id3translate
translate id3 tags in your audio files

TO DO
utils:
require ffmpeg
wishlist:
id3OrigObj renamed with original/ API detected language, e.g. -id3-th.txt (for thai)
id3TransObj renamed with translated lagnuage, e.g. -id3-en.txt (for english)
rename files and folders with translations
overwrite option
option to not print ffmetadata1 txt files
option for quiet mode
cleanup()
'''
import io
import os
import sys
import time
import types
import argparse
import subprocess
from nltk.tag import pos_tag
from mtranslate import translate

class dotdict(dict):
	'''
    dot.notation access to dictionary attributes
    '''
	__getattr__ = dict.get
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__

def go(ffstr):
	'''
	runs ffmpeg, returns true is success, error is fail
	'''
	try:
		if os.name == 'posix':
			returncode = subprocess.check_output(ffstr, shell=True)
		else:
			returncode = subprocess.check_output(ffstr)
		return True
	except subprocess.CalledProcessError as e:
		returncode = e.returncode
        print(returncode)
        return returncode

def check_id3OrigObj(file):
    '''
    id3Check takes an input file and verifies if there is ID3 metadata already in there
    '''
    if not os.path.exists(file.id3OrigObj):
        ffstr = 'ffmpeg -i "' + file.inputFullPath + '" -f ffmetadata -y "' + file.id3OrigObj + '"'
        ffWorked = go(ffstr)
        if ffWorked is not True:
            return None
        time.sleep(1)
        b = os.path.getsize(file.id3OrigObj) #grab the size, in bytes, of the resulting text file
        if b < 55:
            os.remove(file.id3OrigObj)
            return False
        else:
            return True
    else:
        return True

def id3file_to_dict(file):
	'''
	walk line by line through each metadata element in the id3OrigObj
	'''
	tagsOrig = dotdict({})
	contents = [line.rstrip() for line in open(file.id3OrigObj) if "=" in line]
	for line in contents:
		tag, value = line.split("=")
		tagsOrig[tag] = value
	return tagsOrig

def translate_tags(args, tagsOrig):
	'''
	sends tags to google translate
	'''
	tagsTrans = ({})
	for tag, value in tagsOrig.items():
		if isinstance(value, (str,)):
			tagsTrans[tag] = translate(value, args.d, args.s)
		else:
			values = []
			for v in value:
				val = translate(v, args.d, args.s)
				values.append(val)
			tagsTrans[tag] = values
	return tagsTrans

def write_translated_id3file(file, tagsTrans):
	'''
	writes the translated tags to an ;FFMETADATA1 file
	'''
	id3file = open(file.id3TransObj,'a')
	id3file.write(";FFMETADATA1")
	for key, value in tagsTrans.items():
		id3file.write(key + "=" + value.encode('utf-8') + "\n")
	id3file.close()

def separate_properNouns(tags):
	'''
	separates proper nouns from the tag value strings
	'''
	properNouns = dotdict({})
	pnIndicies = {}
	for tag, value in tags.items():
		tagged_content = pos_tag(value.split())
		properNouns[tag] = [word for word, pos in tagged_content if pos == 'NNP']
	return properNouns

def replace_properNouns(tagsTrans, properNounsOrig, properNounsTrans):
	'''
	replaces translated proper nouns with original proper nouns
	'''
	tagsTransPNreplaced = dotdict({})
	for tag, value in tagsTrans.items():
		tagsTransPNreplaced[tag] = value
		if properNounsOrig[tag]:
			for pno in properNounsOrig[tag]:
				indx = properNounsOrig[tag].index(pno)
				pnt = properNounsTrans[tag][indx]
				something = tagsTransPNreplaced[tag].replace(pnt, pno)
				tagsTransPNreplaced[tag] = something
	return tagsTransPNreplaced

def make_trans_id3str(file):
	'''
	makes a string to write the new file
	'''
	ffstr = 'ffmpeg -i "' + file.id3TransObj + '" -i "' + file.inputFullPath + '" -c copy -write_id3v1 1 -id3v2_version 3 -y "' + file.outputFullPath + '"'
	return ffstr

def process_single_file(args, file):
	'''
	run a single file through the whole process
	'''
	id3Exists = check_id3OrigObj(file)
	if id3Exists is None:
		print('id3translate encountered an error exporting ID3 metadata from input file: ' + file.name)
		return False
	if id3Exists is False:
		print('id3translate could not locate any ID3 metadata in file: ' + file.name)
		print('please check to make sure ID3 metadata exists')
		return False
	tagsOrig = id3file_to_dict(file)
	tagsTrans = translate_tags(args, tagsOrig)
	if args.names is True:
		properNounsOrig = separate_properNouns(tagsOrig)
		properNounsTrans = translate_tags(args, properNounsOrig)
		tagsTrans = replace_properNouns(tagsTrans, properNounsOrig, properNounsTrans)
	write_translated_id3file(file, tagsTrans)
	ffstr = make_trans_id3str(file)
	ffworked = go(ffstr)
	if ffworked is not True:
		print(ffworked)
		return False
	else:
		return True

def parse_input(args):
	'''
	returns a dictionary of file attributes/ paths
	'''
	file = dotdict({})
	file.i = args.i.strip()
	file.inputFullPath = os.path.abspath(file.i)
	file.inputDir = os.path.dirname(file.inputFullPath)
	file.name, file.ext = os.path.splitext(os.path.basename(file.inputFullPath))
	if args.o is None:
		file.outputDir = file.inputDir
	else:
		file.outputDir = os.path.abspath(args.o.strip())
		if not os.path.exists(file.outputDir):
			os.makedirs(file.outputDir)
	file.outputFullPath = os.path.join(file.outputDir, file.name + "-trans" + file.ext)
	file.id3OrigObj = os.path.join(file.inputDir, file.name + '-id3-orig.txt')
	file.id3TransObj = os.path.join(file.outputDir, file.name + '-id3-trans.txt')
	return file

def init_args():
	'''
	initialize arguments from the CLI
	'''
	parser = argparse.ArgumentParser(description="translates ID3 metadata embedded in an audio file")
	parser.add_argument('-i', '--input', dest='i', help="the path to the file or folder to be translated")
	parser.add_argument('-o', '--output', dest='o', default=None, help="the output folder path for the translated files")
	parser.add_argument('-srce', '--source-language', dest='s', default=None, help="the source language (ISO 639-1), if unspecified id3translate will guess")
	parser.add_argument('-dest', '--destination-language', dest='d', default='en', help="the destination language (ISO 639-1), default is English (en)")
	parser.add_argument('--ignore-names', dest='names', action='store_true', default=False, help="don't translate words identified as proper nouns")
	args = parser.parse_args()
	return args

def main():
	'''
	do the thing
	'''
	args = init_args()
	if os.path.isfile(args.i):
		file = parse_input(args)
		processWorked = process_single_file(args, file)
		if processWorked is not True:
			print('id3translate encountered an error')
			print('id3translate is exiting...')
			sys.exit()
	elif os.path.isdir(args.i):
		for dirs, subdirs, files in os.walk(args.i):
			for f in files:
				file = parse_input(dotdict({"i":os.path.join(dirs, f), "o":args.o}))
				processWorked = process_single_file(args, file)
				if processWorked is not True:
					print('id3translate encountered an error')
					print('id3translate is exiting...')
					sys.exit()
				foo = input("Press any key to process the next file file")

if __name__ == "__main__":
    main()
