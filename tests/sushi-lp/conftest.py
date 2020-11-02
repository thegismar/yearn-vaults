import pytest
from brownie import Wei


#change these fixtures for generic tests
@pytest.fixture
def currency(interface):
    #this one is ETH/DAI SLP:
    yield interface.ERC20('0xc3d03e4f041fd4cd388c549ee2a29a9e5075882f')

@pytest.fixture
def strategy_changeable(StrategySushiswapPair):
    yield StrategySushiswapPair

@pytest.fixture
def whale(accounts, history, web3):
    #lots of ETH/DAI LP account
    acc = accounts.at('0xc3d03e4f041fd4cd388c549ee2a29a9e5075882f', force=True)
    yield acc

@pytest.fixture()
def strategist(accounts, whale, currency):
    currency.transfer(accounts[1], Wei('1000 ether'), {'from': whale})
    yield accounts[1]


@pytest.fixture
def dai(interface):
    yield interface.ERC20('0x6b175474e89094c44da98b954eedeac495271d0f')

#any strategy just deploys base strategy can be used because they have the same interface
@pytest.fixture(scope='session')
def strategy_generic(StrategySushiswapPair):
    #print('Do you want to use deployed strategy? (y)')
    #if input() == 'y' or 'Y':
    print('Enter strategy address')
    yield StrategySushiswapPair.at(input())

@pytest.fixture(scope='session')
def vault_generic(Vault):
    print('Enter vault address')
    yield Vault.at(input())

@pytest.fixture(scope='session')
def strategist_generic(accounts):
    print('Enter strategist address')
    yield accounts.at(input(), force=True)

@pytest.fixture(scope='session')
def governance_generic(accounts):
    print('Enter governance address')
    yield accounts.at(input(), force=True)

@pytest.fixture(scope='session')
def whale_generic(accounts):
    print('Enter whale address')
    yield accounts.at(input(), force=True)

@pytest.fixture(scope='session')
def want_generic(interface):
    print('Enter want address')
    yieldinterface.ERC20(input())

@pytest.fixture(scope='session')
def live_vault(Vault):
    yield Vault.at('0x9B142C2CDAb89941E9dcd0B6C1cf6dEa378A8D7C')

@pytest.fixture(scope='session')
def live_strategy(YearnDaiCompStratV2):
    yield YearnDaiCompStratV2.at('0x4C6e9d7E5d69429100Fcc8afB25Ea980065e2773')

@pytest.fixture(scope='session')
def dai(interface):
    yield interface.ERC20('0x6b175474e89094c44da98b954eedeac495271d0f')

#@pytest.fixture(autouse=True)
#def isolation(fn_isolation):
#    pass
@pytest.fixture(scope="module", autouse=True)
def shared_setup(module_isolation):
    pass

@pytest.fixture
def gov(accounts):
    yield accounts[0]

@pytest.fixture
def rando(accounts):
    yield accounts[9]

@pytest.fixture()
def vault(gov, dai, Vault):
    # Deploy the Vault
    vault = gov.deploy(
        Vault, dai, gov, gov, "Yearn DAI v2", "y2DAI"
    )
    yield vault

@pytest.fixture()
def seededvault(vault, dai, rando):
   # Make it so vault has some AUM to start
    amount = Wei('10000 ether')
    token.approve(vault, amount, {"from": rando})
    vault.deposit(amount, {"from": rando})
    assert token.balanceOf(vault) == amount
    assert vault.totalDebt() == 0  # No connected strategies yet
    yield vault

@pytest.fixture()
def strategy(gov, strategist, dai, vault, YearnDaiCompStratV2):
    strategy = strategist.deploy(YearnDaiCompStratV2, vault)

    vault.addStrategy(
        strategy,
        dai.totalSupply(),  # Debt limit of 20% of token supply 
        dai.totalSupply(),  # Rate limt of 0.1% of token supply per block
        50,  # 0.5% performance fee for Strategist
        {"from": gov},
    )
    yield strategy

@pytest.fixture()
def largerunningstrategy(gov, strategy, dai, vault, whale):

    amount = Wei('499000 ether')
    dai.approve(vault, amount, {'from': whale})
    vault.deposit(amount, {'from': whale})    

    strategy.harvest({'from': gov})
    
    #do it again with a smaller amount to replicate being this full for a while
    amount = Wei('1000 ether')
    dai.approve(vault, amount, {'from': whale})
    vault.deposit(amount, {'from': whale})   
    strategy.harvest({'from': gov})
    
    yield strategy

@pytest.fixture()
def enormousrunningstrategy(gov, largerunningstrategy, dai, vault, whale):
    dai.approve(vault, dai.balanceOf(whale), {'from': whale})
    vault.deposit(dai.balanceOf(whale), {'from': whale})   
   
    collat = 0

    while collat < largerunningstrategy.collateralTarget() / 1.001e18:

        largerunningstrategy.harvest({'from': gov})
        deposits, borrows = largerunningstrategy.getCurrentPosition()
        collat = borrows / deposits
        
    
    yield largerunningstrategy
