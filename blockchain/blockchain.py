from collections import OrderedDict
import binascii

from Cryptodome.Hash import SHA
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask,request, render_template
from flask_cors import CORS

MINING_SENDER = 'BLOCKCHAIN'
MINING_REWARD = 0.5
MINING_DIFFICULTY = 3

class Blockchain:
    def __init__(self):
        self.transactions = []
        self.chain = []
        self.nodes = set()
        self.node_id = str(uuid4()).replace('-','') # Random number to assign as node_id
        self.create_block(0,'000') # Genesis block


    def register_node(self,node_url):
        '''
        This function will add a new node to the list of nodes
        '''
        parsed_url = urlparse(node_url) # Checking if node_url has a valid format
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path) # Accepts URL without a scheme like 192.168.0.0:3000
        else:
            raise ValueError("Invalid URL")
        

    def verify_transaction_signature(self, sender_address, signature, transaction):
        '''
        Check if the signature provided by the sender corresponds to the transaction signed using public key of the sender
        '''
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        return verifier.verify(h,binascii.unhexlify(signature))
    

    def submit_transaction(self, sender_address, recipient_address, value, signature):
        '''
        Add a transaction to the transaction array if the sigature is verified
        '''
        transaction = OrderedDict({
            'sender_address':sender_address,
            'recipient_address': recipient_address,
            'value': value
        }) 

        if sender_address == MINING_SENDER:
            self.transactions.append(transaction)
            return len(self.chain)+1
        
        else:
            transaction_verification = self.verify_transaction_signature(sender_address, signature, transaction)
            if transaction_verification:
                self.transactions.append(transaction)
                return len(self.chain) + 1
            else:
                return False
            
        
    def create_block(self, nonce, previous_hash):
        '''
        Add a block of transaction to the blockchain
        '''
        block = {
            'block_number': len(self.chain)+1,
            'timestamp': time(),
            'transaction': self.transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        }

        self.transactions = [] #Reset the current transactions array after creating the block

        self.chain.append(block)
        return block
    

    def hash(self, block):
        '''
        Create a SHA-256 hash of a block
        '''
        block_string = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()
    

    def proof_of_work(self):
        '''
        Proof of work algorith
        '''
        last_block = self.chain[-1]
        last_hash = self.hash(last_block)

        nonce = 0
        while self.valid_proof(self.transactions, last_hash, nonce) is False:
            nonce += 1

        return nonce
    

    def valid_proof(self, transactions, last_hash, nonce, difficulty = MINING_DIFFICULTY):
        '''
        Validate if the hash value satisfies the mining condition.
        '''
        guess = (str(transactions)+str(last_hash)+str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:difficulty] == '0'*difficulty
    

    def valid_chain(self, chain):
        '''
        Check if the current blockchain is valid or not
        '''
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            #check if the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            
            #check if the proof of work is correct and delete the reward transaction
            transactions = block['transactions'][:-1]
            transaction_elements = ['sender_address', 'recipient_address', 'value']
            transactions = [OrderedDict((k, transaction[k]) for k in transaction_elements) for transaction in transactions]

            if not self.valid_proof(transactions, block['previous_hash'], block['nonce'], MINING_DIFFICULTY):
                return False
            
            last_block = block
            current_index += 1

        return True
    

    def resolve_conflicts(self):
        '''
        Resolving the conflicts between blockchain's nodes by replacing the current chain with the longest chian in the network
        '''
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        #verify the chains from all the nodes in the network
        for node in neighbours:
            print('http://'+node+'chain/')
            response = requests.get('http://'+node+'chain/')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

            
        #Replace the current chain with the new one if new chain is longer
        if new_chain:
            self.chain = new_chain
            return True

        return False
  



