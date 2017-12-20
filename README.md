# id3translate
translate ID3 metadata

python id3translate.py -i /path/to/file.mp3

python id3translate.py -i "C:/path/to/folder with audio"

requires [python 2.7](https://www.python.org/downloads/), [ffmpeg](https://github.com/adaptlearning/adapt_authoring/wiki/Installing-FFmpeg),
[mtranslate](https://pypi.python.org/pypi?:action=display&name=mtranslate&version=1.3), [nltk](https://pypi.python.org/pypi/nltk)

nltk also requires the averaged_perceptron_tagger, download it with:

In Terminal/ cmd.exe

```python
python
>>> import nltk
>>> nltk.download('averaged_perceptron_tagger')
>>> exit()```
