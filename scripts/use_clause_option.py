from brownie import accounts

# contract container
ERC20
ERC20FixedSupply
ERC1400
clauseOption


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

# on deploie le contrat d'option
clauseOption.deploy(ERC1400[0].address, ERC20FixedSupply[0].address, {'from':acc0})

clauseOption[0].address
### out : '0x1BbDe47982ac6dEB4E752a4DFF32Cb70DF8e5C18'


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
ERC1400[0].registerEscrow(clauseOption[0].address, {'from':acc0})

ERC1400[0].holders(clauseOption[0].address)
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
### Clause d'option
###--------------------------------


# Bob autorise le contract d'option à débiter son compte de 1 tokens ERC20 : c'est le prix de l'option
ERC20FixedSupply[0].approve(clauseOption[0].address, 1, {'from':acc2})

# Alice autorise le contract d'option à modifier le status de sa partition
ERC1400[0].approveEscrow(clauseOption[0].address, 1234, 3, {'from':acc1})

# Alice (account#1) initie un droit d'option :
#	- sur sa partition 1234
#	- pour le bénéficiaire Bob (account#2)
#	- au prix d'exercice de 3 tokens (> au montant de 2 tokens de la partition)
#	- le coût de l'option est de 1 tokens
#	- la durée de l'option est de 2 jours
clauseOption[0].startOption(acc2, 1234, 3, 1, 2, {'from':acc1})

clauseOption[0].options(1234)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", "0x034C935853f5cbE76169d5c643Ac0657fDC50DFf", 1, 3, 1606852265, 1)

ERC1400[0].partitions(1234)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 2, 1606679412, 1)

ERC1400[0].confined(1234)
### out : ("0x1BbDe47982ac6dEB4E752a4DFF32Cb70DF8e5C18", 1606852265, 3)

# -> dans la durée des deux jours, Bob accepte l'achat de la partition
# Bob autorise le contract ERC1400 à débiter son compte de 4 tokens ERC20 : c'est le prix de l'exercice
ERC20FixedSupply[0].approve(ERC1400[0].address, 3, {'from':acc2})

# Bob indique son accord sur le contract d'option
clauseOption[0].recipientAccept(1234, {'from':acc2})

ERC1400[0].partition(1234)
### out :

ERC1400[0].confined(1234)
### out :










