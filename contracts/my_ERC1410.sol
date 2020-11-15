pragma solidity ^0.6.0;

//import "contracts/my_ERC1410.sol";
import "interfaces/my_IERC20.sol";

contract ERC1410 {

    address creator; // Developper account
	IERC20 tokenContract; // TokenContract managing payment 

	enum partitionStates {
		STATUS_FAILED,
		STATUS_ACTIVE, 
		STATUS_SOLD
	}

	enum holderStates {
		STATUS_REGISTERED
	}

    // Represents a partially fungible tokens.
    struct Partition {
		address owner;
        uint256 amount;
		uint creation; // date de création
		partitionStates status;
    }

	// Represents a holder of Partition
	struct Holder {
		uint256 nbUid;
		holderStates status;
	}

    // Mapping from partition UID
    mapping (uint256 => Partition) public partitions;

    // Mapping from investor to their partitions
    mapping (address => mapping (uint256 => uint256)) public uids;

    // Mapping from investor to the number of partitions they own
    //mapping (address => uint256) public nbUid;

    // Mapping from investor (holder) to the number of partitions they own
    mapping (address => Holder) public holders;


    /// @notice Use to get the list of partitions associated with
    /// @param owner : An address corresponds whom partition list is queried
    /// @return List of partitions

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

	constructor(address _tokenContractAddress) public {
	    creator = msg.sender;
		tokenContract = IERC20(_tokenContractAddress);
	}

	/**
	* Register an account
	**/
	function registerAccount() public{	
		require(tokenContract.balanceOf(msg.sender) >= 0);
		holders[msg.sender].nbUid = 0;
		holders[msg.sender].status = holderStates.STATUS_REGISTERED;
	}

	/**
	* Buy a partition through TokenContract payment.
	* Used in ERC20 standard 
	* @param partitionUid, amount
	*
	*/
	function buyPartition( uint256 partitionUid, uint256 amount ) public{
		require(partitionUid != 0);
		require(holders[msg.sender].status == holderStates.STATUS_REGISTERED);
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
		uids[msg.sender][j] = 0;
	}

	/**
	* Transfer a partition through TokenContract payment.
	* Used in ERC20 standard 
	* @param partitionUid, receiver account
	*
	*/
	function transferByPartition( uint256 partitionUid, address receiver, uint256 price ) public{
		require(tokenContract.balanceOf(receiver) >= price);
		require(msg.sender == partitions[partitionUid].owner);
		require(holders[receiver].status == holderStates.STATUS_REGISTERED);
		require(tokenContract.transferFrom(receiver, msg.sender, price));  // price should be partitionIndex[partitionuid].amount
		
		partitions[partitionUid].owner = receiver;
		holders[receiver].nbUid++;
		uids[receiver][holders[receiver].nbUid] = partitionUid;

		uint j;
		for(uint i = 0; i < holders[msg.sender].nbUid; i++) {
			if(uids[msg.sender][i+1] == partitionUid) {
				j = i;
				i = holders[msg.sender].nbUid;
			}
		}
		uids[msg.sender][j+1] = 0;
	}

}
