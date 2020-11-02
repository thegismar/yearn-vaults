from itertools import count
from brownie import Wei, reverts
from useful_methods import stateOfStrat, stateOfVault, deposit,wait, withdraw, harvest
import brownie


def test_strat_sushi(accounts, interface, web3, chain, Vault, StrategySushiswapPair):
    gov = accounts[0]
    print(gov)
    strategist_and_keeper = accounts[1]
    print(strategist_and_keeper)
    
    # dai = interface.ERC20('0x6b175474e89094c44da98b954eedeac495271d0f')
    lp = interface.ERC20('0xc3d03e4f041fd4cd388c549ee2a29a9e5075882f')
    sushi = interface.ERC20('0x6b3595068778dd592e39a122f4f5a5cf09c90fe2')
    
    whale = accounts.at("0xc3d03e4f041fd4cd388c549ee2a29a9e5075882f", force=True)

    # Deploy the Vault
    vault = gov.deploy(
        Vault, lp, gov, gov, "Yearn Sushi LP v1", "yETH-DAI-SLP"
    )

    assert vault.governance() == gov
    assert vault.guardian() == gov
    assert vault.rewards() == gov
    assert vault.token() == lp

    # Deploy the Strategy
    strategy = strategist_and_keeper.deploy(StrategySushiswapPair, vault)

    # Addresses
    assert strategy.strategist() == strategist_and_keeper
    assert strategy.keeper() == strategist_and_keeper
    assert strategy.want() == vault.token()
    stateOfStrat(strategy,lp)

    # Add strategy to the Vault
    assert vault.strategies(strategy) == [0, 0, 0, 0, 0, 0, 0]

    _debtLimit = Wei('1000000 ether')
    _rateLimit =  Wei('1000000 ether')

    vault.addStrategy(strategy, _debtLimit, _rateLimit, 50, {"from": gov})

    assert vault.strategies(strategy) == [
        50,
        web3.eth.blockNumber,
        _debtLimit,
        _rateLimit,
        web3.eth.blockNumber,
        0,
        0,
    ]

    # Nothing was reported yet from the strategy
    assert vault.expectedReturn(strategy) == 0
    stateOfStrat(strategy,lp)

    depositLimit = Wei('500000 ether')
    vault.setDepositLimit(depositLimit, {"from": gov})
    assert vault.depositLimit() == depositLimit 
    
    # Provide funds to the Vault from whale
   
    # Test first with simply 5k as it is the current rate LP/block

    amount = Wei('100000 ether')
    deposit(amount,whale, lp, vault )
    stateOfStrat(strategy,lp)
    stateOfVault(vault,strategy)

    # Call harvest in Strategy only when harvestTrigger() --> (true)
    harvest(strategy, strategist_and_keeper)

   # assert( !strategy.harvestTrigger(0, {'from': strategist_and_keeper}))
    stateOfStrat(strategy,lp)
    stateOfVault(vault,strategy)

    # now lets see 90k

    amount = Wei('320000 ether')
    deposit(amount,whale, lp, vault )
    stateOfStrat(strategy,lp)
    stateOfVault(vault,strategy)
    
    harvest(strategy, strategist_and_keeper)

    stateOfStrat(strategy,lp)
    stateOfVault(vault,strategy)

    stateOfStrat(strategy,lp)
    stateOfVault(vault,strategy)

    while strategy.harvestTrigger(0) == False:
         wait(25, chain)

    stateOfStrat(strategy,lp)
    stateOfVault(vault,strategy)

    harvest(strategy, strategist_and_keeper)

    stateOfStrat(strategy,lp)
    stateOfVault(vault,strategy)

    ##test migration
    print('test migration')
    strategy2 = strategist_and_keeper.deploy(StrategySushiswapPair, vault)
    vault.migrateStrategy(strategy,strategy2,  {"from": gov})

    print('old strat')
    stateOfStrat(strategy,lp)
    stateOfVault(vault,strategy)

    print('new strat')
    stateOfStrat(strategy2,lp)
    stateOfVault(vault,strategy2)

    withdraw(1, whale, lp, vault)
    stateOfStrat(strategy2,lp)
    stateOfVault(vault,strategy2)

    amount = Wei('320000 ether')
    deposit(amount,whale, lp, vault )
    stateOfStrat(strategy2,lp)
    stateOfVault(vault,strategy2)

    harvest(strategy2, strategist_and_keeper)
    stateOfStrat(strategy2,lp)
    stateOfVault(vault,strategy2)

    withdraw(1, whale, lp, vault)
    stateOfStrat(strategy2,lp)
    stateOfVault(vault,strategy2)