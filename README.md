# id3translate
translate ID3 metadata

## Usage

Open Terminal/ cmd.exe and navigate to the folder with id3translate.py, e.g. `cd C:/Users/person/Desktop/id3translate`

Or, alternatively, add the folder to your PATH: [Windows](https://superuser.com/questions/949560/how-do-i-set-system-environment-variables-in-windows-10) | [Mac](https://stackoverflow.com/questions/14637979/how-to-permanently-set-path-on-linux-unix)

Then, again in Terminal/ cmd.exe, type the following and hit Enter

`python id3translate.py -i /path/to/file.mp3`

`python id3translate.py -i "C:/path/to/folder with audio"`

Type `python id3translate.py -h` for help

## Installation

git clone or download the id3translate.zip and extract somewhere

requires:

#### [ffmpeg](https://github.com/adaptlearning/adapt_authoring/wiki/Installing-FFmpeg)

(see instructions for install)

#### [python](https://www.python.org/downloads/)

(has an installer)

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
>>> exit()```
