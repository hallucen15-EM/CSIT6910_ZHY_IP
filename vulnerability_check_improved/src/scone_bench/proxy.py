# Copyright 2026 Anthropic PBC
# SPDX-License-Identifier: Apache-2.0
"""Proxy-contract implementation-address detection via web3 storage-slot reads."""

from eth_utils.address import to_checksum_address


def get_proxy_implementation_address(eth, target: str, block_number: int) -> str | None:
    """Return the implementation address if `target` is a proxy, else None.

    Covers EIP-1167 minimal clones, ERC-1967 implementation slot, and
    ERC-1967 beacon slot — together ~90% of proxies seen in the wild.
    """
    target_checksum = to_checksum_address(target)

    # EIP-1167 minimal clone: 363d3d373d3d3d363d73<addr>5af43d82803e903d91602b57fd5bf3
    try:
        code = eth.get_code(target_checksum, int(block_number)).hex()
        if code.startswith("0x363d3d373d3d3d363d73") and "5af43d82803e" in code:
            return to_checksum_address("0x" + code[22:62])
    except Exception:
        pass

    # ERC-1967 implementation slot
    IMPLEMENTATION_SLOT = 0x360894A13BA1A3210667C828492DB98DCA3E2076CC3735A920A3CA505D382BBC
    try:
        impl_raw = eth.get_storage_at(target_checksum, IMPLEMENTATION_SLOT, int(block_number))
        implementation = "0x" + impl_raw[-20:].hex()
        if implementation != "0x0000000000000000000000000000000000000000":
            return to_checksum_address(implementation)
    except Exception:
        pass

    # ERC-1967 beacon slot → call beacon.implementation()
    BEACON_SLOT = 0xA3F0AD74E5423AEBFD80D3EF4346578335A9A72AEAEE59FF6CB3582B35133D50
    try:
        beacon_raw = eth.get_storage_at(target_checksum, BEACON_SLOT, int(block_number))
        beacon = "0x" + beacon_raw[-20:].hex()
        if beacon != "0x0000000000000000000000000000000000000000":
            result = eth.call({"to": to_checksum_address(beacon), "data": "0x5c60da1b"}, int(block_number))
            impl = "0x" + result[-20:].hex()
            if impl != "0x0000000000000000000000000000000000000000":
                return to_checksum_address(impl)
    except Exception:
        pass

    return None
