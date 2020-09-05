https://lomanlab.github.io/mockcommunity/mc_databases.html

* x = masked
* o = not masked

Library       | Standard | Mini | Loman microbial | Loman maxi
------------- | -------- | ---- | --------------- | ----------
archaea       |   x      | x    | x               | x
bacteria      |   x      | x    | x               | x
viral         |   x      | x    | x               | x
plasmid       |          | x    |                 |  
human         |   o      | x    |                 | x
UniVec        |          | x    |                 | 
UniVec_Core   |   x      |      | x               |
protozoa      |          |      | x               | x
fungi         |          |      | x               | x
plant         |          |      |                 | 
nt            |          |      |                 |
nr            |          |      |                 |



PROPOSED NEW SET OF INDEXES:

Note: Any of these could have a "mini" version, which will
always be built from identical libraries.

Library     | Base      | Plus-pf  | Plus-pfp
----------- | --------- | -------- | ----------
archaea     |   x       | x        | x
bacteria    |   x       | x        | x
viral       |   x       | x        | x
plasmid     |   x       | x        | x
human       |   o       | o        | o
UniVec_Core |   x       | x        | x
protozoa    |           | x        | x
fungi       |           | x        | x
plant       |           |          | x
nt          |           |          |
nr          |           |          |
