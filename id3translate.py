'''
id3translate
translate id3 tags in your audio files
'''
import os
import sys
import time
import argparse
import subprocess

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
            print 'id3translate encountered an error exporting ID3 metadata from input file: ' + file.name
            print 'id3translate is exiting...'
            return False
        time.sleep(1)
        b = os.path.getsize(file.id3OrigObj) #grab the size, in bytes, of the resulting text file
        if b < 55:
            os.remove(file.id3OrigObj)
            return None
        else:
            return True
    else:
        return True

def process_single_file(file):
    '''
    run a single file through the whole process
    '''
    check_id3OrigObj(file)
    return True

def parse_input():
    '''
    returns a dictionary of file attributes/ paths
    '''
    file = dotdict({})
    file.i = args.i.strip()
    file.inputFullPath = os.path.abspath(file.i)
    file.inputDir = os.path.dirname(file.inputFullPath)
    file.name, file.ext = os.path.splitext(os.path.basename(file.inputFullPath))
    file.outputDir = os.path.abspath(args.o.strip())
    file.outputFullPath = os.path.join(file.outputDir, file.name + file.ext)
    file.id3OrigObj = os.path.join(file.inputDir, file.name + '-id3-orig.txt')
    file.id3TransObj = os.path.join(file.outputDir, file.name + '-id3-trans.txt')
    return file


def init_args():
    '''
    initialize arguments from the CLI
    '''
    global args
    parser = argparse.ArgumentParser(description="translates ID3 metadata embedded in an audio file")
    parser.add_argument('-i', '--input', dest='i', help='the path to the file or folder to be translated')
    parser.add_argument('-o', '--output', dest='o', default=os.getcwd(), help='the output folder path for the translated files')
    args = parser.parse_args()

def main():
    '''
    do the thing
    '''
    init_args()
    if os.path.isfile(args.i):
        file = parse_input()
        processWorked = process_single_file(file)
        if processWorked is not True:
            print 'id3translate encountered an error'
            sys.exit()

if __name__ == "__main__":
    main()
