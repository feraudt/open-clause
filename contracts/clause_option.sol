pragma solidity ^0.6.0;

import "interfaces/my_IERC20.sol";
import "interfaces/my_IERC1400.sol";

contract clauseOption {

	// déclaration des différents états d'une option
	enum optionStates {
		STATUS_UNUSED,  // par défaut : 0
		STATUS_PENDING,  
		STATUS_CLOSED 
	}

	// Represents an option parameters
    struct OptionRight {
		address promisor;
		address recipient;
        uint256 priceOption;
		uint256 priceExercise;
		uint256 expirationDate;
		optionStates status;
    }

    // Mapping from partition UID to Option
    mapping ( uint256 => OptionRight) public options;

	IERC1400 public tokenStock;   // token qui représente la partition (ERC1410)
	IERC20 public tokenPayment;   // token qui représente le coin (ERC20)

	//address public recipient;     // le bénéficiaire (buyer)
	//address public promisor;  // le promettant (seller)
	//uint256 public priceExercise;  // prix de l'exercice (au moins la valeur de la partition)
	//uint256 public priceOption;    // prix à payer par le bénéficiaire pour le droit d'option
	//uint256 public expirationDate; // date après laquelle le bénéficiaire ne peut plus exercer son droit d'option

	 
	constructor(address _tokenStockAddress, address _tokenPaymentAddress) public {
	    require(_tokenStockAddress != address(0));
		require(_tokenPaymentAddress != address(0));

		tokenStock = IERC1400(_tokenStockAddress);
		tokenPayment = IERC20(_tokenPaymentAddress);
	}


	//------------------------------------------------------------
	// Option right events
	//------------------------------------------------------------

	event StartOption(address indexed _promisor, address indexed _recipient, address escrow, uint256 _partitionUid, uint256 _priceExercise, uint256 _priceOption, uint256 _expirationDate);
	//event Opened(address indexed _recipient, uint256 _priceOption);
	//event Closed(address indexed _promisor, uint256 _amountPayment);


	//------------------------------------------------------------
	// Option right functions
	//------------------------------------------------------------

	// The promisor initiate the Option Exercise on a partition he owns

	function startOption(address recipient, uint256 partitionUid, uint256 priceExercise, uint256 priceOption, uint256 duration) public returns (bool){
		require(options[partitionUid].status != optionStates.STATUS_PENDING, "Une partition peut être l'objet de plusieurs options mais pas simultanément");
		require(tokenStock.getPartitionOwner(partitionUid) == msg.sender, "Seul le promettant peut initier une option");
		require(tokenStock.getPartitionStatus(partitionUid) == 0, "la partition cible de l'option doit être active - STATUS_ACTIVE is 0");
		require(priceExercise > 0);
		require(priceOption > 0);
		require(duration > 0, "la durée d'une option est exprimée en jours");
		require(tokenPayment.balanceOf(recipient) >= priceOption + priceExercise);
		require(tokenPayment.allowance(recipient, address(this)) >= priceOption);

		options[partitionUid].promisor = msg.sender;
		options[partitionUid].recipient = recipient;
        options[partitionUid].priceOption = priceOption;
		options[partitionUid].priceExercise = priceExercise;
		options[partitionUid].expirationDate = now + duration * 1 days;
		options[partitionUid].status = optionStates.STATUS_PENDING;

		// promisor send previously a transaction to ERC1400 to approve EscrowAccount on partitionUid for priceExercice
		require(tokenStock.allowanceEscrow(msg.sender, address(this), partitionUid) >= priceExercise, "le contract de séquestre doit être autorisé à modifier le status de la partition");

		// Transfer partitions[partitionUid].owner vers sequestre (address(this)) sur contract ERC1400
		// changement status partition en CONFINED (pas de chgt de owner)
		// mise à jour de la variable mapping escrows (fait sur le contract ERC1400)	
		uint256 endDate = now + duration * 1 days;
		//tokenStock.confinePartition(msg.sender, recipient, partitionUid, endDate, priceExercise);
		// the promisor is the origin (msg.sender) of the transactions call
		tokenStock.confinePartition(recipient, partitionUid, endDate, priceExercise);

		// Transfer du priceOption sur le contract ERC20
		tokenPayment.transferFrom(recipient, msg.sender, priceOption);
		// recipient doit avoir mis une allowance auparavant et avoir une balanceOf > priceOption

		emit StartOption(msg.sender, recipient, address(this), partitionUid, priceExercise, priceOption, endDate);
		return true;
	}


	// The recipient accepts during the option exercice duration

	function recipientAccept(uint256 partitionUid) public returns (bool){
		require(msg.sender == options[partitionUid].recipient);
		require(tokenPayment.balanceOf(msg.sender) >= options[partitionUid].priceExercise);
		require(now <= options[partitionUid].expirationDate);
		require(options[partitionUid].status == optionStates.STATUS_PENDING);
		require(tokenStock.getPartitionStatus(partitionUid) == 1, "la partition cible de l'option doit être en séquestre - STATUS_CONFINED is 1");

		// Transfer de la partition au coût de priceExercise
		require(tokenStock.allowanceEscrow(options[partitionUid].promisor, address(this), partitionUid) >= options[partitionUid].priceExercise);
		// the recipient is the origin (msg.sender) of the transactions call
		tokenStock.escrowTransfer(options[partitionUid].promisor, options[partitionUid].priceExercise, partitionUid);

		//tokenStock.stopOptionExercise(partitionUid);
		require(tokenStock.stopOptionByRecipient(partitionUid));
		options[partitionUid].status = optionStates.STATUS_CLOSED;
		return true;
	}


	// The recipient denies during the option exercice duration

	function recipientDeny(uint256 partitionUid) public returns (bool){
		require(msg.sender == options[partitionUid].recipient);
		require(now <= options[partitionUid].expirationDate);
		require(options[partitionUid].status == optionStates.STATUS_PENDING);
		require(tokenStock.getPartitionStatus(partitionUid) == 1, "la partition cible de l'option doit être en séquestre - STATUS_CONFINED is 1");

		// levée du séquestre de la partition
		require(tokenStock.stopOptionByRecipient(partitionUid));
		options[partitionUid].status = optionStates.STATUS_CLOSED;
		return true;
	}


	// The promisor stop the option exercice after the expiration date

	function stopOption(uint256 partitionUid) public returns (bool){
		require(msg.sender == options[partitionUid].promisor);
		require(now > options[partitionUid].expirationDate);

		require(tokenStock.stopOptionByPromisor(partitionUid));
		options[partitionUid].status = optionStates.STATUS_CLOSED;
		return true;
	}

	// Help to debug
	function isOrigin() public returns (address){
		return tokenStock.whoIsOrigin();
	}
}

