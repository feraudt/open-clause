# open-clausier

## présentation des clauses

### clause à terme

### clause de préemption

### clause d'exclusion

### clause d'option

### clause sell or buy

## hypothèses de développement

Aucun token n'est créé. Les tokens sont gérés par le smart contract ERC20, accessible à tous les utilisateurs.
Le smart contract ERC1400 gère les actions (partitions) pour un groupe d'utilisateurs enregistrés (autorisés).
Les mouvements des token sont effectués sur le smart contract ERC20.
Les transfert, acquisition, vente, confinement de partitions sont effectués sur le smart contract ERC1400.

Pour mettre en oeuvre les clauses sous forme de smart contracts et permettre leur exécution automatique, un groupe d'utilisateurs doit être enregistré sur un smart contract ERC1400 représentant les actions de leur entreprise. Pour permettre l'acquisition d'actions, une méthode d'achat de partitions est implémentée. D'autres techniques d'acquisition de partitions pourront être mises en oeuvre selon les cas d'usage considérés.

Les smart contracts codant l'exécution automatique des clauses sont enregistrés avec le rôle "d'escrow" sur le smart contract ERC1400. Les utilisateurs lui délèguent la possibilité d'agir sur une de leur partition dans le cadre des méthodes définies dans le smart contract et pour un temps déterminé.

Nous avons fait le choix d'implémenter le séquestre d'une partition sous la forme d'un confinement. Cela présente l'avantage de conserver la partition sur le compte de son possesseur. En revanche, celui-ci ne peut pas agir dessus pendant la durée du confinement. C'est le smart contract "d'escrow" qui lève le séquestre, en déconfinant la partition lorsque les conditions de la clause sont réunies.

## composants de la librairie

![Image](./sources/lib_smart_contract.png)

## scénarios

### clause d'option

![Image](./sources/sequence_clause_option_commente.png)

## tests

   $ brownie test -s
