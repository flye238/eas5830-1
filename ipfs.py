import requests
import json

PINATA_API_KEY = "a66c009f1dfb9526919b"
PINATA_API_SECRET = "2fbc0f374e50d6ba358cc1b56bfa6a98a3147abfe6069fdf14b958e3141ba590"

def pin_to_ipfs(data):
    assert isinstance(data, dict), f"Error pin_to_ipfs expects a dictionary"
    
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_API_SECRET,
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        headers=headers,
        json=data
    )
    
    assert response.status_code == 200, f"Failed to pin to IPFS: {response.text}"
    
    cid = response.json()["IpfsHash"]
    return cid


def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), f"get_from_ipfs accepts a cid in the form of a string"
    
    url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    response = requests.get(url)
    
    assert response.status_code == 200, f"Failed to get from IPFS: {response.text}"
    
    data = response.json()
    
    assert isinstance(data, dict), f"get_from_ipfs should return a dict"
    return data


if __name__ == "__main__":
    test_data = {"test": "hello"}
    cid = pin_to_ipfs(test_data)
    print(f"Pinned! CID: {cid}")
    result = get_from_ipfs(cid)
    print(f"Retrieved: {result}")