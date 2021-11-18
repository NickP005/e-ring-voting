# e-ring-voting
USE THIS AS YOUR RISK. THIS IS A CODE THAT'S BEING STILL WRITTEN
This is demonstration voting system based on blockchain technology written by @NickP005 and @lindaniele

## Abstract
Currently electronic voting made in many countries such as Brazil flowered. 
Electronic voting that uses black boxes that require to be trusted is itself dangerous and susceptible to fraud.
In countries such Brazil they require the voter to trust the vote will be counted and that their identity will not be 
associated with their vote. This is not admissible for a vote. 
This project aims to make a public system that can be verified by anyone for electronic voting based on blockchain
where anonymity is a must. 

The blockchain will have a currency that will be given with a fixed reward of 900eVotes for each block. 
Half of each fee will be given to the miner. 

### Voting procedure - start
A manager is a person that starts a vote.
To start a vote the manager needs X eVote.
For every transaction there is a fixed fee of 1eVote. 
To prepare a vote the manager needs to submit a special transaction.
In that special transaction the manager needs to specify the public addresses of who can vote, the options that can be voted, a voting message, members per group and a range that specifies how much the voting lasts;
the range has a start (expressed in block number) and a finish (expressed in a block number).
The fee of the special transaction is calculated from:
1 fixed eVote + (members \* members_per_group) + 10 \* range_of_blocks

### Voting procedure - voter set up
#### The Interface
One important point of failure of the system is the 
user's interface. The interface will need to be as
intuitive and complete as possible since not everyone
is a computer expert. 

#### Registration
Through the interface the voter will generate a private/public 
keypair of normal elliptic curve cryptography. Then
the voter exports the public key and sends it 
to the database of the manager (while sending also 
proofs of the identity). Meanwhile the voter 
has to get 1 eVote currency on the public key 
balance to keep it in the ledger and sign a 
special transaction to set their public name of
maximum 32 ascii characters. 

### Voting procedure - voting phase
After the public voting list has been published along
with the details required the voter will see
a vote permission alongside with the voting id 
that is the hash of the special transaction that
started the voting. \n
So the voter now reads the in-blockchain vote 
prompt and expresses anonymously their vote.

### Voting procedure - counting the result
When the voting ends every node computes 
the votes and determines the exit of the
democratic vote. Every client that partecipated
can choose to review who voted and count the votes
themselves. Plus can verify if the vote ended up
in the final counting.
