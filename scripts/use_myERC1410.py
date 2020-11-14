from brownie import accounts

acc0 = accounts.load('acc0')

# contract container
ERC20
ERC20FixedSupply
ERC1410

# on deploie le contrat de paiement ERC20
ERC20FixedSupply.deploy({'from':acc0})

ERC20FixedSupply[0].address
### '0x06b67fa799de9CaE96Ab9e62C127B090B6bD57fc'

# transfer 10 tokens vers account#1
acc1 = accounts.load('acc1')
ERC20FixedSupply[0].transfer(acc1, 10)
ERC20FixedSupply[0].balanceOf(acc1)
### out : 10

# on déploie le contract my_ERC1410 : c'est le contract ERC20FixedSupply qui est utilisé pour les paiements
ERC1410.deploy(ERC20FixedSupply[0].address, {'from':acc0})

ERC1410[0].address
### ''0x1BbDe47982ac6dEB4E752a4DFF32Cb70DF8e5C18

# account#1 autorise le contract ERC1410 à acquérir 5 tokens
ERC20FixedSupply[0].approve(ERC1410[0].address, 5, {'from':acc1})
ERC20FixedSupply[0].allowance(acc1, ERC1410[0].address)
### out : 5

# account#1 achète une partition ERC1410 de 2 tokens
ERC1410[0].registerAccount({'from':acc1})
ERC1410[0].nbUid(acc1)
### out : 0

ERC1410[0].buyPartition(1234, 2, {'from':acc1})
ERC1410[0].buyPartition(5678, 1, {'from':acc1})

ERC1410[0].partitions(1234)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 2, 1604857751, 1)
ERC1410[0].partitions(5678)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 1, 1605395533, 1)
ERC20FixedSupply[0].balanceOf(acc1)
### out : 7
ERC1410[0].nbUid(acc1)
### out : 2
ERC1410[0].partitionsOf(acc1)
### out : (1234, 5678)
ERC1410[0].uids(acc1, 1)
### out : 1234


