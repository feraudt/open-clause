# open-clausier

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

un script est disponible pour tester les smart contrats storeService. Pour cela, lancer :

	$ brownie console


