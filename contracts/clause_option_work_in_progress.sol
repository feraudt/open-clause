pragma solidity ^0.6.0;

import "interfaces/my_IERC20.sol";
import "interfaces/my_IERC1400.sol";

contract Option {

//on instancie les différents états du contrat

	enum ContractStates {
		STATUS_NONE,
		STATUS_INITIALIZED, 
		STATUS_OPENED, 
		STATUS_CLOSED 
	}

    ContractStates public currentState;

	// Evenements qui se déclenchent aux différentes étapes du contrat
	event Initialized (address indexed _seller, uint256 _amountStock);
	event Opened(address indexed _buyer, uint256 _priceOption);
	event Closed(address indexed _seller, uint256 _amountPayment);

	address public buyer;
	address public seller;

	IERC20 public tokenStock;   // token qui représente l'action
	IERC20 public tokenPayment; // token qui représente le stablecoin (ERC20)

	uint256 public nbStock;     // nombre d'actions 
	uint256 public priceStock;  // prix d'une action
	uint256 public priceOption; // prix à payer par l'acheteur pour le droit d'option
	uint256 public dateExpiration; // date de l'OS linux après laquelle l'acheteur ne peut plus exercer son droit d'option
	uint256 public priceExercise;  // prix fixé pour l'exercice 

	/**
	 * Le vendeur initie le contrat en paramètrant toutes les variables.
	 * The Seller should also have already "allowed" the ERC20 to be transferred in by the contract
	 * in the amount specified by premiumAmount.  This will be held in escrow.
	 */
	 
	constructor(
		IERC20 _tokenStock,
		uint256 _nbStock,
		IERC20 _tokenPayment,
		uint256 _priceExercise,
		uint256 _priceOption,
		uint _dateExpiration
	) public {
	    
		require(address(_tokenStock) != address(0));
		require(_nbStock > 0);
		require(address(_tokenPayment) != address(0));
		require(_priceExercise > 0);
		require(_priceOption > 0);
		require(_dateExpiration > now);

		// Save off the inputs
		seller = msg.sender;
		tokenStock = _tokenStock;
		nbStock = _nbStock;
		tokenPayment = _tokenPayment;
		priceExercise = _priceExercise;
		priceOption = _priceOption;
		dateExpiration = _dateExpiration;

		// l'etat du contrat est sur none
		currentState = ContractStates.STATUS_NONE;
	}

	function initialize() public {
		require(currentState == ContractStates.STATUS_NONE);

		require(msg.sender == seller, "Seul le vendeur peut initialiser le contrat");

		// Les actions sont envoyées en séquestre
		require(tokenStock.transferFrom(seller, address(this), nbStock), "Doit envoyer les actions en séquestre");

		// met à jour l'etat du contrat
		currentState = ContractStates.STATUS_INITIALIZED;

		// Emet l'evenement
		emit Initialized(seller, nbStock);
	}

	/**
	 * Une fois le contrat ouvert par le vendeur, l'acheteur peut.....
	 */
	 
	function open() public {
		// Validate contract state
		require(now < dateExpiration);
		
		require(currentState == ContractStates.STATUS_INITIALIZED);

		// Save off the buyer
		buyer = msg.sender;

		// Transfer the tokens over to the seller
		require(tokenPayment.transferFrom(buyer, seller, priceOption));

		// Set the status to open
		currentState = ContractStates.STATUS_OPENED;

		// Emit the event
		emit Opened(buyer, priceOption);
	}

	/**
	 * If the contract was never opened by a buyer or the contract was never redeemed and it expired,
	 * the seller can close it out and get back the initial underlying asset token.
	 */

	/**
	 * After a buyer has opened the contract they can redeem their right to the underlying asset.
	 * They can only do this if the contract is in the open state and it has not expired.
	 * They must pay the purchase price times the asset amount and they will get the underlying asset in return.
	 * The buyer must have already "allowed" the contract to transfer the payment amount of purchasingTokens
	 */
	 
	function redeem() public {
		// Validate contract state
		require(currentState == ContractStates.STATUS_OPENED && now < dateExpiration);
		require(msg.sender == buyer);

		// Calculate the amount of tokens that should be paid
		uint256 amountPayment = nbStock * priceExercise;

		// Move the payment from the buyer to the seller
		require(tokenPayment.transferFrom(buyer, seller, amountPayment));

		// Pay out the buyer from escrow
		tokenStock.transfer(buyer, nbStock);

		// Set the status to closed
		currentState = ContractStates.STATUS_CLOSED;

		// Emit the event
		emit Closed(buyer, amountPayment);
	}

}

