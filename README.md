# roboh : Text Classifier

roboh is a text classifier software. 
roboh for (Review Of Books On Hypotheses) is dedicated to detect review of book on scientific article. Written in python 3, it is based on the famous scikit-learn machine learning library (http://scikit-learn.org/stable/index.html). 
roboh contains three open source independant scripts to managed the full process. The fisrt one (set_tag.py) is for import text from openedition database or from files.txt and to annotate them:
	- Annotate with Named Entity recognition (Based on the Rest API : http://nerd.readthedocs.io/en/latest/index.html)
	- Annotate with a sentiment analyser (sub-git module implemented echo: https://github.com/OpenEdition/echo) 
The second one (search_best_params) is to get the best classifier and his parameters. This process is only based on bag of words. Neither of one annotated enhancement is used. Scikit library is widely used.
The third one (cr_learning) concatenate features in a large matrix (numpy library) to train and test this classifier.


## Contributors

Mathieu Orban.

## Installation

See INSTALL.txt

## Usage

See README.txt

## Licence

roboh is released under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE

## Documentation
