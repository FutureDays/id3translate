# id3translate
translate ID3 metadata

## Usage

in Terminal/ cmd.exe, type the following and hit Enter

`python id3translate.py -i /path/to/file.mp3`

`python id3translate.py -i "C:/path/to/folder with audio"`

Type `python id3translate.py -h` for help

### Options

-i input | required, the input file or path to files. enclose filepaths with spaces in quotes ("")

-o output | optional, the output path where you want the translated files to be written. defaults to input path. files are renamed name-trans.ext, so nothing is overwritten (overwriting option coming soon!)

-srce --source-language | optional, the source language of the tags that you want to translate. if not specified, id3translate/ google translate will take its best guess

-dest --destination-language | optional, the destination language of the tags that you want to translate. if not specified, id3translate/ google translate will translate into English

-p --print | optional, print sidecar ;FFMETADATA1 text files. Default is off. id3translate will automatically create ;FFMETADATA1
files for each input, but will delete them after the tags have been translated

--ignore-names | optional, id3translate will use nltk's Part Of Speech tagger to guess at proper nouns and omit them in the translation. default will translate the proper nouns

--filenames-mode | optional, choose between: translate, which translates the input filename; rename, which renames the input filename with the Title tag; or None, which appends "-trans" to the input filename

## Installation

git clone or download the id3translate.zip and extract somewhere

Open Terminal/ cmd.exe and navigate to the folder with id3translate.py, e.g. `cd C:/Users/person/Desktop/id3translate`

Or, alternatively, add the folder to your PATH: [Windows](https://superuser.com/questions/949560/how-do-i-set-system-environment-variables-in-windows-10) | [Mac](https://stackoverflow.com/questions/14637979/how-to-permanently-set-path-on-linux-unix)

also requires:

#### [ffmpeg](https://github.com/adaptlearning/adapt_authoring/wiki/Installing-FFmpeg)

(see instructions for install)

#### [python](https://www.python.org/downloads/)

(has an installer. default branch is python2)

### Python libs

#### [mtranslate](https://pypi.python.org/pypi?:action=display&name=mtranslate&version=1.3)

install by typing, in Terminal/ cmd.exe `pip install mtranslate` and hit enter

#### [nltk](https://pypi.python.org/pypi/nltk)
install by typing, in Terminal/ cmd.exe `pip install nltk` and hit enter

nltk also requires the averaged_perceptron_tagger, download it by:

In Terminal/ cmd.exe

```python
python
>>> import nltk
>>> nltk.download('averaged_perceptron_tagger')
>>> exit()
```
