# open-clausier

environnement de développement et de test des smart contracts du projet :

	https://smart-contracts.univ-grenoble-alpes.fr/

## installer Brownie

le code source de eth-brownie est disponible sur github :

	https://github.com/eth-brownie/brownie

la documentation est disponible sur readthedocs :

	https://eth-brownie.readthedocs.io/en/stable/install.html

eth-brownie utilise l'émulateur ethereum en ligne de commande *ganache-cli* disponible sur github :

	https://github.com/trufflesuite/ganache-cli

## configurer l'environnement

pour utiliser les comptes *accounts* mis à disposition par *ganache-cli*, il faut renseigner leur *private key*, leur donner un nom et leur associer un mot de passe. Pour cela, utiliser la commande :

	$ brownie accounts new <id>

Les *private key* de chacun des 10 comptes *ganache-cli* sont obtenues en lançant *ganache-cli* en ligne de commande :

	$ ganche-cli

Une fois les comptes renseignés, ils apparaissent en format json dans le répertoire $HOME/.brownie/accounts/



## utiliser les smart contracts storeService

pour compiler les smart contracts :

	$ brownie compile

le script *use_storeService.py* est disponible pour tester les smart contrats *storeService_to_account.sol* et *storeService_to_contract.sol*. Pour cela, dérouler les instructions du script dans la console :

	$ brownie console

## utiliser le smart contract my_ERC1400.sol

le script *use_myERC1400.py* est en cours de développement pour tester le smart contract *my_ERC1400.sol*. Les instructions du script fonctionnent et peuvent être lancées dans la console :

	$ brownie console



