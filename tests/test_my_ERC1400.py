import pytest
from brownie import accounts

@pytest.fixture(scope="module")
def acc0():
	print("account[0] : ");
	return accounts.load('acc0')  # Developer

@pytest.fixture(scope="module")
def acc1():
	print("account[1] : ");
	return accounts.load('acc1')  # Holder : Alice

@pytest.fixture(scope="module")
def acc2():
	print("account[2] : ");
	return accounts.load('acc2')  # Holder : Bob

@pytest.fixture(scope="module")
def acc9():
	print("account[9] : ");
	return accounts.load('acc9')  # Controller

def test_transferByPartition(acc0, acc1, acc2, acc9):
	print("mon premier test");
