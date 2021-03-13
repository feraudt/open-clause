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
def acc9():
	print("account[9] : ")
	return accounts.load('acc9')  # Controller

@pytest.fixture(scope="module")
def ERC20FixedSupply(acc0, ERC20FixedSupply):
	return ERC20FixedSupply.deploy({'from':acc0})  # Déploiement de ERC20

@pytest.fixture(scope="module")
def ERC1400(acc0, ERC20FixedSupply, ERC1400):
	return ERC1400.deploy(ERC20FixedSupply.address, 1, {'from':acc0})  # Déploiement de ERC1400

@pytest.fixture(scope="module")
def clauseOption(acc0, ERC20FixedSupply, ERC1400, clauseOption):
	return clauseOption.deploy(ERC1400.address, ERC20FixedSupply.address, {'from':acc0})  # Déploiement de clauseOption

def test_address(ERC1400, clauseOption):
	print("ERC1400.address = ", ERC1400.address)
	print("clauseOption.address = ", clauseOption.address)

def test_register_holders(acc1, acc2, ERC1400):  #  Déclaration des utilisateurs à ERC1400
	ERC1400.registerAccount({'from':acc1})
	ERC1400.registerAccount({'from':acc2})
	assert ERC1400.holders(acc1)[1] == 0 and ERC1400.holders(acc2)[1] == 0

def test_register_escrow(acc0, ERC1400, clauseOption):  # Déclaration du séquestre à ERC1400
	ERC1400.registerEscrow(clauseOption.address, {'from':acc0})
	assert ERC1400.holders(clauseOption.address)[1] == 2

def test_erc20_transfer(acc1, acc2, ERC20FixedSupply):  # Transfert de ERC20 aux utilisateurs
	b1 = ERC20FixedSupply.balanceOf(acc1)
	b2 = ERC20FixedSupply.balanceOf(acc2)
	ERC20FixedSupply.transfer(acc1, 20)
	ERC20FixedSupply.transfer(acc2, 20)
	assert ERC20FixedSupply.balanceOf(acc1) == b1 + 20 and ERC20FixedSupply.balanceOf(acc2) == b2 + 20

def test_init_allowance(acc1, acc2, ERC20FixedSupply, ERC1400):
	ERC20FixedSupply.approve(ERC1400.address, 0, {'from':acc1})
	ERC20FixedSupply.approve(ERC1400.address, 0, {'from':acc2})
	assert ERC20FixedSupply.allowance(acc1, ERC1400.address) == 0 and ERC20FixedSupply.allowance(acc2, ERC1400.address) == 0

def test_allow_erc1400(acc1, ERC20FixedSupply, ERC1400):  # Autorisation pour ERC1400 de débiter Alice en ERC20
	a = ERC20FixedSupply.allowance(acc1, ERC1400.address)
	ERC20FixedSupply.increaseAllowance(ERC1400.address, 5, {'from':acc1})
	assert ERC20FixedSupply.allowance(acc1, ERC1400.address) == a + 5

def test_buy_part_erc1400(acc1, ERC1400, ERC20FixedSupply):  # Achat d'une part ERC1400 par Alice
	np = ERC1400.holders(acc1)[0]
	b = ERC20FixedSupply.balanceOf(acc1)
	s = ERC1400.balanceOf(acc1)
	a = ERC20FixedSupply.allowance(acc1, ERC1400.address)
	ERC1400.buyPartition(1234, 2, {'from':acc1})
	assert ERC1400.holders(acc1)[0] == np + 1
	assert ERC20FixedSupply.balanceOf(acc1) == b - 2
	assert ERC1400.balanceOf(acc1) == s + 2
	assert ERC20FixedSupply.allowance(acc1, ERC1400.address) == a - 2

def test_allow_option(ERC20FixedSupply, ERC1400, clauseOption, acc1, acc2):  # Autorisation d'option sur la part
	ERC20FixedSupply.approve(clauseOption.address, 0, {'from':acc1})
	ERC20FixedSupply.approve(clauseOption.address, 0, {'from':acc2})
	a = ERC20FixedSupply.allowance(acc2, clauseOption.address)
	ERC20FixedSupply.increaseAllowance(clauseOption.address, 1, {'from':acc2})
	ERC1400.approveEscrow(clauseOption.address, 1234, {'from':acc1})
	assert ERC20FixedSupply.allowance(acc2, clauseOption.address) == a + 1
	assert ERC20FixedSupply.allowance(acc1, clauseOption.address) == 0

def test_start_option(ERC20FixedSupply, clauseOption, ERC1400, acc1, acc2):  # Début de l'option sur la part d'Alice pour Bob
	b2 = ERC20FixedSupply.balanceOf(acc2)
	a = ERC20FixedSupply.allowance(acc2, clauseOption.address)
	clauseOption.startOption(acc2, 1234, 3, 1, 2, {'from':acc1})
	part = ERC1400.partitions(1234)
	opt = clauseOption.options(1234)
	assert part[3] == 1
	assert opt[0] == part[0]
	assert opt[1] == acc2
	assert ERC20FixedSupply.balanceOf(acc2) == b2 - 1
	assert ERC20FixedSupply.allowance(acc2, clauseOption.address) == a - 1

def test_accept(ERC20FixedSupply, ERC1400, clauseOption, acc1, acc2):  # Vente de la part à Bob
	np = ERC1400.holders(acc2)[0]
	b1 = ERC20FixedSupply.balanceOf(acc1)
	b2 = ERC20FixedSupply.balanceOf(acc2)
	ERC20FixedSupply.increaseAllowance(ERC1400.address, 3, {'from':acc2})
	clauseOption.recipientAccept(1234, {'from':acc2})
	assert ERC1400.holders(acc2)[0] == np + 1
	assert ERC1400.partitions(1234)[3] == 0
	assert ERC20FixedSupply.balanceOf(acc2) == b2 - 3
	assert ERC20FixedSupply.balanceOf(acc1) == b1 + 3

def test_deny(ERC20FixedSupply, ERC1400, clauseOption, acc1, acc2):  # Option pour Alice sur la part de Bob et refus d'Alice
	b1 = ERC20FixedSupply.balanceOf(acc1)
	ERC20FixedSupply.increaseAllowance(clauseOption.address, 1, {'from':acc1})
	ERC1400.approveEscrow(clauseOption.address, 1234, {'from':acc2})
	clauseOption.startOption(acc1, 1234, 4, 1, 5, {'from':acc2})
	assert ERC1400.partitions(1234)[3] == 1
	clauseOption.recipientDeny(1234, {'from':acc1})
	assert ERC1400.partitions(1234)[3] == 0
	assert ERC20FixedSupply.balanceOf(acc1) == b1 - 1
