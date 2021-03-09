pragma solidity ^0.6.0;

import "interfaces/my_IERC20.sol";
import "interfaces/my_IERC1400.sol";

contract clauseForward {

	// déclaration des différents états d'une vente à terme
	enum forwardStates {
		STATUS_UNUSED,  // par défaut : 0
		STATUS_PENDING,
		STATUS_CLOSED
	}

	// Represents a forward sale parameters
  struct ForwardSale {
		address seller;
		address recipient;
    uint256 priceForward;
		uint256 expirationDate;
		forwardStates status;
    }

  // Mapping from partition UID to the forward sale
  mapping ( uint256 => ForwardSale) public forwards;

	IERC1400 public tokenStock;   // token qui représente la partition (ERC1410)
	IERC20 public tokenPayment;   // token qui représente le coin (ERC20)
	address tokenStockAddress;

	constructor(address _tokenStockAddress, address _tokenPaymentAddress) public {
	  require(_tokenStockAddress != address(0));
		require(_tokenPaymentAddress != address(0));

		tokenStock = IERC1400(_tokenStockAddress);
		tokenPayment = IERC20(_tokenPaymentAddress);
		tokenStockAddress = _tokenStockAddress;
	}


	//------------------------------------------------------------
	// Forward sale events
	//------------------------------------------------------------

	event StartForwardSale(address indexed _seller, address indexed _recipient, address escrow, uint256 _partitionUid, uint256 _priceForward, uint256 _expirationDate);

	//------------------------------------------------------------
	// Option right functions
	//------------------------------------------------------------

	// The seller initiates the forward sale on a partition he owns

	function startForwardSale(address recipient, uint256 partitionUid, uint256 priceForward, uint256 duration) public returns (bool){
		require(forwards[partitionUid].status != forwardStates.STATUS_PENDING, "Une partition peut être engagée dans une autre vente à terme");
		require(tokenStock.getPartitionOwner(partitionUid) == msg.sender, "Seul le possesseur de la partition peut initier une vente à terme");
		require(tokenStock.getPartitionStatus(partitionUid) == 0, "la partition cible de la vente doit être active - STATUS_ACTIVE is 0");
		require(priceForward >= 0);
		require(duration > 0, "la durée de la vente à terme est exprimée en minutes");
		require(tokenPayment.balanceOf(recipient) >= priceForward + tokenStock.getPartitionAmount(partitionUid));
		require(tokenPayment.allowance(recipient, address(this)) >= priceForward);
		require(tokenPayment.allowance(recipient, tokenStockAddress) >= tokenStock.getPartitionAmount(partitionUid));

		forwards[partitionUid].seller = msg.sender;
		forwards[partitionUid].recipient = recipient;
    forwards[partitionUid].priceForward = priceForward;
		forwards[partitionUid].expirationDate = now + duration * 1 minutes;
		forwards[partitionUid].status = forwardStates.STATUS_PENDING;

		// the seller sends previously a transaction to ERC1400 to approve EscrowAccount on partitionUid for priceExercice
		require(tokenStock.allowanceEscrow(msg.sender, address(this), partitionUid) == true, "le contract de séquestre doit être autorisé à modifier le status de la partition");

		// Transfer partitions[partitionUid].owner vers sequestre (address(this)) sur contract ERC1400
		// changement status partition en CONFINED (pas de chgt de owner)
		// mise à jour de la variable mapping escrows (fait sur le contract ERC1400)
		uint256 endDate = now + duration * 1 minutes;
		tokenStock.confinePartition(recipient, partitionUid, endDate, tokenStock.getPartitionAmount(partitionUid));

		emit StartForwardSale(msg.sender, recipient, address(this), partitionUid, priceForward, endDate);
		return true;
	}


	// The sale is launched

	function launchSale(uint256 partitionUid) public returns (bool){
		require(msg.sender == forwards[partitionUid].recipient || msg.sender == forwards[partitionUid].seller, "la vente peut être déclenchée soit par le vendeur, soit par acheteur");
		require(tokenPayment.balanceOf(forwards[partitionUid].recipient) >= forwards[partitionUid].priceForward + tokenStock.getPartitionAmount(partitionUid));
		require(now >= forwards[partitionUid].expirationDate);
		require(forwards[partitionUid].status == forwardStates.STATUS_PENDING);
		require(tokenStock.getPartitionStatus(partitionUid) == 1, "la partition cible doit être en séquestre - STATUS_CONFINED is 1");

		// la partition est déconfinée
		tokenStock.deconfinePartition(forwards[partitionUid].seller, 1234);

		// Transfer du priceForward sur le contract ERC20
		tokenPayment.transferFrom(forwards[partitionUid].recipient, forwards[partitionUid].seller, forwards[partitionUid].priceForward);

		// Transfer de la partition
		require(tokenStock.allowanceEscrow(forwards[partitionUid].seller, address(this), partitionUid) == true);
		tokenStock.escrowExplicitTransfer(forwards[partitionUid].seller, forwards[partitionUid].recipient, tokenStock.getPartitionAmount(partitionUid), partitionUid);

		forwards[partitionUid].status = forwardStates.STATUS_CLOSED;
		return true;
	}

}
