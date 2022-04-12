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

## Voting procedure
Here there will be explained the various points of a voting.

### Registration on blockchain
The registration is an important phase in which is 
decided who can vote and who can't. The list of allowed 
voters is compiled in this phase. Each single voter
must have registered inside the blockchain their EC pubkey 
along with some mandatory parameters such as displayname and 
some optional parameters which could be an unique identifier. 
To register this information to the blockchain the voter should 
sign those informations with the EC pubkey. This packet should then 
be signed by an address that is willing to pay 1eVote to 
register this information to blockchain. 
This benefactor could be the same voter or could be the 
organisation which is setting up the voting.

### Collect the voters on private platform
At this point we suggest to create a simple interface where 
you ask to proof the identity of the users and then ask to 
them to provide their public keys and craft a simple proof 
that "proofs" they own that public key (eg: they could sign 
a random message). 

### Reserve the blocks
After the list of voters is completed, the manager has to 
publicly submit all the informations about the voting. This 
information could be really big to fir in a maximum transaction 
size chunk.

The manager will send at first a transaction that includes the 
following data: preparing idle, votation lease, many partecipants, 
group size and all the hashes of the chunks of data. 
According to the information given in this transaction, the manager
will have to put in forfeit a certain amount of eVotes. Plus
the manager will have to pay as direct fee 5 eVotes for each data
chunk.

This transaction will generate a layer 2 blockchain where all the
preparing and voting will be logged. This L2 will be identified 
with the below-described transaction hash. The hash will also 
include the blocknumber. There must not exist two votings with
the same identifier. If one is presented, will be rejected.

#### Difference between fee and forfeit
The fee, for example the fee of the transaction, is a payment 
in favour of the miner that mines the block. Meanwhile a 
forfeit is an amount of eVotes taken (from the manager in this 
case) which aren't directly given to the miner.

### Push the data chunks
The data chunks of the voting informations can be sent during
the preparing idle period, starting directly from the same 
block in which the reserving transaction took place. The 
chunks don't need to be signed since the hash already is 
present on the blockchain. 

For each data chunk, depending on the information inside

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
