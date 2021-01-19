pragma solidity ^0.6.0;

import "interfaces/my_IERC20.sol";
import "interfaces/my_IERC1400.sol";

contract clauseSellorbuy {

	// déclaration des différents de l'avis de vente
	enum sellorbuyStates {
		STATUS_UNUSED,  // par défaut : 0
		STATUS_PENDING,  
		STATUS_CLOSED 
	}

	// Represents a notice of sale parameters
    struct NoticeSale {
		address offerer;    // actionnaire offrant
		address remainer;   // actionnaire restant
		uint256 pricePurchase;
		uint256 expirationDate;
		sellorbuyStates status;
    }

    // Mapping from partition UID to Option
    mapping ( address => NoticeSale ) public notices;

	IERC1400 public tokenStock;   // token qui représente la partition (ERC1410)
	IERC20 public tokenPayment;   // token qui représente le coin (ERC20)

	constructor(address _tokenStockAddress, address _tokenPaymentAddress) public {
	    require(_tokenStockAddress != address(0));
		require(_tokenPaymentAddress != address(0));

		tokenStock = IERC1400(_tokenStockAddress);
		tokenPayment = IERC20(_tokenPaymentAddress);
	}


	//------------------------------------------------------------
	// Sell or Buy events
	//------------------------------------------------------------

	event StartSellorbuy(address offerer, address remainer, address escrow, uint256 pricePurchase, uint256 endDate);

	//------------------------------------------------------------
	// Sell or Buy functions
	//------------------------------------------------------------

	// The offerer initiates the Notice of Sale on all the partitions of the remainer

	function startSellorbuy(address remainer, uint256 pricePurchase, uint256 duration) public returns (bool){
		uint i=0;
		uint256 nbPartition;
		nbPartition = tokenStock.getHolderNbuid(remainer);
		require(nbPartition > 0);
		uint256[] memory uidList = new uint256[](nbPartition);
		uidList = tokenStock.partitionsOf(remainer);

		for(i=0; i<nbPartition; i++) {
			require(tokenStock.getPartitionStatus(uidList[i]) != 1, "Les partitions ne doivent être STATUS_CONFINED, soit 1");
		}

		require(pricePurchase >= tokenStock.balanceOf(remainer), "Le prix de l'exercice doit être supérieur ou égal à la valeur des partitions détenues par l'actionnaire restant (remainer)");

		require(duration > 0, "la durée d'un avis de vente est exprimée en jours");
		require(tokenPayment.balanceOf(msg.sender) >= pricePurchase, "L'actionnaire offrant (offerer) doit posséder suffisamment de token pour acquérir les partitions de l'actionnaire restant (remainer)");

		require(notices[remainer].status != sellorbuyStates.STATUS_PENDING, "Il ne peut pas y avoir un avis de vente en cours sur les partitions du remainer");
		require(notices[msg.sender].status != sellorbuyStates.STATUS_PENDING, "Il ne peut pas y avoir un avis de vente en cours sur les partitions de l'actionnaire offrant (offerer)");

		notices[remainer].offerer = msg.sender;
		notices[remainer].remainer = remainer;
        notices[remainer].pricePurchase = pricePurchase;
		notices[remainer].expirationDate = now + duration * 1 days;
		notices[remainer].status = sellorbuyStates.STATUS_PENDING;

		// the offerer sends previously a transaction to ERC1400 to approve EscrowAccount on all its partitions (in case of remainer deny)
		nbPartition = tokenStock.getHolderNbuid(msg.sender);
		uidList = tokenStock.partitionsOf(msg.sender);

		for(i=0; i<nbPartition; i++) {
			require(tokenStock.allowanceEscrow(msg.sender, address(this), uidList[i]) >= tokenStock.getPartitionAmount(uidList[i]), "le contract de séquestre doit être autorisé à modifier le status de toutes les partitions de l'actionnaire offrant (offerer)");
		}

		// the offerer sends previously a transaction to ERC20 to approve EscrowAccount for the transfer of the priceDelta (in case of remainer accept)
		uint256 priceDelta;
		priceDelta = pricePurchase - tokenStock.balanceOf(remainer);
		require(tokenPayment.allowance(msg.sender, address(this)) >= priceDelta);

		// Transfer partitions[partitionUid].owner vers sequestre (address(this)) sur contract ERC1400
		// changement status partition en CONFINED (pas de chgt de owner)
		// mise à jour de la variable mapping escrows (fait sur le contract ERC1400)	
		uint256 endDate = now + duration * 1 days;

		//tokenStock.confinePartition(msg.sender, recipient, partitionUid, endDate, priceExercise);
		// the promisor is the origin (msg.sender) of the transactions call
		for(i=0; i<nbPartition; i++) {
			tokenStock.confinePartition(msg.sender, uidList[i], endDate, tokenStock.getPartitionAmount(uidList[i]));
		}

		emit StartSellorbuy(msg.sender, remainer, address(this), pricePurchase, endDate);
		return true;
	}

	// TODO : public for debug only - SHOULD be private
	function deconfine(address holder) public returns (bool){
		uint i;
		uint256 nbPartition;
		nbPartition = tokenStock.getHolderNbuid(holder);
		require(nbPartition > 0);

		uint256[] memory uidList = new uint256[](nbPartition);
		uidList = tokenStock.partitionsOf(holder);

		for(i=0; i<nbPartition; i++) {
			tokenStock.deconfinePartition(holder, uidList[i]);
		}
		return true;
	}


	// The remainer accepts during the notice of sale duration
	// The partitions are transfered from remainer to offerer
	function remainerAccept() public returns (bool){
		address offerer = notices[msg.sender].offerer;
		require(msg.sender == notices[msg.sender].remainer);
		require(tokenPayment.balanceOf(offerer) >= notices[msg.sender].pricePurchase);
		require(now <= notices[msg.sender].expirationDate);
		require(notices[msg.sender].status == sellorbuyStates.STATUS_PENDING);

		// le remainer doit avoir mis au préalable une allowance sur chacune de ses partitions pour autoriser le transfert
		uint i=0;
		uint256 nbPartition;
		nbPartition = tokenStock.getHolderNbuid(msg.sender);
		require(nbPartition > 0);

		uint256[] memory uidList = new uint256[](nbPartition);
		uidList = tokenStock.partitionsOf(msg.sender);

		// le offerer doit avoir mis au préalable une allowance sur le contract ERC20 pour autoriser le débit du coût priceDelta lié à l'exercice
		uint256 priceDelta;
		priceDelta = notices[msg.sender].pricePurchase - tokenStock.balanceOf(msg.sender);
		require(tokenPayment.allowance(offerer, address(this)) >= priceDelta);

		// Transfer des partitions au coût de pricePurchase de msg.sender vers offerer
		for(i=0; i<nbPartition; i++) {
			require(tokenStock.allowanceEscrow(msg.sender, address(this), uidList[i]) >= tokenStock.getPartitionAmount(uidList[i]));
			tokenStock.escrowExplicitTransfer(msg.sender, offerer, tokenStock.getPartitionAmount(uidList[i]), uidList[i]);
		}

		tokenPayment.transferFrom(offerer, msg.sender, priceDelta);
		notices[msg.sender].status = sellorbuyStates.STATUS_CLOSED;

		// on déconfine les partitions de offerer
		//require(deconfine(offerer) == true);

		// l'avis de vente est clos
		notices[msg.sender].status = sellorbuyStates.STATUS_CLOSED;

		return true;
	}

	// The remainer denies during the notice of sale duration
	// The partitions are transfered from offerer to remainer
	function remainerDeny() public returns (bool){
		address offerer = notices[msg.sender].offerer;
		require(msg.sender == notices[msg.sender].remainer);
		require(tokenPayment.balanceOf(notices[msg.sender].remainer) >= notices[msg.sender].pricePurchase);
		require(now <= notices[msg.sender].expirationDate);
		require(notices[msg.sender].status == sellorbuyStates.STATUS_PENDING);

		// Les partitions de offerer doivent être en séquestre
		uint i=0;
		uint256 nbPartition;
		nbPartition = tokenStock.getHolderNbuid(offerer);
		require(nbPartition > 0);

		uint256[] memory uidList = new uint256[](nbPartition);
		uidList = tokenStock.partitionsOf(offerer);

		for (i=0; i<nbPartition; i++) {
			require(tokenStock.getPartitionStatus(uidList[i]) == 1, "les partitions de l'offerer doivent être en séquestre - STATUS_CONFINED is 1");
		}

		// le remainer doit avoir mis au préalable une allowance sur le contrat ERC20 pour permettre le paiement des partitions
		uint256 priceDelta;
		priceDelta = notices[msg.sender].pricePurchase - tokenStock.balanceOf(offerer);
		require(tokenPayment.allowance(msg.sender, address(this)) >= priceDelta);

		// Transfer des partitions au coût de pricePurchase de offerer vers msg.sender
		for(i=0; i<nbPartition; i++) {
			require(tokenStock.allowanceEscrow(offerer, address(this), uidList[i]) >= tokenStock.getPartitionAmount(uidList[i]));
			tokenStock.escrowExplicitTransfer(offerer, msg.sender, tokenStock.getPartitionAmount(uidList[i]), uidList[i]);
			// on déconfine les partitions de offerer
			tokenStock.deconfinePartition(offerer, uidList[i]);
		}

		tokenPayment.transferFrom(msg.sender, offerer, priceDelta);
		
		// l'avis de vente est clos
		notices[msg.sender].status = sellorbuyStates.STATUS_CLOSED;

		return true;
	}

	// The controller forces the transfer after the notice of sale duration
	// The partitions are transfered from remainer to offerer (or controller)
	function controllerForce(address remainer) public returns (bool){
		require(notices[remainer].status == sellorbuyStates.STATUS_PENDING);
		require(now > notices[remainer].expirationDate);

		// le offerer doit avoir positionné une allowance sur ERC20, sinon le transfert est effectué sur le compte du controller
		uint256 priceDelta;
		priceDelta = notices[remainer].pricePurchase - tokenStock.balanceOf(remainer);
		require(tokenPayment.allowance(remainer, address(this)) >= priceDelta);

		// Le controller transfert les partitions de remainer vers offerer
		uint i=0;
		uint256 nbPartition;
		nbPartition = tokenStock.getHolderNbuid(remainer);
		require(nbPartition > 0);

		uint256[] memory uidList = new uint256[](nbPartition);
		uidList = tokenStock.partitionsOf(remainer);

		for (i=0; i<nbPartition; i++) {
			tokenStock.controllerTransfer(remainer, notices[remainer].offerer, tokenStock.getPartitionAmount(uidList[i]), uidList[i]);

			// on déconfine les partitions de offerer
			tokenStock.deconfinePartition(notices[remainer].offerer, uidList[i]);
		}
		
		// l'avis de vente est clos
		notices[remainer].status = sellorbuyStates.STATUS_CLOSED;
		return true;
	}

}
