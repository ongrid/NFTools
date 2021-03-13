import argparse
import requests
import os
from web3 import Web3
import json
from termcolor import colored
from random import randint

parser = argparse.ArgumentParser(description="Display ERC-721 token details")
parser.add_argument("token_address")
args = parser.parse_args()

WEB3_URL = os.getenv("WEB3_URL")
ETHERSCAN_KEY = os.getenv("ETHERSCAN_KEY")
ABIFILES_BASEPATH = "artifacts"

# Taken from official spec
# https://eips.ethereum.org/EIPS/eip-721
ERC_721_METHODS = [
    "balanceOf",
    "ownerOf",
    "safeTransferFrom",
    "transferFrom",
    "approve",
    "setApprovalForAll",
    "getApproved",
    "isApprovedForAll",
]
ERC_721_META_METHODS = ["name", "symbol", "tokenURI"]
ERC_721_ENUMERABLE_METHODS = ["totalSupply", "tokenByIndex", "tokenOfOwnerByIndex"]

ERC165_METHOD = "supportsInterface"

KNOWN_FUNCS = (
    ERC_721_METHODS
    + ERC_721_META_METHODS
    + ERC_721_ENUMERABLE_METHODS
    + [ERC165_METHOD]
)

total_supply = None
owner = "0x0000000000000000000000000000000000000000"


def load_abi_from_etherscan(address):
    abi_url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={ETHERSCAN_KEY}"
    r = requests.get(abi_url, allow_redirects=True)
    escaped_abi = json.loads(r.content)["result"]
    dict_abi = json.loads(escaped_abi)
    jsoned_abi = json.dumps(dict_abi).encode()
    abi_filename = f"{ABIFILES_BASEPATH}/{address}.json"
    open(abi_filename, "wb").write(jsoned_abi)
    return abi_filename


def get_abi(address):
    abi_filename = f"{ABIFILES_BASEPATH}/{address}.json"
    if not os.path.isfile(abi_filename):
        abi_filename = load_abi_from_etherscan(address)
    with open(abi_filename, "r") as abi_file:
        abi = json.load(abi_file)
    return abi


w3 = Web3(Web3.HTTPProvider(WEB3_URL))
token_address = w3.toChecksumAddress(args.token_address)
print(f"Looking for {token_address}")
abi = get_abi(token_address)
token = w3.eth.contract(abi=abi, address=token_address)

UNKNOWN_FUNCS = set(token.functions) ^ set(KNOWN_FUNCS)

print("\nERC-721 basic methods:")
for m in ERC_721_METHODS:
    print(f" {m}", end=" ")
    if m in token.functions:
        print(colored("+", "green"))
    else:
        print(colored("MISS", "red"))

print("\nERC-721 Enumerable methods:")
for m in ERC_721_ENUMERABLE_METHODS:
    print(f" {m}", end=" ")
    if m in token.functions:
        if m == "totalSupply":
            try:
                total_supply = token.functions.totalSupply().call()
                print(colored(total_supply, "green"))
            except:
                print(colored("failed", "red"))
                pass
        else:
            print(colored("+", "green"))
    else:
        print(colored("MISS", "red"))

print("\nERC-721 META methods:")
for m in ERC_721_META_METHODS:
    print(f" {m}", end=" ")
    if m in token.functions:
        if m in ["name", "symbol"]:
            try:
                func = getattr(token.functions, m)
                print(colored(func().call(), "green"))
            except:
                print(colored("failed", "red"))
                pass
        else:
            print(colored("+", "green"))
    else:
        print(colored("MISS", "red"))

print("\nERC-165 Interfaces support:", end=" ")
if ERC165_METHOD in token.functions:
    print(colored("+", "green"))

# calculate token id to test it
if total_supply:
    token_index = randint(0, total_supply)
    try:
        token_id = token.functions.tokenByIndex(token_index).call()
    except:
        pass
else:
    token_id = 1

print(f"\nWith example token {colored(token_id, 'green')}:")
if "tokenURI" in token.functions:
    print(" tokenURI:", end=" ")
    try:
        print(colored(token.functions.tokenURI(token_id).call(), "green"))
    except:
        print(colored("failed", "red"))
        pass
if "ownerOf" in token.functions:
    print(" ownerOf:", end=" ")
    try:
        owner = token.functions.ownerOf(token_id).call()
        print(colored(owner, "green"))
    except:
        print(colored("failed", "red"))
        pass

print(f"\nFuzzing non-standard functions:")
for m in UNKNOWN_FUNCS:
    print(f" {m}:", end=" ")
    f = getattr(token.functions, m)
    result = None
    try:
        result = f().call()
    except:
        pass

    try:
        result = f(token_id).call()
    except:
        pass

    try:
        result = f(owner).call()
    except:
        pass

    if result:
        print(colored(result, "yellow"))
    else:
        print()
