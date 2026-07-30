from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware #Necessary for POA chains
from datetime import datetime
from pathlib import Path
import json
import pandas as pd


def connect_to(chain):
    if chain == 'source':  # The source contract chain is avax
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet

    if chain == 'destination':  # The destination contract chain is bsc
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet

    if chain in ['source','destination']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the poa compatibility middleware to the innermost layer
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def get_contract_info(chain, contract_info):
    """
        Load the contract_info file into a dictionary
        This function is used by the autograder and will likely be useful to you
    """
    try:
        with open(contract_info, 'r')  as f:
            contracts = json.load(f)
    except Exception as e:
        print( f"Failed to read contract info\nPlease contact your instructor\n{e}" )
        return 0
    return contracts[chain]



def scan_blocks(chain, contract_info="contract_info.json"):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    # This is different from Bridge IV where chain was "avax" or "bsc"
    if chain not in ['source','destination']:
        print( f"Invalid chain: {chain}" )
        return 0
    
        #YOUR CODE HERE
    # Load private key from sk.txt
    cur_dir = Path(__file__).parent.absolute()
    with open(cur_dir.joinpath('sk.txt'), 'r') as f:
        private_key = f.readline().rstrip()
    if private_key[:2] == "0x":
        private_key = private_key[2:]

    # Connect to the chain being scanned
    w3 = connect_to(chain)
    contracts = get_contract_info(chain, contract_info)
    contract_address = contracts['address']
    abi = contracts['abi']
    contract = w3.eth.contract(address=contract_address, abi=abi)
    account = w3.eth.account.from_key(private_key)

    # Scan last 5 blocks
    end_block = w3.eth.get_block_number()
    start_block = end_block - 5
    print(f"Scanning blocks {start_block} - {end_block} on {chain}")

    if chain == 'source':
        # Use get_logs instead of create_filter
        events = contract.events.Deposit.get_logs(
            from_block=start_block,
            to_block=end_block
        )

        if events:
            dest_w3 = connect_to('destination')
            dest_info = get_contract_info('destination', contract_info)
            dest_contract = dest_w3.eth.contract(
                address=dest_info['address'],
                abi=dest_info['abi']
            )
            dest_account = dest_w3.eth.account.from_key(private_key)

            for evt in events:
                token = evt.args['token']
                recipient = evt.args['recipient']
                amount = evt.args['amount']
                print(f"Deposit found: token={token}, recipient={recipient}, amount={amount}")

                tx = dest_contract.functions.wrap(token, recipient, amount).build_transaction({
                    'from': dest_account.address,
                    'nonce': dest_w3.eth.get_transaction_count(dest_account.address),
                    'gas': 300000,
                    'gasPrice': dest_w3.eth.gas_price,
                })
                signed_tx = dest_w3.eth.account.sign_transaction(tx, private_key=private_key)
                tx_hash = dest_w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                dest_w3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"wrap() called on destination, tx hash: {tx_hash.hex()}")

    elif chain == 'destination':
        # Use alternative BSC RPC that supports get_logs
        bsc_w3 = Web3(Web3.HTTPProvider("https://bsc-testnet-rpc.publicnode.com"))
        bsc_w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        dest_contract = bsc_w3.eth.contract(address=contract_address, abi=abi)

        try:
            events = dest_contract.events.Unwrap.get_logs(
                from_block=start_block,
                to_block=end_block
            )
        except Exception as e:
            print(f"get_logs failed: {e}")
            events = []

        if events:
            src_w3 = connect_to('source')
            src_info = get_contract_info('source', contract_info)
            src_contract = src_w3.eth.contract(
                address=src_info['address'],
                abi=src_info['abi']
            )
            src_account = src_w3.eth.account.from_key(private_key)

            for evt in events:
                underlying_token = evt.args['underlying_token']
                recipient = evt.args['to']
                amount = evt.args['amount']
                print(f"Unwrap found: token={underlying_token}, recipient={recipient}, amount={amount}")

                tx = src_contract.functions.withdraw(underlying_token, recipient, amount).build_transaction({
                    'from': src_account.address,
                    'nonce': src_w3.eth.get_transaction_count(src_account.address),
                    'gas': 300000,
                    'gasPrice': src_w3.eth.gas_price,
                })
                signed_tx = src_w3.eth.account.sign_transaction(tx, private_key=private_key)
                tx_hash = src_w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                src_w3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"withdraw() called on source, tx hash: {tx_hash.hex()}")