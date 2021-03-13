import pytest
import time
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
def clauseForward(acc0, ERC20FixedSupply, ERC1400, clauseForward):
    return clauseForward.deploy(ERC1400.address, ERC20FixedSupply.address, {'from':acc0})  # Déploiement de clauseForward

def test_address(clauseForward):
    print("clauseForward.address = ", clauseForward.address)

def test_register_holders(acc1, acc2, ERC1400):  #  Déclaration des utilisateurs à ERC1400
    ERC1400.registerAccount({'from':acc1})
    ERC1400.registerAccount({'from':acc2})
    ERC20FixedSupply.approve(ERC1400.address, 0, {'from':acc1})
    ERC20FixedSupply.approve(ERC1400.address, 0, {'from':acc2})
    assert ERC1400.holders(acc1)[1] == 0 and ERC1400.holders(acc2)[1] == 0
    assert ERC20FixedSupply.allowance(acc1, ERC1400.address) == 0 and ERC20FixedSupply.allowance(acc2, ERC1400.address) == 0

def test_register_escrow(acc0, ERC1400, clauseForward):  # Déclaration du séquestre à ERC1400
    ERC1400.registerEscrow(clauseForward.address, {'from':acc0})
    assert ERC1400.holders(clauseForward.address)[1] == 2

def test_erc20_transfer(acc1, acc2, ERC20FixedSupply):  # Transfert de tokens ERC20 aux utilisateurs
    b1 = ERC20FixedSupply.balanceOf(acc1)
    b2 = ERC20FixedSupply.balanceOf(acc2)
    ERC20FixedSupply.transfer(acc1, 20)
    ERC20FixedSupply.transfer(acc2, 20)
    assert ERC20FixedSupply.balanceOf(acc1) == b1 + 20 and ERC20FixedSupply.balanceOf(acc2) == b2 + 20

def test_allow_erc1400(acc1, ERC20FixedSupply, ERC1400):  # Autorisation pour ERC1400 de débiter Alice en ERC20
    a = RC20FixedSupply.allowance(acc1, ERC1400.address)
    ERC20FixedSupply.increaseAllowance(ERC1400.address, 5, {'from':acc1})
    assert ERC20FixedSupply.allowance(acc1, ERC1400.address) == a + 5

def test_buy_part_erc1400(acc1, ERC1400, ERC20FixedSupply):  # Achat d'une part ERC1400 par Alice
    a = ERC20FixedSupply.allowance(acc1, ERC1400.address)
    np = ERC1400.holders(acc1)[0]
    b = ERC20FixedSupply.balanceOf(acc1)
    s = ERC1400.balanceOf(acc1)
    ERC1400.buyPartition(1234, 3, {'from':acc1})
    part = ERC1400.partitions(1234)
    assert ERC1400.holders(acc1)[0] == np + 1
    assert ERC20FixedSupply.balanceOf(acc1) == b - 3
    assert ERC1400.balanceOf(acc1) == s + 3
    assert part[0] == acc1.address
    assert part[1] == 3
    assert part[3] == 0
    assert ERC20FixedSupply.allowance(acc1, ERC1400.address) == a - 3

def test_allow_sale(acc1, acc2, ERC20FixedSupply, ERC1400, clauseForward):  # Positionnement des autorisations requises
    a1400 = ERC20FixedSupply.allowance(acc2, ERC1400)
    ERC1400.approveEscrow(clauseForward.address, 1234, 3, {'from':acc1})
    ERC20FixedSupply.approve(clauseForward.address, 0, {'from':acc1})
    ERC20FixedSupply.approve(clauseForward.address, 0, {'from':acc2})
    ERC20FixedSupply.increaseAllowance(clauseForward.address, 2, {'from':acc2})
    ERC20FixedSupply.increaseAllowance(ERC1400.address, 3, {'from':acc2})
    assert ERC20FixedSupply.allowance(acc2, clauseForward.address) == 2
    assert ERC20FixedSupply.allowance(acc2, ERC1400.address) == a1400 + 3

def test_start_sale(acc1, acc2, clauseForward):  # Lancement de l'avis de vente par Alice pour Bob
    clauseForward.startForwardSale(acc2, 1234, 2, 1, {'from':acc1})
    f = clauseForward.forwards(1234)
    assert f[0] == acc1.address
    assert f[1] == acc2.address
    assert f[2] == 2
    assert f[4] == 1

def test_launch_sale(acc2, clauseForward, ERC1400):  # Attente du terme et vente effective de la partition
    time.sleep(61)
    clauseForward.launchSale(1234, {'from':acc2})
    assert clauseForward.forwards(1234)[4] == 2
    assert ERC1400.partitions(1234)[0] == acc2.address












