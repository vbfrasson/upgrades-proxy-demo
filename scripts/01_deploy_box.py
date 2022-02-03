from scripts.helpful_scripts import *
from brownie import (
    network,
    accounts,
    Box,
    BoxV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    config,
)


def main():
    account = get_account()
    print(f"Deploy to {network.show_active()}")
    # Implementation Contract
    box = Box.deploy(
        {"from": account},
        publish_source=True,
    )
    # Hooking up proxy to Implementation Contract

    # Optional, deploy the ProxyAdmin and use that as the admin contract
    proxy_admin = ProxyAdmin.deploy(
        {"from": account}, publish_source=True
    )  # , publish_source=True)
    # If we want an intializer function we can add
    # `initializer=box.store, 1`
    # to simulate the initializer being the `store` function
    # with a `newValue` of 1
    box_encoded_initializer_function = encode_function_data()
    # box_encoded_initializer_function = encode_function_data(initializer=box.store, 1)

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        # account.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
        publish_source=True,
    )
    print(f"Proxy deployed to {proxy}, you can now update to V2")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(0, {"from": account})

    # Updating Proxy to BoxV2
    box_v2 = BoxV2.deploy({"from": account}, publish_source=True)
    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    print("Proxy has been upgraded")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())
