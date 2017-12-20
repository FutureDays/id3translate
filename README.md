# id3translate
translate ID3 metadata

python id3translate.py -i /path/to/file.mp3

python id3translate.py -i "C:/path/to/folder with audio"

## Installation

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
