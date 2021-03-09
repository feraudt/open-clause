pragma solidity ^0.6.0;

import "interfaces/my_IERC20.sol";
import "interfaces/my_IERC1400.sol";

contract clausePreemption {

	// Represents a preemption parameters
  struct PreemptionRight {
		address promisor;
		address recipient;
		uint256 expirationDate;
  }

	struct PreemptionResponse {
		address promisor;
		address recipient;
		uint256 partitionUid;
		uint256 pricePreemption;
		uint256 expirationNotice;
		uint256 expirationDate;
		uint256 decisionDate;
		bool decision;
	}

  // Mapping from partition UID to Option
  mapping ( address => mapping (uint256 => PreemptionRight)) public preemptions;

	mapping (address => uint256) public nbRecipient;
	mapping (address => mapping (uint256 => PreemptionResponse)) public responses;

	IERC1400 public tokenStock;   // token qui représente la partition (ERC1410)
	IERC20 public tokenPayment;   // token qui représente le coin (ERC20)

	//address public recipient;     // le bénéficiaire de la preemption
	//address public promisor;  // le promettant
	//uint256 public expirationDate; // la date de fin du droit de premption


	constructor(address _tokenStockAddress, address _tokenPaymentAddress) public {
	  require(_tokenStockAddress != address(0));
		require(_tokenPaymentAddress != address(0));

		tokenStock = IERC1400(_tokenStockAddress);
		tokenPayment = IERC20(_tokenPaymentAddress);
	}


	//------------------------------------------------------------
	// Preemption right events
	//------------------------------------------------------------

	event StartPreemption(address indexed _promisor, address indexed _recipient, address escrow, uint256 _expirationDate);

	//------------------------------------------------------------
	// Preemption right functions
	//------------------------------------------------------------

	// The promisor initiate the Preemption for a given recipient

	function startPreemption(address recipient, uint256 duration) public returns (bool){
		require(tokenStock.getHolderStatus(msg.sender) == 0 , "Le émetteur (promisor) doit être un détenteur de titres");
		require(tokenStock.getHolderStatus(recipient) == 0, "Le bénéficiaire (recipient) doit être un détenteur de titres");
		require(duration > 0, "la durée d'une premption est exprimée en minutes");

		uint256 index;
		if( preemptions[msg.sender][0].promisor == address(0) ) {
			nbRecipient[msg.sender] = 0;
		}

		preemptions[msg.sender][index].promisor = msg.sender;
		preemptions[msg.sender][index].recipient = recipient;
		uint256 endDate;
		endDate = preemptions[msg.sender][index].expirationDate = now + duration * 1 minutes;

		index = index + 1;
		nbRecipient[msg.sender] = index;
		emit StartPreemption(msg.sender, recipient, address(this), endDate);
		return true;
	}


	function launchNotice(address recipient, uint256 partitionUid, uint256 pricePreemption, uint256 duration) public returns (bool){
		require(tokenStock.getHolderStatus(msg.sender) == 0 , "Le émetteur (promisor) doit être un détenteur de titres");
		require(tokenStock.getHolderStatus(recipient) == 0, "Le bénéficiaire (recipient) doit être un détenteur de titres");
		require(tokenStock.getPartitionOwner(partitionUid) == msg.sender, "Le émetteur doit être le propriétaire de la partition");

		uint256 index = nbRecipient[msg.sender];
		uint j;
		for ( uint i=0; i< index; i++) {
			if ( preemptions[msg.sender][i].recipient == recipient ) {
				j = i;
				i = index;
			}
		}
		require(preemptions[msg.sender][j].expirationDate > now);
		require(tokenStock.allowanceEscrow(msg.sender, address(this), partitionUid) == true);

		responses[recipient][partitionUid].promisor = msg.sender;
		responses[recipient][partitionUid].recipient = recipient;
		responses[recipient][partitionUid].partitionUid = partitionUid;
		responses[recipient][partitionUid].pricePreemption = pricePreemption;
		responses[recipient][partitionUid].expirationNotice = now + duration * 1 minutes;
		responses[recipient][partitionUid].expirationDate = preemptions[msg.sender][j].expirationDate;
		responses[recipient][partitionUid].decisionDate = 0;
		responses[recipient][partitionUid].decision = false;
	}


	// The recipient notifies his decision

	function recipientDecision(uint256 partitionUid, bool decision) public returns (bool){
		require(msg.sender == responses[msg.sender][partitionUid].recipient);
		require(responses[msg.sender][partitionUid].expirationNotice >= now);
		require(responses[msg.sender][partitionUid].expirationDate >= now);

		responses[msg.sender][partitionUid].decisionDate = now;
		responses[msg.sender][partitionUid].decision = decision;
		return true;
	}

	function launchTransfer(address recipient, uint256 partitionUid) public returns (bool){
		require(now >= responses[recipient][partitionUid].decisionDate, "now est postérieur à responses.decisionDate");
		require(tokenStock.getPartitionOwner(partitionUid) == msg.sender, "msg.sender doit être le owner de la partition");
		require(responses[recipient][partitionUid].decision == true, "le recipient doit être bénéficiaire et avoir notifié une décision positive");
		require(tokenStock.allowanceEscrow(msg.sender, address(this), partitionUid) == true, "msg.sender a positionné une allowance à this sur la partition");
		require(tokenPayment.allowance(recipient, address(this)) >= responses[recipient][partitionUid].pricePreemption, "le recipient a positionné une allowance à this pour le coût de la préemption");
		//require("le recipient a positionné une allowance à ERC1400 pour le coût de la partition");

		// paiment du coût de la préemption
		tokenPayment.transferFrom(recipient, msg.sender, responses[recipient][partitionUid].pricePreemption);
		// transfert of the partition from promisor (msg.sender) to recipient
		tokenStock.escrowFreeTransfer(recipient, tokenStock.getPartitionAmount(partitionUid), partitionUid);
	}

}
