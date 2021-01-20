from brownie import accounts

# contract container
ERC20
ERC20FixedSupply
ERC1400
clauseSellorbuy


###--------------------------------
### Déploiement des smart contracts
###--------------------------------

acc0 = accounts.load('acc0')  # Developer

# on deploie le contrat de paiement ERC20
ERC20FixedSupply.deploy({'from':acc0})

ERC20FixedSupply[0].address
### '0x06b67fa799de9CaE96Ab9e62C127B090B6bD57fc'

# on déploie le contract my_ERC1400 : c'est le contract ERC20FixedSupply qui est utilisé pour les paiements
ERC1400.deploy(ERC20FixedSupply[0].address, 1, {'from':acc0})

ERC1400[0].address
### '0x44011BCaA71EdfB9D89fb0f5AF711334EE1fc9e5'

# on deploie le contrat Sellorbuy
clauseSellorbuy.deploy(ERC1400[0].address, ERC20FixedSupply[0].address, {'from':acc0})

clauseSellorbuy[0].address
### out :


###----------------------------------------------------------
### Enregistrements des comptes sur le smart contract ERC1400
###----------------------------------------------------------

acc1 = accounts.load('acc1')  # Holder : Alice
acc2 = accounts.load('acc2')  # Holder : Bob

# account#1 s'enregistre sur le contract ERC1400
ERC1400[0].registerAccount({'from':acc1})
ERC1400[0].holders(acc1)
### out : (0, 0)

# account#2 s'enregistre sur le contract ERC1400
ERC1400[0].registerAccount({'from':acc2})
ERC1400[0].holders(acc2)
### out : (0, 0)


###---------------------
### Achat des partitions
###---------------------

# transfer 50 tokens vers account#1 (Holder : Alice)
ERC20FixedSupply[0].transfer(acc1, 50)
ERC20FixedSupply[0].balanceOf(acc1)
### out : 50

# transfer 50 tokens vers account#2 (Holder : Bob)
ERC20FixedSupply[0].transfer(acc2, 50)
ERC20FixedSupply[0].balanceOf(acc2)
### out : 50

# account#1 autorise le contract ERC1400 à débiter son compte de 5 tokens
ERC20FixedSupply[0].approve(ERC1400[0].address, 5, {'from':acc1})
ERC20FixedSupply[0].allowance(acc1, ERC1400[0].address)
### out : 5

# account#1 achète deux partitions ERC1400, l'une de 2 tokens, l'autre de 3 tokens
ERC1400[0].buyPartition(1234, 2, {'from':acc1})
ERC1400[0].buyPartition(5678, 3, {'from':acc1})

ERC1400[0].partitions(1234)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 2, 1610915708, 0)
ERC1400[0].partitions(5678)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 3, 1610915722, 0)
ERC20FixedSupply[0].balanceOf(acc1)
### out : 15
ERC1400[0].partitionsOf(acc1)
### out : (1234, 5678)
ERC1400[0].uids(acc1, 1)
### out : 1234
ERC1400[0].balanceOf(acc1)
### out : 5


# account#2 autorise le contract ERC1400 à débiter son compte de 5 tokens
ERC20FixedSupply[0].approve(ERC1400[0].address, 5, {'from':acc2})
ERC20FixedSupply[0].allowance(acc2, ERC1400[0].address)
### out : 5

# account#2 achète deux partitions ERC1400, l'une de 2 tokens, l'autre de 3 tokens
ERC1400[0].buyPartition(4321, 2, {'from':acc2})
ERC1400[0].buyPartition(8765, 3, {'from':acc2})

ERC1400[0].partitions(4321)
### out : ("0x034C935853f5cbE76169d5c643Ac0657fDC50DFf", 2, 1610915899, 0)
ERC1400[0].partitions(8765)
### out : ("0x034C935853f5cbE76169d5c643Ac0657fDC50DFf", 3, 1610915910, 0)
ERC20FixedSupply[0].balanceOf(acc2)
### out : 15
ERC1400[0].partitionsOf(acc2)
### out : (4321, 8765)
ERC1400[0].uids(acc2, 1)
### out : 4321
ERC1400[0].balanceOf(acc2)
### out : 5

###--------------------------------
### Clause sell or buy
###--------------------------------


# Alice (account#1) initie un avis de vente :
#	- destiné à Bob (account#2)
#	- au prix de 8 tokens (> au montant du total des partitions de 5 tokens)
#	- la durée de l'avis de vente est de 2 jours

# account#0 enregistre l'adresse du smart contract clauseSellorbuy comme séquestre sur le contract ERC1400
ERC1400[0].registerEscrow(clauseSellorbuy[0].address, {'from':acc0})

ERC1400[0].holders(clauseSellorbuy[0].address)
### out : (0, 2)


# Alice autorise le contract clauseSellorbuy à modifier le status de ses partitions
ERC1400[0].approveEscrow(clauseSellorbuy[0].address, 1234, 2, {'from':acc1})
ERC1400[0].approveEscrow(clauseSellorbuy[0].address, 5678, 3, {'from':acc1})

# Alice autorise le contract ERC20 à débiter son compte du coût de l'avis de vente (8 tokens - 5 tokens correspondants à la valeur des partitions)
ERC20FixedSupply[0].approve(clauseSellorbuy[0].address, 3, {'from':acc1})

# Alice lance de l'avis de vente
clauseSellorbuy[0].startSellorbuy(acc2, 8, 2, {'from':acc1})

clauseSellorbuy[0].notices(acc2)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", "0x034C935853f5cbE76169d5c643Ac0657fDC50DFf", 8, 1611089836, 1)

ERC1400[0].partitions(1234)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 2, 1606679412, 1)

ERC1400[0].confined(1234)
### out : ("0x1BbDe47982ac6dEB4E752a4DFF32Cb70DF8e5C18", 1611089836, 2, "0xF800DeBE778aA16295AEF005db9c85aD4293DfA0")

# -> dans la durée des deux jours, Bob accepte la vente de ses partitions
#Alice doit avoir positionner les autorisations avant de lancer l'avis de vente
ERC20FixedSupply[0].allowance(acc1, clauseSellorbuy[0].address)
ERC20FixedSupply[0].allowance(acc1, ERC1400[0].address)
ERC1400[0].allowanceEscrow(acc1, clauseSellorbuy[0].address, 1234)
ERC1400[0].partitions(1234)
### out :

# Bob autorise le contract clauseSellorbuy à modifier le status de ses partitions
ERC1400[0].approveEscrow(clauseSellorbuy[0].address, 4321, 2, {'from':acc2})
ERC1400[0].approveEscrow(clauseSellorbuy[0].address, 8765, 3, {'from':acc2})

# Bob accepte la vente de ses partitions
clauseSellorbuy[0].remainerAccept({'from':acc2})

ERC20FixedSupply[0].balanceOf(acc2)
### out : 16 (20 - priceOption - priceExercise)

ERC1400[0].confined(1234)
### out : ("0x1BbDe47982ac6dEB4E752a4DFF32Cb70DF8e5C18", 1606861993, 3, "0x034C935853f5cbE76169d5c643Ac0657fDC50DFf")


###################
# Test remainerDeny
###################

# account#2 autorise le contract ERC1400 à débiter son compte de 10 tokens
ERC20FixedSupply[0].approve(ERC1400[0].address, 10, {'from':acc2})
ERC20FixedSupply[0].allowance(acc2, ERC1400[0].address)
### out : 5

# Bob (account#2) achète une partition ERC1400 de 10 tokens
ERC1400[0].buyPartition(8888, 10, {'from':acc2})

# Alice (account#1) initie un avis de vente :
#	- destiné à Bob (account#2)
#	- au prix de 8 tokens (> au montant du total des partitions de 5 tokens)
#	- la durée de l'avis de vente est de 2 jours

# Alice autorise le contract clauseSellorbuy à modifier le status de ses partitions
ERC1400[0].approveEscrow(clauseSellorbuy[0].address, 1234, 2, {'from':acc1})
ERC1400[0].approveEscrow(clauseSellorbuy[0].address, 5678, 3, {'from':acc1})
ERC1400[0].approveEscrow(clauseSellorbuy[0].address, 4321, 2, {'from':acc1})
ERC1400[0].approveEscrow(clauseSellorbuy[0].address, 8765, 3, {'from':acc1})

# Alice autorise le contract ERC20 à débiter son compte du coût de l'avis de vente (12 tokens - 10 tokens correspondants à la valeur des partitions)
ERC20FixedSupply[0].approve(clauseSellorbuy[0].address, 2, {'from':acc1})

# Alice lance de l'avis de vente
clauseSellorbuy[0].startSellorbuy(acc2, 12, 2, {'from':acc1})

# Bob autorise le contrat clauseSellorbuy à débiter son compte
ERC20FixedSupply[0].approve(clauseSellorbuy[0].address, 2, {'from':acc2})

# Bob indique son refus de vendre ses partitions et achète celles d'Alice
clauseSellorbuy[0].remainerDeny({'from':acc2})
