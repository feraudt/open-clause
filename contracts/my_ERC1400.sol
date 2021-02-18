pragma solidity ^0.6.0;

import "interfaces/my_IERC20.sol";

contract ERC1400 {

  address creator; // Developper account
	bool isControl;
	IERC20 tokenContract; // TokenContract managing payment

	enum partitionStates {
		STATUS_ACTIVE,
		STATUS_CONFINED,
		STATUS_SOLD
	}

  // TODO : mettre un statut UNREGISTERED en position 0 car c'est utilisé par défaut
	enum holderStates {
		STATUS_HOLDER,
		STATUS_CONTROLLER,
		STATUS_ESCROW,
    STATUS_UNREGISTERED
	}

  // Represents a partially fungible tokens.
  struct Partition {
		address owner;
    uint256 amount;
		uint256 creation; // date de création
		partitionStates status;
  }

	// Represents a holder of Partition
	struct Holder {
		uint256 nbUid;
		holderStates status;
	}

	// Represents an escrow
	struct ConfinedPartition {
		address escrow;
		uint256 expirationDate;
		uint256 priceExercise;
		address recipient;
	}

  // Mapping from partition UID
  mapping (uint256 => Partition) public partitions;

  // Mapping from investor to their partitions
  mapping (address => mapping (uint256 => uint256)) public uids;

  // Mapping from investor (holder) to the number of partitions they own
  mapping (address => Holder) public holders;

	// Mapping from partition UID to escrow status
	mapping (uint256 => ConfinedPartition) public confined;


	constructor(address _tokenContractAddress, bool _isControl) public {
	  creator = msg.sender;
		isControl = _isControl;
		tokenContract = IERC20(_tokenContractAddress);
	}

	//-------
	// getter
	//-------

  function getPartitionOwner(uint256 partitionUid) public view returns (address) {
      return partitions[partitionUid].owner;
  }

  function getPartitionStatus(uint256 partitionUid) public view returns (uint) {
      return uint(partitions[partitionUid].status);
  }

	function getPartitionAmount(uint256 partitionUid) public view returns (uint256) {
      return uint(partitions[partitionUid].amount);
  }

	function getHolderNbuid(address user) public view returns (uint256) {
      return uint(holders[user].nbUid);
  }

  function getHolderStatus(address user) public view returns (uint) {
      return uint(holders[user].status);
  }

  function getUid(address user, uint index) public view returns (uint256) {
      return uint(uids[user][index]);
  }

	//---------------------------------------------------------
	// specifications ERC1410 - Partially Fungible Token events
	//---------------------------------------------------------

	event TransferByPartition( uint256 partitionUid, address sender, address receiver, uint256 price );

	//------------------------------------------------------------
	// specifications ERC1410 - Partially Fungible Token functions
	//------------------------------------------------------------

  function partitionsOf(address owner) external view returns ( uint256[] memory ) {
		uint256[] memory uidList = new uint256[](holders[owner].nbUid);
		for(uint i = 0; i < holders[owner].nbUid; i++) {
			uidList[i] = uids[owner][i+1];
		}

    return uidList;
  }

	function balanceByPartition(uint256 partitionUid) external view returns ( uint256 ){
		return partitions[partitionUid].amount;
	}

	function balanceOf(address owner) external view returns ( uint256 ){
		uint256 total = 0;
		for(uint i = 0; i < holders[owner].nbUid; i++) {
			if(uids[owner][i+1] != 0) {
				total += partitions[uids[owner][i+1]].amount;
			}
		}

		return total;
	}

	/**
	* Register an account
	**/
	function registerAccount() public{
		require(tokenContract.balanceOf(msg.sender) >= 0);
		holders[msg.sender].nbUid = 0;
		holders[msg.sender].status = holderStates.STATUS_HOLDER;
	}

  function unRegisterAccount(address holder) public{
    require(msg.sender == creator);
    require(this.balanceOf(holder) == 0, "les partitions de holder doivent être soldées");
    holders[holder].status = holderStates.STATUS_UNREGISTERED;
  }

	/**
	* Buy a partition through TokenContract payment.
	* Used in ERC20 standard
	* @param partitionUid, amount
	*
	*/
	function buyPartition( uint256 partitionUid, uint256 amount ) public{
		require(partitionUid != 0);
		require(holders[msg.sender].status == holderStates.STATUS_HOLDER);
		require(tokenContract.balanceOf(msg.sender) >= amount);
		require(tokenContract.burnFrom(msg.sender, amount));

		partitions[partitionUid].owner = msg.sender;
		partitions[partitionUid].amount = amount;
		partitions[partitionUid].creation = now;
		partitions[partitionUid].status = partitionStates.STATUS_ACTIVE;

		holders[msg.sender].nbUid++;
		uids[msg.sender][holders[msg.sender].nbUid] = partitionUid;
	}

	/**
	* Sell a partition through TokenContract payment.
	* Used in ERC20 standard
	* @param partitionUid, amount
	*
	*/
	function sellPartition( uint256 partitionUid ) public{
		require(msg.sender == partitions[partitionUid].owner);
		require(tokenContract.mintFrom(msg.sender, partitions[partitionUid].amount));

		partitions[partitionUid].amount = 0;
		partitions[partitionUid].status = partitionStates.STATUS_SOLD;

		uint j;
		for(uint i = 0; i < holders[msg.sender].nbUid; i++) {
			if(uids[msg.sender][i+1] == partitionUid) {
				j = i;
				i = holders[msg.sender].nbUid;
			}
		}
		uids[msg.sender][j+1] = 0;
	}

	/**
	* Transfer a partition through TokenContract payment.
	* Used in ERC20 standard
	* @param partitionUid, receiver account
	*
	*/
	function transferByPartition(uint256 partitionUid, address receiver, uint256 price) public{
		require(holders[receiver].status == holderStates.STATUS_HOLDER);

		_transfertByPartition(partitionUid, msg.sender, receiver, price);

		//require(tokenContract.balanceOf(receiver) >= price);
		//require(msg.sender == partitions[partitionUid].owner);
		//require(tokenContract.allowance(receiver, address(this)) >= price);
		//require(tokenContract.transferFrom(receiver, msg.sender, price));  // price should be partitionIndex[partitionuid].amount

		//partitions[partitionUid].owner = receiver;
		//holders[receiver].nbUid++;
		//uids[receiver][holders[receiver].nbUid] = partitionUid;

		//uint j;
		//for(uint i = 0; i < holders[msg.sender].nbUid; i++) {
		//	if(uids[msg.sender][i+1] == partitionUid) {
		//		j = i;
		//		i = holders[msg.sender].nbUid;
		//	}
		//}
		//uids[msg.sender][j+1] = 0;

		emit TransferByPartition(partitionUid, msg.sender, receiver, price);
	}


	function _transfertByPartition(uint256 partitionUid, address sender, address receiver, uint256 price) internal virtual {
		require(tokenContract.balanceOf(receiver) >= price);
		require(sender == partitions[partitionUid].owner);
		require(tokenContract.allowance(receiver, address(this)) >= price);
		require(tokenContract.transferFrom(receiver, sender, price));

		partitions[partitionUid].owner = receiver;
		holders[receiver].nbUid++;
		uids[receiver][holders[receiver].nbUid] = partitionUid;

		uint j;
		for(uint i = 0; i < holders[sender].nbUid; i++) {
			if(uids[sender][i+1] == partitionUid) {
				j = i;
				i = holders[sender].nbUid;
			}
		}
		uids[sender][j+1] = 0;

    decreaseAllowanceEscrow(sender, address(this), partitionUid, partitions[partitionUid].amount);
	}


	//-------------------------------------------
	// specifications ERC1644 - Controller Events
	//-------------------------------------------

    event ControllerTransfer(address controller, address indexed seller, address indexed receiver, uint256 price, uint256 partitionUid);

    event ControllerRedemption(address controller, address indexed seller, uint256 price, uint256 partitionUid);


	//----------------------------------------------
	// specifications ERC1644 - Controller functions
	//----------------------------------------------

	/**
	* Register a controller
	**/
	function registerController( address controller) public{
		require(msg.sender == creator);
		require(tokenContract.balanceOf(controller) >= 0);
		require(holders[controller].status == holderStates.STATUS_HOLDER);

		holders[controller].status = holderStates.STATUS_CONTROLLER;
	}

	/**
	* Revoke a controller
	**/
	function unRegisterController( address controller) public{
		require(msg.sender == creator);
		require(holders[controller].status == holderStates.STATUS_CONTROLLER);

		holders[controller].status = holderStates.STATUS_HOLDER;
	}

	function isControllable() external view returns (bool){
		return isControl;
	}


	function controllerTransfer(address seller, address receiver, uint256 partitionUid) public{
		require(holders[tx.origin].status == holderStates.STATUS_CONTROLLER);
		require(holders[seller].status == holderStates.STATUS_HOLDER);
		require(holders[receiver].status == holderStates.STATUS_HOLDER);

		_transfertByPartition(partitionUid, seller, receiver, partitions[partitionUid].amount);
		emit ControllerTransfer(tx.origin, seller, receiver, partitions[partitionUid].amount, partitionUid);
	}

  function controllerRedeem(address seller, uint256 partitionUid) public{
		require(holders[tx.origin].status == holderStates.STATUS_CONTROLLER);
		require(holders[seller].status == holderStates.STATUS_HOLDER);

		_transfertByPartition(partitionUid, seller, tx.origin, partitions[partitionUid].amount);
		emit ControllerRedemption(tx.origin, seller, partitions[partitionUid].amount, partitionUid);
	}

	//------------------------------------
	// addition to ERC1400 - Escrow events
	//------------------------------------

	event ApprovalEscrow(address owner, address escrow, uint256 partitionUid, uint256 price);
	event EscrowTransfer(address escrow, address seller, address receiver, uint256 price, uint256 partitionUid);
	event EscrowExplicitTransfer(address escrow, address seller, address recipient, uint256 price, uint256 partitionUid);

	//---------------------------------------
	// addition to ERC1400 - Escrow functions
	//---------------------------------------

	mapping (address => mapping (address => mapping (uint256 => uint256))) private _allowanceEscrow;

	/**
	* Register an escrow address (this should be the caller smart contract address)
	**/
	function registerEscrow(address escrow) public returns (bool){
		holders[escrow].nbUid = 0;
		holders[escrow].status = holderStates.STATUS_ESCROW;
		return true;
	}

  function unRegisterEscrow(address escrow) public returns (bool){
    require(msg.sender == creator);
    require(holders[escrow].status == holderStates.STATUS_ESCROW);
    holders[escrow].status = holderStates.STATUS_UNREGISTERED;
    return true;
  }

	/**
	* Approve an escrow address for the transfer of a partition
	**/
	function approveEscrow(address escrow, uint256 partitionUid, uint256 price) public returns (bool){
    require(escrow != address(0));
		require(price >= partitions[partitionUid].amount);
		require(msg.sender == partitions[partitionUid].owner);

    _allowanceEscrow[msg.sender][escrow][partitionUid] = price;
    emit ApprovalEscrow(msg.sender, escrow, partitionUid, price);
		return true;
	}

	/**
	* Allowance given to an escrow address on a partition
	**/
	function allowanceEscrow(address owner, address escrow, uint256 partitionUid) public returns (uint256){
		return _allowanceEscrow[owner][escrow][partitionUid];
	}

  function decreaseAllowanceEscrow(address owner, address escrow, uint256 partitionUid, uint256 subAmount) private returns (bool) {
    if( _allowanceEscrow[owner][escrow][partitionUid] >= subAmount ) {
      _allowanceEscrow[owner][escrow][partitionUid] = _allowanceEscrow[owner][escrow][partitionUid] - subAmount;
    }
    else {
      _allowanceEscrow[owner][escrow][partitionUid] = 0;
    }
    return true;
  }

	/**
	* Get the message sender (help to debug)
	**/
	function whoIsOrigin() public returns (address){
		return tx.origin;
	}

	/**
	* Confinement of a Partition for a given duration
	**/

	function confinePartition(address recipient, uint256 partitionUid, uint256 expirationDate, uint256 priceExercise) public returns (bool){
		require(tx.origin == partitions[partitionUid].owner);
		require(holders[msg.sender].status == holderStates.STATUS_ESCROW);
		require(_allowanceEscrow[tx.origin][msg.sender][partitionUid] >= priceExercise, "le contract de séquestre doit être autorisé à modifier le status de la partition");

		partitions[partitionUid].status = partitionStates.STATUS_CONFINED;
		confined[partitionUid].escrow = msg.sender;
		confined[partitionUid].expirationDate = expirationDate;
		confined[partitionUid].priceExercise = priceExercise;
		confined[partitionUid].recipient = recipient;
		return true;
	}

	/**
	* Deconfinement of a Partition
	**/

	function deconfinePartition(address recipient, uint256 partitionUid) public returns (bool){
    // TODO : decomment the requirements
    require(partitions[partitionUid].owner == recipient, "le recipient est le propriétaire de la partition");
		//require(partitions[partitionUid].status == partitionStates.STATUS_CONFINED, "la partition doit être confinée");
		require(holders[msg.sender].status == holderStates.STATUS_ESCROW, "la transaction doit être émise depuis un compte de séquestre");
    //require(_allowanceEscrow[recipient][msg.sender][partitionUid] >= partitions[partitionUid].amount, "le contract Escrow doit être autorisé à modifier le status de la partition");

		partitions[partitionUid].status = partitionStates.STATUS_ACTIVE;
		if(confined[partitionUid].expirationDate > now) {
			confined[partitionUid].expirationDate = now;
		}
		return true;
	}


	/**
	* stop the Option Exercise on a Partition by escrow account or after expiration of the exercise
	**/

	function stopOptionByPromisor(uint256 partitionUid) public returns (bool) {
		require(holders[msg.sender].status == holderStates.STATUS_ESCROW);
		require(holders[tx.origin].status == holderStates.STATUS_HOLDER);
		require(msg.sender == confined[partitionUid].escrow);
		require(tx.origin == partitions[partitionUid].owner);
		require(partitions[partitionUid].status == partitionStates.STATUS_CONFINED);
		_allowanceEscrow[partitions[partitionUid].owner][msg.sender][partitionUid] = 0;

		require(now > confined[partitionUid].expirationDate);
		partitions[partitionUid].status = partitionStates.STATUS_ACTIVE;
		return true;
	}

	function stopOptionByRecipient(uint256 partitionUid) public returns (bool) {
		require(holders[msg.sender].status == holderStates.STATUS_ESCROW);
		require(holders[tx.origin].status == holderStates.STATUS_HOLDER);
		require(msg.sender == confined[partitionUid].escrow);
		require(tx.origin == confined[partitionUid].recipient);
		require(partitions[partitionUid].status == partitionStates.STATUS_CONFINED);
		_allowanceEscrow[partitions[partitionUid].owner][msg.sender][partitionUid] = 0;

		require(now <= confined[partitionUid].expirationDate);
		partitions[partitionUid].status = partitionStates.STATUS_ACTIVE;
		confined[partitionUid].expirationDate = now;
		return true;
	}

	/**
	* transfer partition from escrow
	**/

	function escrowTransfer(address seller, uint256 price, uint256 partitionUid) public{
		require(tx.origin == confined[partitionUid].recipient);

		require(holders[msg.sender].status == holderStates.STATUS_ESCROW);
		require(holders[seller].status == holderStates.STATUS_HOLDER);
		require(holders[tx.origin].status == holderStates.STATUS_HOLDER);
		require(msg.sender == confined[partitionUid].escrow);
		require(seller == partitions[partitionUid].owner);
		require(now <= confined[partitionUid].expirationDate);

		_transfertByPartition(partitionUid, seller, tx.origin, price);

		emit EscrowTransfer(msg.sender, seller, tx.origin, price, partitionUid);
	}

	function escrowExplicitTransfer(address seller, address recipient, uint256 price, uint256 partitionUid) public{
		require(holders[msg.sender].status == holderStates.STATUS_ESCROW);
		require(holders[seller].status == holderStates.STATUS_HOLDER);
		require(holders[recipient].status == holderStates.STATUS_HOLDER);
		require(seller == partitions[partitionUid].owner);

		_transfertByPartition(partitionUid, seller, recipient, price);

		emit EscrowExplicitTransfer(msg.sender, seller, recipient, price, partitionUid);
	}

  function escrowFreeTransfer(address recipient, uint256 price, uint256 partitionUid) public{
    require(tx.origin == partitions[partitionUid].owner);
    require(holders[msg.sender].status == holderStates.STATUS_ESCROW);
    require(holders[tx.origin].status == holderStates.STATUS_HOLDER);
    require(holders[recipient].status == holderStates.STATUS_HOLDER);

    _transfertByPartition(partitionUid, tx.origin, recipient, price);

    emit EscrowTransfer(msg.sender, tx.origin, recipient, price, partitionUid);
  }
}
