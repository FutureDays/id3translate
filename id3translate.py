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
option for quiet mode
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
	except subprocess.CalledProcessError, e:
		returncode = e.returncode
        print returncode
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
	tagsTrans = dotdict({})
	for tag, value in tagsOrig.iteritems():
		if isinstance(value, types.StringTypes):
			tagsTrans[tag] = translate(value, args.d, args.s)
		else:
			values = []
			for v in value:
				val = translate(v, args.d, args.s)
				values.append(val)
			tagsTrans[tag] = values
	return tagsTrans

def separate_properNouns(tags):
	'''
	separates proper nouns from the tag value strings
	'''
	properNouns = dotdict({})
	pnIndicies = {}
	for tag, value in tags.iteritems():
		tagged_content = pos_tag(value.split())
		properNouns[tag] = [word for word, pos in tagged_content if pos == 'NNP']
	return properNouns

def replace_properNouns(tagsTrans, properNounsOrig, properNounsTrans):
	'''
	replaces translated proper nouns with original proper nouns
	'''
	tagsTransPNreplaced = dotdict({})
	for tag, value in tagsTrans.iteritems():
		tagsTransPNreplaced[tag] = value
		if properNounsOrig[tag]:
			for pno in properNounsOrig[tag]:
				indx = properNounsOrig[tag].index(pno)
				pnt = properNounsTrans[tag][indx]
				something = tagsTransPNreplaced[tag].replace(pnt, pno)
				tagsTransPNreplaced[tag] = something
	return tagsTransPNreplaced

def make_trans_id3str(file, tagsTrans):
	'''
	makes a string to write the new file
	'''
	mtdstr = ''
	for tag, value in tagsTrans.iteritems():
		mtdstr = mtdstr + ' -metadata ' + tag + '="' + value + '"'
	ffstr = 'ffmpeg -i "' + file.inputFullPath.decode('utf-8') + '" -c copy ' + mtdstr + ' -write_id3v1 1 -id3v2_version 3 -y "' + file.outputFullPath + '"'
	#ffstr = 'ffmpeg -i "foobar.mp3" -c copy ' + mtdstr + ' -write_id3v1 1 -id3v2_version 3 -y "' + file.outputFullPath + '"'
	#ffstr = 'ffmpeg -i "' + file.inputFullPath + '" -c copy ' + mtdstr + ' -write_id3v1 1 -id3v2_version 3 -y "foobar.mp3"'
	return ffstr

def rename(file, tagsTrans):
	'''
	renaming logic for the file, based on translating from title tag
	'''
	if tagsTrans.title:
		file.outputFullPath = os.path.join(file.outputDir, tagsTrans.title + file.ext)
		file.id3TransObj = os.path.join(file.outputDir, tagsTrans.title + file.ext)
		file = output_duplicate_check(file)
	return file

def output_duplicate_check(file):
	'''
	checks if there's a duplicate filepath present in destination, prefixes 01- to file.name
	'''
	count = 1
	fbasename = os.path.basename(file.outputFullPath)
	id3basename = os.path.basename(file.id3TransObj)
	while os.path.exists(file.outputFullPath) or os.path.exists(file.id3TransObj):
		if count < 10:
			strcount = "0" + str(count) + "-"
		else:
			strcount = str(count) + "-"
		file.outputFullPath = os.path.join(file.outputDir, strcount + fbasename)
		file.id3TransObj = os.path.join(file.outputDir, strcount + id3basename)
		count = count + 1
		print file.outputFullPath
		foo = raw_input("eh")
	return file

def write_translated_id3file(file, tagsTrans):
	'''
	writes the translated tags to an ;FFMETADATA1 file
	'''
	id3file = open(file.id3TransObj,'a')
	id3file.write(";FFMETADATA1")
	for key, value in tagsTrans.iteritems():
		id3file.write(key + "=" + value + "\n")
	id3file.close()

def cleanup(args, file, tagsTrans):
	'''
	handles printing/ deleting/ renaming things
	'''
	if args.p:
		write_translated_id3file(file, tagsTrans)
	else:
		os.remove(file.id3OrigObj)

def process_single_file(args, file):
	'''
	run a single file through the whole process
	'''
	id3Exists = check_id3OrigObj(file)
	if id3Exists is None:
		print 'id3translate encountered an error exporting ID3 metadata from input file: ' + file.name
		return False
	if id3Exists is False:
		print 'id3translate could not locate any ID3 metadata in file: ' + file.name
		print 'please check to make sure ID3 metadata exists'
		return False
	tagsOrig = id3file_to_dict(file)
	tagsTrans = translate_tags(args, tagsOrig)
	if args.names is True:
		properNounsOrig = separate_properNouns(tagsOrig)
		properNounsTrans = translate_tags(args, properNounsOrig)
		tagsTrans = replace_properNouns(tagsTrans, properNounsOrig, properNounsTrans)
	if args.fnames == 'rename':
		file = rename(file, tagsTrans)
	ffstr = make_trans_id3str(file, tagsTrans)
	ffworked = go(ffstr)
	if ffworked is not True:
		print ffworked
		return False
	else:
		cleanup(args, file, tagsTrans)
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
	if args.fnames == 'translate':
		f = translate_tags(args, dotdict({'name':file.name}))
		file.outputFullPath = os.path.join(file.outputDir, f.name + file.ext)
		file.id3OrigObj = os.path.join(file.inputDir, file.name + '-id3.txt')
		file.id3TransObj = os.path.join(file.outputDir, f.name + '-id3.txt')
	print args.fnames is False
	print args
	print file.outputFullPath == file.inputFullPath
	if args.fnames is None or args.fnames == 'rename' or file.outputFullPath == file.inputFullPath:
		file.outputFullPath = os.path.join(file.outputDir, file.name + "-trans" + file.ext)
		file.id3OrigObj = os.path.join(file.inputDir, file.name + '-id3-orig.txt')
		file.id3TransObj = os.path.join(file.outputDir, file.name + '-id3-trans.txt')
	file = output_duplicate_check(file)
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
	parser.add_argument('-p', '--print', dest='p', action='store_true', default=False, help="print sidecar ;FFMETADATA1 text files, default is False")
	#parser.add_argument('--translate-filenames', dest='fnames', action='store_true', default=False, help="don't translate filenames, default will translate")
	parser.add_argument('--ignore-names', dest='names', action='store_true', default=False, help="don't translate words identified as proper nouns, default will translate")
	parser.add_argument('--filenames-mode', dest='fnames', choices=['translate','rename', None], const=None, nargs='?', help="filenames mode, translate will translate the input directly, rename will rename output file with translated Title tag. default leaves original names")
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
			print 'id3translate encountered an error'
			print 'id3translate is exiting...'
			sys.exit()
	elif os.path.isdir(args.i):
		for dirs, subdirs, files in os.walk(args.i):
			for f in files:
				if not f.startswith ('.'):
					file = parse_input(dotdict({"i":os.path.join(dirs, f), "o":args.o}))
					processWorked = process_single_file(args, file)
					if processWorked is not True:
						print 'id3translate encountered an error'
						print 'id3translate is exiting...'
						sys.exit()
					foo = raw_input("Press any key to process the next file file")
	else:
		print "id3translate could not locate the file or folder specified"
		print "or, the file is of an unknown type"
		print "please check the file/ folder path and try again"
		print 'id3translate encountered an error'
		print 'id3translate is exiting...'
		sys.exit()

if __name__ == "__main__":
    main()
