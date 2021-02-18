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

# on deploie le contrat de vente à terme
clauseForward.deploy(ERC1400[0].address, ERC20FixedSupply[0].address, {'from':acc0})

clauseForward[0].address
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

# account#0 enregistre l'adresse du smart contract clauseOption comme séquestre sur le contract ERC1400
ERC1400[0].registerEscrow(clauseForward[0].address, {'from':acc0})

ERC1400[0].holders(clauseForward[0].address)
### out : (0, 2)


###---------------------
### Achat des partitions
###---------------------

# transfer 20 tokens vers account#1 (Holder : Alice)
ERC20FixedSupply[0].transfer(acc1, 20)
ERC20FixedSupply[0].balanceOf(acc1)
### out : 20

# transfer 20 tokens vers account#2 (Holder : Bob)
ERC20FixedSupply[0].transfer(acc2, 20)
ERC20FixedSupply[0].balanceOf(acc2)
### out : 20

# account#1 autorise le contract ERC1400 à débiter son compte de 5 tokens
ERC20FixedSupply[0].approve(ERC1400[0].address, 5, {'from':acc1})
ERC20FixedSupply[0].allowance(acc1, ERC1400[0].address)
### out : 5

# account#1 achète deux partitions ERC1400, l'une de 2 tokens, l'autre de 3 tokens
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


###--------------------------------
### Clause de vente à terme
###--------------------------------


# Alice (account#1) initie une vente à terme :
#	- sur sa partition 1234
#	- au bénéficiaire Bob (account#2)
#	- pour un coût 3 tokens (en plus du montant de la partition)
#	- le terme est fixé à 2 minutes

# Bob autorise le contract de vente à terme à débiter son compte de 3 tokens ERC20
ERC20FixedSupply[0].approve(clauseForward[0].address, 3, {'from':acc2})

# Bob autorise le contract ERC1400 à débiter son compte de 2 tokens ERC20
ERC20FixedSupply[0].approve(ERC1400[0].address, 2, {'from':acc2})

# Alice autorise le contract de vente à terme à modifier le status de sa partition
ERC1400[0].approveEscrow(clauseForward[0].address, 1234, 2, {'from':acc1})

# Alice initie la vente à terme
clauseForward[0].startForwardSale(acc2, 1234, 3, 2, {'from':acc1})

clauseForward[0].forwards(1234)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", "0x034C935853f5cbE76169d5c643Ac0657fDC50DFf", 3, 1613661080, 1)

ERC1400[0].partitions(1234)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 2, 1613660912, 1)

ERC1400[0].confined(1234)
### out : ("0x1BbDe47982ac6dEB4E752a4DFF32Cb70DF8e5C18", 1613661080, 2, "0x034C935853f5cbE76169d5c643Ac0657fDC50DFf")

# passés les deux minutes correspondant à la durée du terme
# Bob lance la vente
clauseForward[0].launchSale(1234, {'from':acc2})

clauseForward[0].forwards(1234)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", "0x034C935853f5cbE76169d5c643Ac0657fDC50DFf", 3, 1613661080, 2)

ERC1400[0].partitions(1234)
### out : ("0x034C935853f5cbE76169d5c643Ac0657fDC50DFf", 2, 1613660912, 1)
