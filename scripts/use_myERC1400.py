from brownie import accounts

acc0 = accounts.load('acc0')  # Developer
acc1 = accounts.load('acc1')  # Holder : Alice
acc2 = accounts.load('acc2')  # Holder : Bob
acc9 = accounts.load('acc9')  # Controller

# contract container
ERC20
ERC20FixedSupply
ERC1400

# on deploie le contrat de paiement ERC20
ERC20FixedSupply.deploy({'from':acc0})

ERC20FixedSupply[0].address
### '0x06b67fa799de9CaE96Ab9e62C127B090B6bD57fc'

# transfer 20 tokens vers account#1 (Holder : Alice)
ERC20FixedSupply[0].transfer(acc1, 20)
ERC20FixedSupply[0].balanceOf(acc1)
### out : 20

# transfer 20 tokens vers account#2 (Holder : Bob)
ERC20FixedSupply[0].transfer(acc2, 20)
ERC20FixedSupply[0].balanceOf(acc2)
### out : 20

# transfer 20 tokens vers account#9 (Controller)
ERC20FixedSupply[0].transfer(acc9, 20)
ERC20FixedSupply[0].balanceOf(acc9)
### out : 20

# on déploie le contract my_ERC1400 : c'est le contract ERC20FixedSupply qui est utilisé pour les paiements
ERC1400.deploy(ERC20FixedSupply[0].address, 1, {'from':acc0})

ERC1400[0].address
### '0x44011BCaA71EdfB9D89fb0f5AF711334EE1fc9e5'

# account#1 autorise le contract ERC1400 à acquérir 5 tokens
ERC20FixedSupply[0].approve(ERC1400[0].address, 5, {'from':acc1})
ERC20FixedSupply[0].allowance(acc1, ERC1400[0].address)
### out : 5

# account#1 s'enregistre sur le contract ERC1400
ERC1400[0].registerAccount({'from':acc1})
ERC1400[0].holders(acc1)
### out : (0, 0)

# account#2 s'enregistre sur le contract ERC1400
ERC1400[0].registerAccount({'from':acc2})
ERC1400[0].holders(acc2)
### out : (0, 0)

# account#9 s'enregistre sur le contract ERC1400
ERC1400[0].registerAccount({'from':acc9})
ERC1400[0].holders(acc9)
### out : (0, 0)

# account#1 achète une partition ERC1400 de 2 tokens
ERC1400[0].buyPartition(1234, 2, {'from':acc1})
ERC1400[0].buyPartition(5678, 3, {'from':acc1})

ERC1400[0].partitions(1234)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 2, 1604857751, 1)
ERC1400[0].partitions(5678)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 3, 1605395533, 1)
ERC20FixedSupply[0].balanceOf(acc1)
### out : 15
ERC20FixedSupply[0].balanceOf(acc1)
### out : (2, 0)
ERC1400[0].partitionsOf(acc1)
### out : (1234, 5678)
ERC1400[0].uids(acc1, 1)
### out : 1234
ERC1400[0].balanceOf(acc1)
### out : 5

# account#1 vend la partition 1234
ERC1400[0].sellPartition(1234, {'from':acc1})

ERC1400[0].partitions(1234)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 0, 1605475602, 2)
ERC20FixedSupply[0].balanceOf(acc1)
### out : 17
ERC1400[0].uids(acc1, 1)

# account#1 transfert sa partition 5678 à account#2 pour 3 tokens
# au préalable, account#2 autorise le contract ERC1400 à débiter son compte de 3 tokens
ERC20FixedSupply[0].approve(ERC1400[0].address, 3, {'from':acc2})
ERC1400[0].transferByPartition(5678, acc2, 3 , {'from':acc1})

ERC1400[0].partitionsOf(acc1)
### out : (0, 0)
ERC1400[0].partitionsOf(acc2)
### out : (5678)

###--------------------------------
### Intervention du Rôle Controller
###--------------------------------

ERC1400[0].isControllable()
### out : 1 (TRUE)

# Enregistrement de account#9 comme Controller
ERC1400[0].registerController(acc9)
ERC1400[0].holders(acc9)
### out : (0,1)

# le Controller (account#9) force le transfert de la partition 5678 du Bob (account#2) vers Alice (account#1) pour un coût de 4 tokens ERC20
# au préalable, Alice (account#1) autorise le contract ERC1400 à débiter son compte d'au moins 4 tokens
ERC20FixedSupply[0].approve(ERC1400[0].address, 5, {'from':acc1})
ERC20FixedSupply[0].balanceOf(acc1)
### out : 20
ERC20FixedSupply[0].allowance(acc1, ERC1400[0].address)
### out : 5
ERC1400[0].partitions(5678)
### out : ("0x034C935853f5cbE76169d5c643Ac0657fDC50DFf", 3, 1605730123, 0)
###       -> la partition est sur le compte de Bob

ERC1400[0].controllerTransfer(acc2, acc1, 4, 5678, {'from':acc9})

ERC1400[0].partitions(5678)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 3, 1605730123, 0) 
###       -> la partition est sur le compte d'Alice

# le Controller (account#9) rachète la partition 5678 de Alice (account#1) pour un coût de 4 tokens ERC20
# au préalable, le Controller (account#9) autorise le contract ERC1400 à débiter son compte d'au moins 4 tokens
ERC20FixedSupply[0].approve(ERC1400[0].address, 5, {'from':acc9})
ERC1400[0].controllerRedeem(acc1, 4, 5678, {'from':acc9})

ERC1400[0].partitions(5678)
### out : ("0x65f559FBbff6fe58879499b729bE9b185bEB5386", 3, 1605730123, 0)
###       -> la partition est sur le compte du Controller






