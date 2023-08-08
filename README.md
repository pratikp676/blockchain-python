# Overview:
The github repository includes a Python-based basic implementation of a blockchain and its client. This blockchain includes the following features:

- The ability to add extra nodes to the blockchain

- Proof of Work (PoW)

- Simple node conflict resolution

- RSA encrypted transactions

## Instructions to run the code:
1. Install all the dependancy using below command.
```
pip install -r requirements.txt
```
2. To start a blockchain node, navigate to the `blockchain` folder and run the following command: 
```
python blockchain.py -p 5000
```
3. By using the same command and a port that is not already in use, you can add a new node to the blockchain.
For example,
```
python blockchain.py -p 5001
```
4. To launch the blockchain client, navigate to the `client` folder and run the following command:
```
python blockchain_client.py -p 8080
```
5. By visiting to localhost:5000 and localhost:8080 in your browser, you can access the blockchain frontend and blockchain client dashboards.