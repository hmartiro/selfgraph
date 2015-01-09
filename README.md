selfgraph
=========
Selfgraph builds a social graph of your own personal network from your
communications with others, and applies machine learning techniques to
provide insights about your network.

![Word Node Subgraph](documents/fig-1-screenshot.png?raw=true)

You input bulk email, SMS, or
WhatsApp data, and selfgraph constructs a complex graph database of your
interactions with others. Selfgraph provides visualizations and algorithms
to gain insights about your own personal network. It can classify who your
friends are, cluster your contacts into groups, and tell you how your
vocabulary tends to shift when speaking with different groups.

Critically, selfgraph is fully free and open source. Since it runs
locally and makes no network connections whatsoever, you can trust it with
any of your data, without worries of it being stored or sold. Selfgraph can also
do more computationally intense calculations per-person than a server could,
because it runs entirely on your machine. This means that unlike
[Immersion](https://immersion.media.mit.edu/) from the MIT Media Lab, we
process the full content of your communications, not just
the metadata. We feed every individual word communicated into our graph.

Selfgraph is written in Python 3, and uses the [neo4j](http://neo4j.com/)
graph database, the [scikit-learn](http://scikit-learn.org/) machine
learning package, and the [nltk](http://www.nltk.org/) NLP library.

Note: Selfgraph is a command-line tool and pre-alpha.
Contact the authors if you are interested.

### Paper
Selfgraph started as a final project for
[CS 229](http://cs229.stanford.edu/schedule.html) at Stanford, taught by
[Andrew Ng](http://en.wikipedia.org/wiki/Andrew_Ng). Our goal was to
predict relationships between a person and their contacts using a
bag-of-words model of their email data. Using a binary friend vs acquaintance
classification, we were able to achieve under 6% error on a sample set of
3000 emails and 309 contacts, using 10-fold cross validation.

Our full technical report is located
[here](documents/Ryan Houlihan, Hayk Matirosyan, Constructing Personal Networks Through Communication History.pdf?raw=true),
with the following abstract:

	This study aims to predict a user's relationships with his or her contacts
	based solely on the words used in electronic communications between them.
	Software was created that reads in bulk exported email data and builds a
	comprehensive graph database of people, the words communicated between them,
	and their relationships to each other. Several stages of preprocessing and
	feature selection were applied, and then various classifiers were shown to
	effectively predict relationships using 10-fold cross validation. Logistic
	regression showed 5.9% testing error on a sample set of 3000 emails and 309
	contacts. The study shows promising results and suggests future work that
	incorporates message meta-data, other mediums of communication like text
	messaging, and larger data sets to further improve accuracy.
