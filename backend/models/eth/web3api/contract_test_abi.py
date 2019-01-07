from models.eth.web3api.contract_erc20_abi import erc20abi

test_erc20abi = erc20abi.copy()
test_erc20abi.append(
    {
        "constant": False,
        "inputs": [
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "showMeTheMoney",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
)
