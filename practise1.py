
import hashlib
import json
import datetime
from flask import Flask,jsonify
import requests
from uuid import uuid4
from urllib.parse import urlparse

# creating Block chian 

class blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        
        #genesis Block
        self.Create_Block(previous_hash = '0000',nonce = 1 )
        
        self.nodes = set()
    
    
    def Create_Block(self,previous_hash,nonce):    # creating block
        block = {
                    'index' : len(self.chain)+1,
                    'time_stamp' : str(datetime.datetime.now()),
                    'nonce' : nonce,
                    'previous_hash' :previous_hash, 
                    'transactions' : self.transactions
                 }
        self.transactions =  []     # emptying transactions after adding to block
        self.chain.append(block)
        return block;
    
    def last_block(self):          # last block of chain
        return self.chain[-1]
    
    def get_hash_of_block(self,block):
        encoded_block = str(json.dumps(block,sort_keys = True)).encode()
        
        return hashlib.sha256(encoded_block).hexdigest()
    
    def proof_of_work(self,previous_nonce):
        nonce = 1
        check_nonce = False
        
        while check_nonce is False :
            hash_operation = hashlib.sha256(str(nonce**2 - previous_nonce**2).encode()).hexdigest()
            
            if hash_operation[:4] == '0000':
                check_nonce = True
            else:
                nonce += 1
        
        return nonce        
 
        
    def chain_valid(self,chain):
        previous_block = chain[0]
        block_index = 1
        
        while block_index < len(chain):
            current_block = chain[block_index]
            
            # compare previous_hash
            if current_block['previous_hash'] != self.get_hash_of_block(previous_block) :
                return False
            
            # compare nonce 
            previous_nonce = previous_block['nonce']
            current_nonce = current_block['nonce']
            
            hash_operation = hashlib.sha256(str(current_nonce**2 - previous_nonce**2).encode()).hexdigest()
            
            if hash_operation[:4] != '0000':
                return False
            
            previous_block = current_block
            block_index += 1
         
        return True    
        
# Crypto code////////////////////////////////////////////////////

    def add_transaction(self,sender,receiver,amount):
        self.transactions.append({ 'sender' : sender , 'receiver' : receiver , 'amount' : amount})
        previous_block = self.last_block()
        return previous_block['index']+1
    
    def add_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def replace_chain(self): 
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        
        for node in network:
            response = requests.get(f'http://127.0.0.1:{node}/get_chain')
            
            if response.status_code ==200:
                 chain = response.json()['chain']
                 length = response.json()['length']
                 
                 if length > max_length and self.chain_valid(chain):
                     longest_chain = chain
                     max_length = length
                     
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
           
            


# mining Blocks

app = Flask(__name__)

node_address = str(uuid4()).replace('-','')

blockchain = blockchain()

# mine a Block

@app.route('/mine_block',methods = ['GET'])

def mine_block():
    
    previous_block = blockchain.last_block()
    previous_nonce = previous_block['nonce']
    nonce = blockchain.proof_of_work(previous_nonce)
    
    previous_hash = blockchain.get_hash_of_block(previous_block)
    blockchain.add_transaction(sender  = node_address, receiver = 'Rehan', Amount = 1 )
    
    block = blockchain.Create_Block(previous_hash,nonce)

    response = {
                   'message' : 'congrats!! Block mined!!',
                   'index' : block['index'],
                   'time_stamp' : block['time_stamp'],   
                   'nonce' : block['nonce'],
                   'previous_hash' : block['previous_hash'],
                   'transactions' : block['transactions']
                }
    return jsonify(response), 200
    
# getting blockchian
@app.route('/get_chain',methods = ['GET'])

def get_chain():
    
    response = {
                'chain' : blockchain.chain,
                'length' : len(blockchain.chain)
                }
    return jsonify(response), 200

# check for validation
    
@app.route('/is_valid', methods = ['GET'])
    
def is_valid():
    response = {
                'Block chain is :' : blockchain.chain_valid(blockchain.chain)
                }
    
    return jsonify(response), 200



# Crypto code////////////////////////////////////////////////////
    
@app.route('/connect_node', methods = ['POST'])

def connect_node():
    json = request.get_nodes()
    nodes = json.get('nodes')
    
    if nodes is None:
        return 'No nodes', 400
    
    for node in nodes:
        blockchain.add_node(node)
    
    response = { 'message' : 'All nodes are connected',
                 'total_nodes' : list(blockchain.nodes)   
                }    
        
    return jsonify(response) , 201


@app.route('/add_transactions', methods = ['POST'])

def add_transactions():
    
    json = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    
    if not all(key in json for key in transaction_keys):
        return 'some elements of transaction are missing ', 400
    index = blockchain.add_transaction(json['sender'],json['receiver'],json['amount'])
    
    response = { 'message' : f'this transaction will be added to block {index}' }

    return jsonify(response) , 201

@app.route('/replace_chain', methods = ['GET'])

def replace_chain():
    
    is_chain_replaced = blockchain.replace_chain()
    
    if is_chain_replaced:
        response = { 'message' : 'the chain is replaced by longest chain.....',
                     'chain' : blockchain.chain
                    }
    else:
        response = { 'message' : 'All good!!!!!!! you have the longest chain.....',
                     'chain' : blockchain.chain
                    }

    return jsonify(response), 200




app.run(host = '0.0.0.0',port = 5000)




