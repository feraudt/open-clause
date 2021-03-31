import pytest
from brownie import accounts
import time

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
def acc9():
    print("account[9] : ")
    return accounts.load('acc9')  # Holder : Controller

@pytest.fixture(scope="module")
def ERC20FixedSupply(acc0, ERC20FixedSupply):
    return ERC20FixedSupply.deploy({'from':acc0})  # Déploiement de ERC20

@pytest.fixture(scope="module")
def ERC1400(acc0, ERC20FixedSupply, ERC1400):
    return ERC1400.deploy(ERC20FixedSupply.address, 1, {'from':acc0})  # Déploiement de ERC1400

@pytest.fixture(scope="module")
def clauseSellorbuy(clauseSellorbuy, ERC1400, ERC20FixedSupply, acc0):
    return clauseSellorbuy.deploy(ERC1400.address, ERC20FixedSupply.address, {'from':acc0})

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

def test_allow_erc1400(acc1, acc2, ERC20FixedSupply, ERC1400):  # Autorisation pour ERC1400 de débiter Alice et Bob en tokens
    ERC20FixedSupply.approve(ERC1400.address, 0, {'from':acc1})
    ERC20FixedSupply.approve(ERC1400.address, 0, {'from':acc2})
    ERC20FixedSupply.increaseAllowance(ERC1400.address, 5, {'from':acc1})
    ERC20FixedSupply.increaseAllowance(ERC1400.address, 5, {'from':acc2})
    assert ERC20FixedSupply.allowance(acc1, ERC1400.address) == 5

def test_buy_part_erc1400(acc1, acc2, ERC1400, ERC20FixedSupply):  # Achat de parts ERC1400 par Alice et Bob
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

def test_allow_sellorbuy(acc1, clauseSellorbuy, ERC1400, ERC20FixedSupply):
    ERC1400.approveEscrow(clauseSellorbuy.address, 1234, {'from':acc1})
    ERC1400.approveEscrow(clauseSellorbuy.address, 4321, {'from':acc1})
    ERC20FixedSupply.approve(clauseSellorbuy.address, 0, {'from':acc1})
    ERC20FixedSupply.increaseAllowance(clauseSellorbuy.address, 1, {'from':acc1})
    ERC20FixedSupply.increaseAllowance(ERC1400.address, 5, {'from':acc1})
    assert ERC1400._allowanceEscrow(acc1, clauseSellorbuy.address, 1234)
    assert ERC20FixedSupply.allowance(acc1, clauseSellorbuy.address) == 1

def test_start_sale(acc1, acc2, clauseSellorbuy):
    clauseSellorbuy.startSellorbuy(acc2, 6, 60, {'from':acc1})
    n = clauseSellorbuy.notices(acc2)
    assert n[0] == acc1.address and n[1] == acc2.address and n[2] == 6

def test_remainer_accept(acc1, acc2, ERC20FixedSupply, ERC1400, clauseSellorbuy):
    b1 = ERC20FixedSupply.balanceOf(acc1)
    b2 = ERC20FixedSupply.balanceOf(acc2)
    bp1 = ERC1400.balanceOf(acc1)
    bp2 = ERC1400.balanceOf(acc2)
    ERC1400.approveEscrow(clauseSellorbuy.address, 5555, {'from':acc2})
    print('allowanceEscrow Bob part 5555 = ', ERC1400._allowanceEscrow(acc2, clauseSellorbuy.address, 5555))
    clauseSellorbuy.remainerAccept({'from':acc2})
    assert ERC20FixedSupply.balanceOf(acc2) == b2 + 6 and ERC20FixedSupply.balanceOf(acc1) == b1 - 6
    assert ERC1400.balanceOf(acc2) == bp2 - 5 and ERC1400.balanceOf(acc1) == bp1 + 5
    assert ERC1400.partitions(5555)[0] == acc1.address

def test_remainer_deny(acc1, acc2, clauseSellorbuy, ERC1400, ERC20FixedSupply):
    ERC20FixedSupply.increaseAllowance(ERC1400.address, 10, {'from':acc2})
    ERC1400.buyPartition(8888, 10, {'from':acc2})

    ERC1400.approveEscrow(clauseSellorbuy.address, 1234, {'from':acc1})
    ERC1400.approveEscrow(clauseSellorbuy.address, 4321, {'from':acc1})
    ERC1400.approveEscrow(clauseSellorbuy.address, 5555, {'from':acc1})
    ERC20FixedSupply.increaseAllowance(clauseSellorbuy.address, 2, {'from':acc1})
    ERC20FixedSupply.increaseAllowance(ERC1400.address, 10, {'from':acc1})

    b1 = ERC20FixedSupply.balanceOf(acc1)
    b2 = ERC20FixedSupply.balanceOf(acc2)
    bp1 = ERC1400.balanceOf(acc1)
    bp2 = ERC1400.balanceOf(acc2)

    clauseSellorbuy.startSellorbuy(acc2, 12, 60, {'from':acc1})
    ERC20FixedSupply.increaseAllowance(clauseSellorbuy.address, 2, {'from':acc2})
    ERC20FixedSupply.increaseAllowance(ERC1400.address, 10, {'from':acc2})
    clauseSellorbuy.remainerDeny({'from':acc2})
    assert ERC20FixedSupply.balanceOf(acc2) == b2 - 12 and ERC20FixedSupply.balanceOf(acc1) == b1 + 12
    assert ERC1400.balanceOf(acc2) == bp2 + 10 and ERC1400.balanceOf(acc1) == bp1 - 10
    assert ERC1400.partitions(5555)[0] == acc2.address

def test_controller(acc1, acc2, acc9, clauseSellorbuy, ERC1400, ERC20FixedSupply):
    ERC20FixedSupply.transfer(acc1, 20)
    ERC20FixedSupply.transfer(acc2, 20)
    ERC20FixedSupply.increaseAllowance(ERC1400.address, 20, {'from':acc1})
    ERC1400.buyPartition(2020, 20, {'from':acc1})
    acc9 = accounts.load('acc9')
    ERC1400.registerController(acc9)

    ERC20FixedSupply.increaseAllowance(clauseSellorbuy.address, 2, {'from':acc1})
    ERC20FixedSupply.increaseAllowance(ERC1400.address, 20, {'from':acc1})
    ERC1400.approveEscrow(clauseSellorbuy.address, 2020, {'from':acc1})

    clauseSellorbuy.startSellorbuy(acc2, 22, 10, {'from':acc1})
    clauseSellorbuy.controllerRemove(acc2, {'from':acc9})

    b1 = ERC20FixedSupply.balanceOf(acc1)
    b2 = ERC20FixedSupply.balanceOf(acc2)
    ERC20FixedSupply.increaseAllowance(clauseSellorbuy.address, 2, {'from':acc1})
    ERC20FixedSupply.increaseAllowance(ERC1400.address, 20, {'from':acc1})
    ERC1400.approveEscrow(clauseSellorbuy.address, 2020, {'from':acc1})

    clauseSellorbuy.startSellorbuy(acc2, 22, 1, {'from':acc1})
    time.sleep(61)
    # in case of litige, is the transfer approved ?
    clauseSellorbuy.controllerForce(acc2, {'from':acc9})
    assert ERC20FixedSupply.balanceOf(acc1) == b1 + 22 and ERC20FixedSupply.balanceOf(acc2) == b2 - 22
    assert ERC1400.partitions(5555)[0] == acc1.address
