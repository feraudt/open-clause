pour lancer pytest avec l'option -s (affichage de print()) :

	$ brownie test -s

	Brownie v1.11.10 - Python development framework for Ethereum

	============================================================ test session starts ============================================================
	platform linux -- Python 3.6.8, pytest-6.0.1, py-1.9.0, pluggy-0.13.1 -- /usr/bin/python3
	cachedir: .pytest_cache
	hypothesis profile 'brownie-verbose' -> verbosity=2, deadline=None, max_examples=50, stateful_step_count=10, report_multiple_bugs=False, database=DirectoryBasedExampleDatabase(PosixPath('/home/ptl/.brownie/hypothesis'))
	rootdir: /home/ptl/solidity/clausier/workspace
	plugins: eth-brownie-1.11.10, web3-5.11.1, hypothesis-5.35.0, forked-1.3.0, xdist-1.34.0, timeout-1.0.0
	collected 38 items                                                                                                                          

	Launching 'ganache-cli --port 8545 --gasLimit 12000000 --accounts 10 --hardfork istanbul --mnemonic brownie'...

	tests/test_clause_forward.py::test_address <span style="color:yellow">some RUNNING text</span>
	account[0] :
	Enter the password to unlock this account:
	clauseForward.address =  0x1BbDe47982ac6dEB4E752a4DFF32Cb70DF8e5C18
	tests/test_clause_forward.py::test_address PASSED
	tests/test_clause_forward.py::test_register_holders RUNNING
	account[1] :
	Enter the password to unlock this account:
	account[2] :
	Enter the password to unlock this account:
	tests/test_clause_forward.py::test_register_holders PASSED
	tests/test_clause_forward.py::test_register_escrow PASSED
	tests/test_clause_forward.py::test_erc20_transfer PASSED
	tests/test_clause_forward.py::test_allow_erc1400 PASSED
	tests/test_clause_forward.py::test_buy_part_erc1400 PASSED
	tests/test_clause_forward.py::test_allow_sale PASSED
	tests/test_clause_forward.py::test_start_sale PASSED
	tests/test_clause_forward.py::test_launch_sale PASSED

	tests/test_clause_option.py::test_address RUNNING
	account[0] :
	Enter the password to unlock this account:
	ERC1400.address =  0x4533C5E890e4a51c1a35B9CdAdd9dCF9c1e70b43
	clauseOption.address =  0x695B0E07A920398fAf49894e323eFd39c4529F7d
	tests/test_clause_option.py::test_address PASSED
	tests/test_clause_option.py::test_register_holders RUNNING
	account[1] :
	Enter the password to unlock this account:
	account[2] :
	Enter the password to unlock this account:
	tests/test_clause_option.py::test_register_holders PASSED
	tests/test_clause_option.py::test_register_escrow PASSED
	tests/test_clause_option.py::test_erc20_transfer PASSED
	tests/test_clause_option.py::test_init_allowance PASSED
	tests/test_clause_option.py::test_allow_erc1400 PASSED
	tests/test_clause_option.py::test_buy_part_erc1400 PASSED
	tests/test_clause_option.py::test_allow_option PASSED
	tests/test_clause_option.py::test_start_option PASSED
	tests/test_clause_option.py::test_accept PASSED
	tests/test_clause_option.py::test_deny PASSED

	tests/test_clause_preemption.py::test_address RUNNING
	account[0] :
	Enter the password to unlock this account:
	clausePreemption.address =  0x8D7C91c13f496efF9C7cE6561ACF0fbC0760474E
	tests/test_clause_preemption.py::test_address PASSED
	tests/test_clause_preemption.py::test_register_holders RUNNING
	account[1] :
	Enter the password to unlock this account:
	account[2] :
	Enter the password to unlock this account:
	account[3] :
	Enter the password to unlock this account:
	account[4] :
	Enter the password to unlock this account:
	tests/test_clause_preemption.py::test_register_holders PASSED
	tests/test_clause_preemption.py::test_register_escrow PASSED
	tests/test_clause_preemption.py::test_erc20_transfer PASSED
	tests/test_clause_preemption.py::test_allow_erc1400 PASSED
	tests/test_clause_preemption.py::test_buy_part_erc1400 PASSED
	tests/test_clause_preemption.py::test_start_preemption PASSED
	tests/test_clause_preemption.py::test_notice PASSED
	tests/test_clause_preemption.py::test_responses PASSED
	tests/test_clause_preemption.py::test_transfer PASSED

	============================================================ 10 passed in 27.96s ============================================================
	Terminating local RPC client...
