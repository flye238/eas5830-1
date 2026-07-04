from web3 import Web3
from web3.providers.rpc import HTTPProvider
import requests
import json

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.to_checksum_address(bayc_address)

# You will need the ABI to connect to the contract
# The file 'abi.json' has the ABI for the bored ape contract
# In general, you can get contract ABIs from etherscan
# https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('ape_abi.json', 'r') as f:
    abi = json.load(f)

############################
# Connect to an Ethereum node
api_url = "https://mainnet.infura.io/v3/e9a06032d664479ab1ffeba3fd821e4f"  # YOU WILL NEED TO PROVIDE THE URL OF AN ETHEREUM NODE
provider = HTTPProvider(api_url)
web3 = Web3(provider)


def get_ape_info(ape_id):
    assert isinstance(ape_id, int), f"{ape_id} is not an int"
    assert 0 <= ape_id, f"{ape_id} must be at least 0"
    assert 9999 >= ape_id, f"{ape_id} must be less than 10,000"

    data = {'owner': "", 'image': "", 'eyes': ""}

    # YOUR CODE HERE
    contract = web3.eth.contract(address=contract_address, abi=abi)
 
    # Get the current owner from the chain
    owner = contract.functions.ownerOf(ape_id).call()
    data['owner'] = owner
 
    # Get the tokenURI from the chain
    token_uri = contract.functions.tokenURI(ape_id).call()
 
    # Convert to an https gateway URL
    ipfs_path = token_uri.replace("ipfs://", "")
    gateway_url = f"https://ipfs.io/ipfs/{ipfs_path}"
 
    response = requests.get(gateway_url)
    metadata = response.json()
 
    # Pull out the image URI directly
    data['image'] = metadata['image']
 
    # The "eyes" trait lives inside the attributes list, keyed by trait_type
    for attribute in metadata['attributes']:
        if attribute['trait_type'] == 'Eyes':
            data['eyes'] = attribute['value']
            break

    assert isinstance(data, dict), f'get_ape_info{ape_id} should return a dict'
    assert all([a in data.keys() for a in
                ['owner', 'image', 'eyes']]), f"return value should include the keys 'owner','image' and 'eyes'"
    return data
