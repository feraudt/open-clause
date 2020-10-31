from brownie import accounts

acc0 = accounts.load('acc0')

# contract container
ERC20
ERC20FixedSupply

ERC20FixedSupply.deploy({'from':acc0})

ERC20FixedSupply[0].transfer.info()
ERC20FixedSupply[0].balanceOf(acc0)
### out : 1000

acc1 = accounts.load('acc1')
ERC20FixedSupply[0].transfer(acc1, 10)

ERC20FixedSupply[0].balanceOf(acc1)
### out : 10

ERC20FixedSupply[0].address
### '0x06b67fa799de9CaE96Ab9e62C127B090B6bD57fc'

# on déploie le contract StoreServiceContract : c'est le contract qui reçoit les tokens
storeServiceContract.deploy(ERC20FixedSupply[0].address, {'from':acc0})

# on déploie le contract StoreServiceAccount : c'est le compte acc9 qui reçoit les tokens
acc9 = accounts.load('acc9')
storeServiceAccount.deploy(ERC20FixedSupply[0].address, acc9, {'from':acc0})

storeServiceContract[0].address
### '0x1BbDe47982ac6dEB4E752a4DFF32Cb70DF8e5C18'

storeServiceAccount[0].address
### '0xB339f293C5776E65c7FA42e0EbD67d459e571b46'

ERC20FixedSupply[0].approve(storeServiceContract[0].address, 3, {'from':acc1})

ERC20FixedSupply[0].allowance(acc1, storeServiceContract[0].address)
### 3

storeServiceContract[0].storeData(18, {'from':acc1})

ERC20FixedSupply[0].balanceOf(acc1)
### 9
ERC20FixedSupply[0].allowance(acc1, storeServiceContract[0].address)
### 2

storeServiceContract[0].storeData(13, {'from':acc1})

ERC20FixedSupply[0].balanceOf(acc1)
### 8
ERC20FixedSupply[0].allowance(acc1, storeServiceContract[0].address)
### 1

ERC20FixedSupply[0].balanceOf(storeServiceContract[0].address)
### 2


ERC20FixedSupply[0].approve(storeServiceAccount[0].address, 3, {'from':acc1})

ERC20FixedSupply[0].allowance(acc1, storeServiceAccount[0].address)
### 3

storeServiceAccount[0].storeData(98, {'from':acc1})

ERC20FixedSupply[0].balanceOf(acc1)
### 7
ERC20FixedSupply[0].allowance(acc1, storeServiceAccount[0].address)
### 2

storeServiceAccount[0].storeData(13, {'from':acc1})

ERC20FixedSupply[0].balanceOf(acc1)
### 6
ERC20FixedSupply[0].allowance(acc1, storeServiceAccount[0].address)
### 1

ERC20FixedSupply[0].balanceOf(acc9)
### 2

