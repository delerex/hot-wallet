from pycoin.networks.bitcoinish import create_bitcoinish_network

network = create_bitcoinish_network(
    symbol="XRP", network_name="Ripple", subnet_name="testnet",
    wif_prefix_hex="80", sec_prefix="BTCSEC:", address_prefix_hex="00", pay_to_script_prefix_hex="05",
    bip32_prv_prefix_hex="0488ade4", bip32_pub_prefix_hex="0488B21E", bech32_hrp="bc",
    magic_header_hex="F9BEB4D9", default_port=8333,
    dns_bootstrap=[])