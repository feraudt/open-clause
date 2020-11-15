from brownie import accounts

acc0 = accounts.load('acc0')
acc1 = accounts.load('acc1')
acc2 = accounts.load('acc2')

# contract container
ERC20
ERC20FixedSupply
ERC1410

# on deploie le contrat de paiement ERC20
ERC20FixedSupply.deploy({'from':acc0})

ERC20FixedSupply[0].address
### '0x06b67fa799de9CaE96Ab9e62C127B090B6bD57fc'

# transfer 20 tokens vers account#1
ERC20FixedSupply[0].transfer(acc1, 20)
ERC20FixedSupply[0].balanceOf(acc1)
### out : 20

# transfer 20 tokens vers account#1
ERC20FixedSupply[0].transfer(acc2, 20)
ERC20FixedSupply[0].balanceOf(acc2)
### out : 20

# on déploie le contract my_ERC1410 : c'est le contract ERC20FixedSupply qui est utilisé pour les paiements
ERC1410.deploy(ERC20FixedSupply[0].address, {'from':acc0})

ERC1410[0].address
### ''0x1BbDe47982ac6dEB4E752a4DFF32Cb70DF8e5C18

# account#1 autorise le contract ERC1410 à acquérir 5 tokens
ERC20FixedSupply[0].approve(ERC1410[0].address, 5, {'from':acc1})
ERC20FixedSupply[0].allowance(acc1, ERC1410[0].address)
### out : 5

# account#1 s'enregistre sur le contract ERC1410
ERC1410[0].registerAccount({'from':acc1})
ERC1410[0].holders(acc1)
### out : (0, 0)

# account#2 s'enregistre sur le contract ERC1410
ERC1410[0].registerAccount({'from':acc2})
ERC1410[0].holders(acc2)
### out : (0, 0)

# account#1 achète une partition ERC1410 de 2 tokens
ERC1410[0].buyPartition(1234, 2, {'from':acc1})
ERC1410[0].buyPartition(5678, 3, {'from':acc1})

ERC1410[0].partitions(1234)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 2, 1604857751, 1)
ERC1410[0].partitions(5678)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 3, 1605395533, 1)
ERC20FixedSupply[0].balanceOf(acc1)
### out : 15
ERC1410[0].holders(acc1)
### out : (2, 0)
ERC1410[0].partitionsOf(acc1)
### out : (1234, 5678)
ERC1410[0].uids(acc1, 1)
### out : 1234
ERC1410[0].balanceOf(acc1)
### out : 5

# account#1 vend la partition 1234 --->>> A REVOIR ###################
ERC1410[0].sellPartition(1234, {'from':acc1})

ERC1410[0].partitions(1234)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 0, 1605475602, 2)
ERC20FixedSupply[0].balanceOf(acc1)
### out : 15  WARNING le résultat attendu est 17 (et non 15)
ERC1410[0].uids(acc1, 1)

# account#1 transfert sa partition 5678 à account#2 pour 3 tokens
# au préalable, account#2 autorise le contract ERC1410 à débiter son compte de 3 tokens
ERC20FixedSupply[0].approve(ERC1410[0].address, 3, {'from':acc2})
ERC1410[0].transferByPartition(5678, acc2, 3 , {'from':acc1})

ERC1410[0].partitionsOf(acc1)
### out : (0, 0)
ERC1410[0].partitionsOf(acc2)
### out : (5678)




