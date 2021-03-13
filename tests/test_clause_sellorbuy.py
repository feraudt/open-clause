import pytest
from brownie import accounts

@pytest.fixture(scope="module")
def acc0():
    print("account[0] : ")
    return accounts.load('acc0')  # Developer

@pytest.fixture(scope="module")
def acc1():
    print("account[1] : ")
    return accounts.load('acc1')  # Holder : Alice

@pytest.fixture(scope="module")
def acc2():
    print("account[2] : ")
    return accounts.load('acc2')  # Holder : Bob

@pytest.fixture(scope="module")
def ERC20FixedSupply(acc0, ERC20FixedSupply):
    return ERC20FixedSupply.deploy({'from':acc0})  # Déploiement de ERC20

@pytest.fixture(scope="module")
def ERC1400(acc0, ERC20FixedSupply, ERC1400):
    return ERC1400.deploy(ERC20FixedSupply.address, 1, {'from':acc0})  # Déploiement de ERC1400

@pytest.fixture(scope="module")
def clauseSellorbuy(clauseSellorbuy, ERC1400, ERC20FixedSupply, acc0):
    return clauseSellorbuy.deploy(ERC1400[0].address, ERC20FixedSupply[0].address, {'from':acc0})

def test_address(clauseSellorbuy):
    print("clauseSellorbuy.address = ", clauseSellorbuy.address)

def test_register_holders(acc1, acc2, ERC1400):  #  Déclaration des utilisateurs à ERC1400
    ERC1400.registerAccount({'from':acc1})
    ERC1400.registerAccount({'from':acc2})
    assert ERC1400.holders(acc1)[1] == 0 and ERC1400.holders(acc2)[1] == 0

def test_register_escrow(acc0, ERC1400, clauseSellorbuy):  # Déclaration du séquestre à ERC1400
    ERC1400.registerEscrow(clauseSellorbuy.address, {'from':acc0})
    assert ERC1400.holders(clauseSellorbuy.address)[1] == 2

def test_erc20_transfer(acc1, acc2, ERC20FixedSupply):  # Transfert de tokens ERC20 aux utilisateurs
    b1 = ERC20FixedSupply.balanceOf(acc1)
    b2 = ERC20FixedSupply.balanceOf(acc2)
    ERC20FixedSupply.transfer(acc1, 50)
    ERC20FixedSupply.transfer(acc2, 50)
    assert ERC20FixedSupply.balanceOf(acc1) == b1 + 50 and ERC20FixedSupply.balanceOf(acc2) == b2 + 50

def test_allow_erc1400(acc1, ERC20FixedSupply, ERC1400):  # Autorisation pour ERC1400 de débiter Alice et Bob en tokens ERC20
    ERC20FixedSupply.approve(ERC1400.address, 0, {'from':acc1})
    ERC20FixedSupply.approve(ERC1400.address, 0, {'from':acc2})
    ERC20FixedSupply.increaseAllowance(ERC1400.address, 5, {'from':acc1})
    ERC20FixedSupply.increaseAllowance(ERC1400.address, 5, {'from':acc2})
    assert ERC20FixedSupply.allowance(acc1, ERC1400.address) == 5

def test_buy_part_erc1400(acc1, ERC1400, ERC20FixedSupply):  # Achat de parts ERC1400 par Alice et Bob
    a = ERC20FixedSupply.allowance(acc1, ERC1400.address)
    np = ERC1400.holders(acc1)[0]
    b = ERC20FixedSupply.balanceOf(acc1)
    s = ERC1400.balanceOf(acc1)
    ERC1400.buyPartition(1234, 2, {'from':acc1})
    ERC1400.buyPartition(4321, 3, {'from':acc1})
    ERC1400.buyPartition(5555, 5, {'from':acc2})
    part = ERC1400.partitions(1234)
    assert ERC1400.holders(acc1)[0] == np + 2
    assert ERC20FixedSupply.balanceOf(acc1) == b - 5
    assert ERC1400.balanceOf(acc1) == s + 5
    assert part[0] == acc1.address
    assert part[1] == 2
    assert part[3] == 0
    assert ERC20FixedSupply.allowance(acc1, ERC1400.address) == a - 5

def test_allow_sellorbuy(acc1, clauseSellorbuy, ERC1400):
    ERC1400.approveEscrow(clauseSellorbuy.address, 1234, 2, {'from':acc1})
    ERC1400.approveEscrow(clauseSellorbuy.address, 4321, 3, {'from':acc1})
    ERC20FixedSupply.approve(clauseSellorbuy.address, 0, {'from':acc1})
    ERC20FixedSupply.increaseAllowance(clauseSellorbuy.address, 1, {'from':acc1})











