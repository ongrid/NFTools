import time
import os
import json
import argparse
from web3 import Web3
from progress.spinner import Spinner


parser = argparse.ArgumentParser(description="Scan ERC-721 tokens from chain")
parser.add_argument("block1", type=int, nargs="?")
parser.add_argument("block2", type=int, nargs="?")
args = parser.parse_args()

blocks_range = []
if args.block1:
    blocks_range.append(args.block1)
if args.block2:
    blocks_range.append(args.block2)
blocks_range.sort()

WEB3_URL = os.getenv("WEB3_URL")
ABI_FILE = "ERC-721.json"
ERC_721_APPROV_TOPIC = (
    "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
)
ERC_721_TRANSFER_TOPIC = (
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
)

with open(ABI_FILE, "r") as abi_f:
    abi = json.load(abi_f)

w3 = Web3(Web3.HTTPProvider(WEB3_URL))


def get_tokens(blocks_range):
    default_block_depth = 10

    if len(blocks_range) == 0:
        current_block = w3.eth.blockNumber
        blocks_range = [current_block - default_block_depth, current_block]
    if len(blocks_range) == 1:
        blocks_range.append(w3.eth.blockNumber)

    contracts = {}
    tokens = {}
    sp = Spinner()
    sp.start()

    for block_number in range(*blocks_range):
        sp.message = f"Blk: {block_number} of {blocks_range[1]}. Found:{len(tokens)} "
        blk = w3.eth.get_block(block_number)
        for tx in blk.transactions:
            rcpt = w3.eth.getTransactionReceipt(tx)
            sp.next()
            for l in rcpt.logs:
                sp.next()
                if len(l.topics) == 3 and l.topics[0].hex() in [
                    ERC_721_TRANSFER_TOPIC,
                    ERC_721_APPROV_TOPIC,
                ]:
                    if l.address not in contracts.keys():
                        try:
                            token = w3.eth.contract(abi=abi, address=l.address)
                            t = token.functions.tokenByIndex(1).call()
                            uri = token.functions.tokenURI(t).call()
                            name = token.functions.name().call()
                            total_supply = token.functions.totalSupply().call()
                            sp.clearln()
                            print(f"{l.address} {name} supply={total_supply} uri={uri}")
                            sp.message = f"Blk: {block_number} of {blocks_range[1]}. Found:{len(tokens)} "
                            sp.next()
                            tokens[l.address] = True
                            contracts[l.address] = True
                        except:
                            contracts[l.address] = False


get_tokens(blocks_range)
