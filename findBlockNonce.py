#!/bin/python
import hashlib
import os
import random


def mine_block(k, prev_hash, transactions):
    """
        k - Number of trailing zeros in the binary representation (integer)
        prev_hash - the hash of the previous block (bytes)
        rand_lines - a set of "transactions," i.e., data to be included in this block (list of strings)

        Complete this function to find a nonce such that 
        sha256( prev_hash + rand_lines + nonce )
        has k trailing zeros in its *binary* representation
    """
    if not isinstance(k, int) or k < 0:
        print("mine_block expects positive integer")
        return b'\x00'

    # TODO your code to find a nonce here
    while True:
        # Generate a random nonce as bytes
        nonce = os.urandom(32)

        # Build the hash: prev_hash + each transaction + nonce
        m = hashlib.sha256()
        m.update(prev_hash)
        for transaction in transactions:
            m.update(transaction.encode('utf-8'))
        m.update(nonce)

        # Get the hash as bytes
        hash_bytes = m.digest()

        # Convert to integer to check trailing zero bits
        hash_int = int.from_bytes(hash_bytes, 'big')

        # Check if the last k bits are all zeros
        if hash_int % (2 ** k) == 0:
            break

    assert isinstance(nonce, bytes), 'nonce should be of type bytes'
    return nonce


def get_random_lines(filename, quantity):
    """
    This is a helper function to get the quantity of lines ("transactions")
    as a list from the filename given. 
    Do not modify this function
    """
    lines = []
    with open(filename, 'r') as f:
        for line in f:
            lines.append(line.strip())

    random_lines = []
    for x in range(quantity):
        random_lines.append(lines[random.randint(0, quantity - 1)])
    return random_lines


if __name__ == '__main__':
    # This code will be helpful for your testing
    filename = "bitcoin_text.txt"
    num_lines = 10  # The number of "transactions" included in the block

    # The "difficulty" level. For our blocks this is the number of Least Significant Bits
    # that are 0s. For example, if diff = 5 then the last 5 bits of a valid block hash would be zeros
    # The grader will not exceed 20 bits of "difficulty" because larger values take to long
    diff = 20

    prev_hash = b'\x00' * 32  # dummy previous hash for testing

    transactions = get_random_lines(filename, num_lines)
    nonce = mine_block(diff, prev_hash, transactions)
    print(nonce)
