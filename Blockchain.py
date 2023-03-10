
# coding: utf-8

# In[39]:


from hashlib import sha256
import json
import time
import copy

from flask import Flask, request, render_template, jsonify
import requests


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

    def info(self):
        """
        A function that return the  block contents.
        """
        return json.dumps(self.__dict__, sort_keys=True)
		
    def __repr__(self):
        return "{} - {} - {} - {} - {} - {}".format(self.index, self.previous_hash, self.transactions, self.timestamp, self.nonce, self.hash )
    def __str__(self):
        return "{} - {} - {} - {} - {} - {}".format(self.index, self.previous_hash, self.transactions, self.timestamp, self.nonce, self.hash )

class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 3

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
		#genesis_block.hash = self.proof_of_work(genesis_block)
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    def proof_of_work(self, block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        t = time.time()
        t_ms = int(t * 1000)
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)

        self.unconfirmed_transactions = []
        t = time.time()
        dt = int(t * 1000) - t_ms
        print("Time used to mine the block [ms]: ",dt)
        return new_block.index
		
    # Get the Blockchain information
    def get_chain(self):
        chain_data = []
        for block in self.chain:
            chain_data.append(block.__dict__)
        return chain_data

	# Validate the Blockchain 
    def validate_chain(self):
        valid = True
        previous_hash = "0"
        for block in self.chain:
            #print("Block index ", block.index)
            #print("Block nonce ", block.nonce)
            #print("Block previous_hash: ", block.previous_hash)
            #print("Block hash: ", block.hash)
            #print("Block info(): ", block.info())
            current_hash = block.hash

            # Make a copy of block and remove the hash from the block
            block2 = copy.deepcopy(block)
            if 'hash' in block2.__dict__:
                del block2.__dict__['hash']
            #print("Block2 compute_hash(): ", block2.compute_hash())
            #print("Block2 info(): ", block2.info())
            if previous_hash !=block.previous_hash:
                valid = False
                print("Error 1 ...............")
            if block.index > 0:
              if current_hash.startswith('0' * Blockchain.difficulty)!= True:
                  valid = False
                  print("Error 2 ...............")
            if current_hash != block2.compute_hash():
                valid = False
                print("Error 3 ...............")
            previous_hash = current_hash
        return valid
		
app = Flask(__name__)
blockchain = Blockchain()
print(blockchain)
print(repr(blockchain))


# In[41]:

@app.route('/')
def index():
    text = '''
	<html>
      <head>
          <link rel="stylesheet" href="{{ url_for('static', filename= 'css/style.css') }}">      
	  </head>
	  <body>
	    <h1>Welcome to Python Blockchain Demo!</h1>
	       Click <a href="/chain">Chain</a> to view the blockchain.<br><br>
	       Click <a href="/trans">Transactions</a> to add transactions and mine the blockchain.<br><br> 	
	       Click <a href="/result">Chain</a> to view the blockchain in a table format.<br><br>
	       Click <a href="/validate">Validate</a> to validate the blockchain.<br><br>
	  </body>
	</html>
	'''
    return text
	
#def hello():
#    text = '''
#	 <h1>Welcome to Python Blockchain Demo!</h1>
#	 Click <a href="/chain">Chain</a> to view the blockchain.<br><br>  
#    <label for="name">Transactions:</label>
#	 <form method="POST" action="/mine">
#    <label for="name">Transaction 1:</label>
#    <input type="text" id="transaction1" name="transaction1" size="20"><br>   	
#    <label for="name">Transaction 2:</label>
#    <input type="text" id="transaction2" name="transaction2" size="20"><br>      	
#    <label for="name">Transaction 3:</label>
#    <input type="text" id="transaction3" name="transaction3" size="20"><br> 
#    <input type="submit" value="Add Transactions and Mine the Blockchain">	
#    </form>	
#	
#	'''
#    return text	

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
#    print("block data [0]....")
#    print(type(chain_data[0]))
#    print(chain_data[0])
#    for key,value in chain_data[0].items():
#        print(key)
#        print(value)

	
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})

@app.route('/trans', methods=['GET'])
def trans():
    return render_template('transactions.html')
	
@app.route('/mine', methods=['GET', 'POST'])
def mine():
    # Add some transactions and mine the block ====================
	transaction = request.form.get('transaction1')
#	print(type(transaction))
#	print(transaction)
	blockchain.add_new_transaction(transaction)
	transaction = request.form.get('transaction2')
	blockchain.add_new_transaction(transaction)
	transaction = request.form.get('transaction3')
	blockchain.add_new_transaction(transaction)
	blockchain.mine()
	return get_chain()

@app.route('/result')
def result():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
#    dict = {'phy':50,'che':60,'maths':70}
    dict = chain_data
    return render_template('result.html', results = dict)

@app.route('/validate')
def validate():
    val = True
    val = blockchain.validate_chain()
    if val:	  
        return "Blockchain is valid!"
    else:
        return "Blockchain is NOT valid!"

# In[45]:



app.run(debug=True, port=5000)

