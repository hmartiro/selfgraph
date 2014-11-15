project-platypus
================


## Useful commands

    match (w:Word)-[h:HEARD]-(p:Person) where h.frequency > 20 return w.value, h.frequency, h.name, p.address
