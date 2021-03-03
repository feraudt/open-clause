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
def acc3():
    print("account[3] : ")
    return accounts.load('acc3')  # Holder : Charles

@pytest.fixture(scope="module")
def acc4():
    print("account[4] : ")
    return accounts.load('acc4')  # Holder : Dave

@pytest.fixture(scope="module")
def ERC20FixedSupply(acc0, ERC20FixedSupply):
    return ERC20FixedSupply.deploy({'from':acc0})  # Déploiement de ERC20

@pytest.fixture(scope="module")
def ERC1400(acc0, ERC20FixedSupply, ERC1400):
    return ERC1400.deploy(ERC20FixedSupply.address, 1, {'from':acc0})  # Déploiement de ERC1400

@pytest.fixture(scope="module")
def clausePreemption(acc0, ERC20FixedSupply, ERC1400, clausePreemption):
    return clausePreemption.deploy(ERC1400.address, ERC20FixedSupply.address, {'from':acc0})  # Déploiement de clausePreemption

def test_address(clausePreemption):
    print("clausePreemption.address = ", clausePreemption.address)

def test_register_holders(acc1, acc2, acc3, acc4, ERC1400):  #  Déclaration des utilisateurs à ERC1400
    ERC1400.registerAccount({'from':acc1})
    ERC1400.registerAccount({'from':acc2})
    ERC1400.registerAccount({'from':acc3})
    ERC1400.registerAccount({'from':acc4})
    assert ERC1400.holders(acc1)[1] == 0 and ERC1400.holders(acc2)[1] == 0 and ERC1400.holders(acc3)[1] == 0 and ERC1400.holders(acc4)[1] == 0

def test_register_escrow(acc0, ERC1400, clausePreemption):  # Déclaration du séquestre à ERC1400
    ERC1400.registerEscrow(clausePreemption.address, {'from':acc0})
    assert ERC1400.holders(clausePreemption.address)[1] == 2

def test_erc20_transfer(acc1, acc2, acc3, acc4, ERC20FixedSupply):  # Transfert de tokens ERC20 aux utilisateurs
    b1 = ERC20FixedSupply.balanceOf(acc1)
    b2 = ERC20FixedSupply.balanceOf(acc2)
    b3 = ERC20FixedSupply.balanceOf(acc3)
    b4 = ERC20FixedSupply.balanceOf(acc4)
    ERC20FixedSupply.transfer(acc1, 20)
    ERC20FixedSupply.transfer(acc2, 20)
    ERC20FixedSupply.transfer(acc3, 20)
    ERC20FixedSupply.transfer(acc4, 20)
    assert ERC20FixedSupply.balanceOf(acc1) == b1 + 20 and ERC20FixedSupply.balanceOf(acc2) == b2 + 20 and ERC20FixedSupply.balanceOf(acc3) == b3 + 20 and ERC20FixedSupply.balanceOf(acc4) == b4 + 20

def test_allow_erc1400(acc1, ERC20FixedSupply, ERC1400):  # Autorisation pour ERC1400 de débiter Alice en ERC20
    a = ERC20FixedSupply.allowance(acc1, ERC1400.address)
    ERC20FixedSupply.approve(ERC1400.address, 5, {'from':acc1})
    assert ERC20FixedSupply.allowance(acc1, ERC1400.address) == a + 5

def test_buy_part_erc1400(acc1, ERC1400, ERC20FixedSupply):  # Achat d'une part ERC1400 par Alice
    a = ERC20FixedSupply.allowance(acc1, ERC1400.address)
    np = ERC1400.holders(acc1)[0]
    b = ERC20FixedSupply.balanceOf(acc1)
    s = ERC1400.balanceOf(acc1)
    ERC1400.buyPartition(1234, 3, {'from':acc1})
    ERC1400.buyPartition(4567, 2, {'from':acc1})
    part = ERC1400.partitions(1234)
    assert ERC1400.holders(acc1)[0] == np + 2
    assert ERC20FixedSupply.balanceOf(acc1) == b - 5
    assert ERC1400.balanceOf(acc1) == s + 5
    assert part[0] == acc1.address
    assert part[1] == 3
    assert part[3] == 0
    assert ERC20FixedSupply.allowance(acc1, ERC1400.address) == a - 5

def test_start_preemption(acc1, acc3, acc4, ERC1400, clausePreemption):  # Déclaration des bénéficiaires par Alice
    ERC1400.approveEscrow(clausePreemption.address, 1234, 3, {'from':acc1})
    clausePreemption.startPreemption(acc3, 10, {'from':acc1})
    p3 = clausePreemption.preemptions(acc1, 0)
    clausePreemption.startPreemption(acc4, 10, {'from':acc1})
    p4 = clausePreemption.preemptions(acc1, 0)
    assert p3[0] == acc1.address and p4[0] == acc1.address
    assert p3[1] == acc3.address and p4[1] == acc4.address

def test_notice(acc1, acc3, acc4, clausePreemption):  # Notification aux bénéficiaires de l'avis de vente de la part d'Alice 1234
    clausePreemption.launchNotice(acc3, 1234, 2, 5, {'from':acc1})
    clausePreemption.launchNotice(acc4, 1234, 2, 5, {'from':acc1})
    r3 = clausePreemption.responses(acc3, 1234)
    r4 = clausePreemption.responses(acc4, 1234)
    assert r3[0] == acc1.address and r3[1] == acc3.address and r3[2] == 1234 and r3[3] == 2
    assert r4[0] == acc1.address and r4[1] == acc4.address and r4[2] == 1234 and r4[3] == 2

def test_responses(acc3, acc4, clausePreemption):  # Accord ou refus des bénéficiaires
    clausePreemption.recipientDecision(1234, 0, {'from':acc3})
    clausePreemption.recipientDecision(1234, 1, {'from':acc4})
    assert clausePreemption.responses(acc3, 1234)[-1] == False
    assert clausePreemption.responses(acc4, 1234)[-1] == True

def test_transfer(acc1, acc4, ERC20FixedSupply, ERC1400, clausePreemption):  # Choix de l'acheteur par Alice et vente
    b1 = ERC20FixedSupply.balanceOf(acc1)
    b4 = ERC20FixedSupply.balanceOf(acc4)
    ERC20FixedSupply.approve(clausePreemption.address, 2, {'from':acc4})
    ERC20FixedSupply.approve(ERC1400.address, 3, {'from':acc4})
    clausePreemption.launchTransfer(acc4, 1234, {'from':acc1})
    assert ERC20FixedSupply.balanceOf(acc1) == b1 + 5
    assert ERC20FixedSupply.balanceOf(acc4) == b4 - 5
    assert ERC1400.partitions(1234)[0] == acc4.address











