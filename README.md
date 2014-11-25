project-platypus
================

## Useful commands

    match (w:Word)-[h:HEARD]-(p:Person) where h.frequency > 20 return w.value, h.frequency, h.name, p.address

## TODO for loader
+ Get rid of active = True in word
+ Get rid of frequency in fetching heards
+ Get rid of category in fetching relations

## Classification 11/24/14
Total database stats:
+ Total messages: 19921
+ Total unique words: 38969
+ Total communicated words: 2146932

Classified person stats:
+ Person: "hayk martirosyan <hayk@stanford.edu>"
+ Messages involving person: 1934
+ Total communicated words involving person: 87626
+ Total # people communicated with: 343

Preparation:
+ min_freq = 5
+ stdev_weight = 6
+ training set fraction = 0.7

##### Naive Bayes:
    
    Results:
    
      Relation 1:
          Correct: 38
        Incorrect: 13
      Relation 3:
          Correct: 41
        Incorrect: 11
    
    Total # of classifications: 103
    # correct classifications: 79
    # incorrect classifications: 24
    
    Error rate: 0.23300970873786409

##### Linear SVC:

    Results:
    
      Relation 1:
          Correct: 35
        Incorrect: 18
      Relation 3:
          Correct: 36
        Incorrect: 14
    
    Total # of classifications: 103
    # correct classifications: 71
    # incorrect classifications: 32
    
    Error rate: 0.3106796116504854
