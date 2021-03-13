# NFT tools

Extracts and outputs ERC-721 fields (both custom and well-known) from the given NFT contract

# Install dependencies

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Run

* Export the URI of web3 node to your environment. The simplest way is to register on infura.io and use the personal https: or wss: endpoint.
* Export your ETHERSCAN API key (it's used to retrieve token ABI if the contract is verified)

```sh
export WEB3_URL=https://mainnet.infura.io/v3/<YOUR_INFURA_ID>
export ETHERSCAN_KEY=<YOUR_ETHERSCAN_KEY>
```

Then run the script using NFT contract address. It accepts both checksumed (EIP-55 mixed case) and plain (lowercase) hex addresses.

```sh
python nftshow.py 0x60f80121c31a0d46b5279700f9df786054aa5ee5
```
