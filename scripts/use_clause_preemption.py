
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
clausePreemption.deploy(ERC1400[0].address, ERC20FixedSupply[0].address, {'from':acc0})

clausePreemption[0].address
### out : '0x1BbDe47982ac6dEB4E752a4DFF32Cb70DF8e5C18'


###----------------------------------------------------------
### Enregistrements des comptes sur le smart contract ERC1400
###----------------------------------------------------------

acc1 = accounts.load('acc1')  # Holder : Alice
acc2 = accounts.load('acc2')  # Holder : Bob
acc3 = accounts.load('acc3')  # Holder : Charles
acc4 = accounts.load('acc4')  # Holder : Dave
acc5 = accounts.load('acc5')  # Holder : Esther

# account#1 s'enregistre sur le contract ERC1400
ERC1400[0].registerAccount({'from':acc1})
ERC1400[0].holders(acc1)
### out : (0, 0)

# account#2 s'enregistre sur le contract ERC1400
ERC1400[0].registerAccount({'from':acc2})
ERC1400[0].holders(acc2)
### out : (0, 0)

# account#3 s'enregistre sur le contract ERC1400
ERC1400[0].registerAccount({'from':acc3})
ERC1400[0].holders(acc3)
### out : (0, 0)

# account#4 s'enregistre sur le contract ERC1400
ERC1400[0].registerAccount({'from':acc4})
ERC1400[0].holders(acc4)
### out : (0, 0)

# account#5 s'enregistre sur le contract ERC1400
ERC1400[0].registerAccount({'from':acc5})
ERC1400[0].holders(acc5)
### out : (0, 0)

# account#0 enregistre l'adresse du smart contract clausePreemption comme séquestre sur le contract ERC1400
ERC1400[0].registerEscrow(clausePreemption[0].address, {'from':acc0})

ERC1400[0].holders(clausePreemption[0].address)
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

# transfer 20 tokens vers account#3 (Holder : Charles)
ERC20FixedSupply[0].transfer(acc3, 20)
ERC20FixedSupply[0].balanceOf(acc3)
### out : 20

# transfer 20 tokens vers account#4 (Holder : Dave)
ERC20FixedSupply[0].transfer(acc4, 20)
ERC20FixedSupply[0].balanceOf(acc4)
### out : 20

# transfer 20 tokens vers account#5 (Holder : Esther)
ERC20FixedSupply[0].transfer(acc5, 20)
ERC20FixedSupply[0].balanceOf(acc5)
### out : 20

# account#1 autorise le contract ERC1400 à débiter son compte de 5 tokens
ERC20FixedSupply[0].approve(ERC1400[0].address, 5, {'from':acc1})
ERC20FixedSupply[0].allowance(acc1, ERC1400[0].address)
### out : 5

# account#1 achète deux partitions ERC1400, l'une de 2 tokens, l'autre de 3 tokens
ERC1400[0].buyPartition(1114, 2, {'from':acc1})
ERC1400[0].buyPartition(1118, 3, {'from':acc1})

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

# account#2 autorise le contract ERC1400 à débiter son compte de 5 tokens
ERC20FixedSupply[0].approve(ERC1400[0].address, 5, {'from':acc2})
ERC1400[0].buyPartition(2224, 2, {'from':acc2})
ERC1400[0].buyPartition(2228, 3, {'from':acc2})

# account#3 autorise le contract ERC1400 à débiter son compte de 5 tokens
ERC20FixedSupply[0].approve(ERC1400[0].address, 5, {'from':acc3})
ERC1400[0].buyPartition(3334, 2, {'from':acc3})
ERC1400[0].buyPartition(3338, 3, {'from':acc3})

# account#4 autorise le contract ERC1400 à débiter son compte de 5 tokens
ERC20FixedSupply[0].approve(ERC1400[0].address, 5, {'from':acc4})
ERC1400[0].buyPartition(4444, 2, {'from':acc4})
ERC1400[0].buyPartition(4448, 3, {'from':acc4})

# account#5 autorise le contract ERC1400 à débiter son compte de 5 tokens
ERC20FixedSupply[0].approve(ERC1400[0].address, 5, {'from':acc5})
ERC1400[0].buyPartition(5554, 2, {'from':acc5})
ERC1400[0].buyPartition(5558, 3, {'from':acc5})

###--------------------------------
### Clause de preemption
###--------------------------------


# Alice (account#1) initie un droit de preemption au bénéfice de Dave :
#	- pour le bénéficiaire Dave (account#4)
#	- la durée de la preemption est de 60 minutes

# Alice lance la preemption au bénéfice de Dave
clausePreemption[0].startPreemption(acc4, 60, {'from':acc1})

clausePreemption[0].preemptions(acc1, 0)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", "0x9B42E5fB86b55Dc6E2D71F13E98eeeD0a9927736", 1613588647)

ERC1400[0].partitions(1114)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", 2, 1613584969, 0)

# Alice (account#1) initie un droit de preemption au bénéfice de Dave :
#	- pour le bénéficiaire Dave (account#4)
#	- la durée de la preemption est de 60 minutes

# Alice lance la preemption au bénéfice de Esther
clausePreemption[0].startPreemption(acc5, 60, {'from':acc1})

clausePreemption[0].preemptions(acc1, 1)
### out :

# Alice notifie Dave de l'intention de vendre sa partition 1114
#	- pour le bénéficiaire Dave (account#4)
#   - sur la partition 1114
#   - le coût de la preemption est de 2 tokens
#	- la validité de l'avis est de 10 minutes

# Alice autorise le contract de preemption à modifier le status de sa partition 114
ERC1400[0].approveEscrow(clausePreemption[0].address, 1114, 2, {'from':acc1})

# Alice notifie Dave de l'intention de vendre sa partition 1114
clausePreemption[0].launchNotice(acc4, 1114, 2, 10, {'from':acc1})

# Alice notifie Esther de l'intention de vendre sa partition 1114
clausePreemption[0].launchNotice(acc5, 1114, 2, 10, {'from':acc1})

clausePreemption[0].responses(acc4, 1114)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", "0x9B42E5fB86b55Dc6E2D71F13E98eeeD0a9927736", 1114, 2, 1613586276, 0, False)
clausePreemption[0].responses(acc5, 1114)
### out :

# Dave indique sa décision : il accepte
clausePreemption[0].recipientDecision(1114, 1, {'from':acc4})
clausePreemption[0].responses(acc4, 1114)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", "0x9B42E5fB86b55Dc6E2D71F13E98eeeD0a9927736", 1114, 2, 1613586276, 1613586121, True)

# Esther indique sa décision : elle accepte
clausePreemption[0].recipientDecision(1114, 1, {'from':acc5})
clausePreemption[0].responses(acc5, 1114)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", "0xfE9edba85a709f35E42Caed3b7697004b51754d4", 1114, 2, 1613653542, 1613656508, 1613652978, True)

# Alice choisit de transférer sa partition à Dave
# Dave autorise le contract ERC1400 à débiter son compte de 2 tokens ERC20 : c'est le coût de la preemption
ERC20FixedSupply[0].approve(clausePreemption[0].address, 2, {'from':acc4})
# Dave autorise le contract ERC1400 à débiter son compte de 2 tokens ERC20 : c'est le coût de la partition 1114
ERC20FixedSupply[0].approve(ERC1400[0].address, 2, {'from':acc4})

clausePreemption[0].launchTransfer(acc4, 1114, {'from':acc1})

# Alice notifie Esther de l'intention de vendre sa partition 1118
#	- pour le bénéficiaire Esther (account#5)
#   - sur la partition 1118
#   - le coût de la preemption est de 2 tokens
#	- la validité de l'avis est de 10 minutes

# Alice autorise le contract de preemption à modifier le status de sa partition 114
ERC1400[0].approveEscrow(clausePreemption[0].address, 1118, 3, {'from':acc1})

# Alice notifie Dave de l'intention de vendre sa partition 1118
clausePreemption[0].launchNotice(acc4, 1118, 2, 10, {'from':acc1})

# Alice notifie Esther de l'intention de vendre sa partition 1118
clausePreemption[0].launchNotice(acc5, 1118, 2, 10, {'from':acc1})

clausePreemption[0].responses(acc5, 1118)
### out :

# Esther indique sa décision : elle refuse
clausePreemption[0].recipientDecision(1118, 0, {'from':acc5})
clausePreemption[0].responses(acc5, 1118)
### out : ("0xF800DeBE778aA16295AEF005db9c85aD4293DfA0", "0xfE9edba85a709f35E42Caed3b7697004b51754d4", 1118, 2, 1613656313, 1613659205, 1613655723, False)

# Dave indique sa décision : il refuse
clausePreemption[0].recipientDecision(1118, 0, {'from':acc4})
clausePreemption[0].responses(acc4, 1118)

# Alice décide de vendre sa partition à Bob qui n'est pas un bénéficiaire
# Bob autorise le contract ERC1400 à débiter son compte de 3 tokens ERC20 : c'est le coût de la partition 1118
ERC20FixedSupply[0].approve(ERC1400[0].address, 3, {'from':acc2})

ERC1400[0].transferByPartition(1118, acc2, 3, {'from':acc1})

# Eclusion du compte de Alice
ERC1400[0].unRegisterAccount(acc1, {'from':acc0})
