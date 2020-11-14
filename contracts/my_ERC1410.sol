pragma solidity ^0.6.0;

//import "contracts/SecurityTokenStandard_ERC1410Basic.sol";
import "interfaces/openzeppelin_IERC20.sol";

contract ERC1410 {

    address creator; // Developper account
	IERC20 tokenContract; // TokenContract managing payment 

	//Partition[] public partitions;

	enum partitionStates {
		STATUS_FAILED,
		STATUS_ACTIVE, 
		STATUS_SOLD
	}

    // Represents a partially fungible tokens.
    struct Partition {
		address owner;
        uint256 amount;
		uint creation; // date de création
		partitionStates status;
    }

    // Mapping from partition UID
    mapping (uint256 => Partition) public partitions;

    // Mapping from investor to their partitions
    mapping (address => mapping (uint256 => uint256)) public uids;

    // Mapping from investor to the number of partitions they own
    mapping (address => uint256) public nbUid;

	// Mapping from investor to their amount
	//mapping (address => uint256) public balanceOf;

	// Mapping from investor to the amount of one of their partition
	//mapping (address => mapping (uint256 => Partition)) balanceOfByPartition;


    /// @notice Use to get the list of partitions associated with
    /// @param owner : An address corresponds whom partition list is queried
    /// @return List of partitions

	/*** GetStorageAt ***/
    function partitionsOf(address owner) external view returns ( uint256[] memory ) {
		uint256[] memory uidList = new uint256[](nbUid[owner]);
		for(uint i = 0; i < nbUid[owner]; i++) {
			uidList[i] = uids[owner][i+1];
		}

        return uidList;
    }

	function balanceByPartition(uint256 partitionUid) external view returns ( uint256 ){
		return partitions[partitionUid].amount;
	}

	function balanceOf(address owner) external view returns ( uint256 ){
		uint256 total = 0;
		for(uint i = 0; i < nbUid[owner]; i++) {
			total += partitions[uids[owner][i+1]].amount;
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
		nbUid[msg.sender] = 0;
	}

	/**
	* Buy a partition through TokenContract payment.
	* Used in ERC20 standard 
	* @param partitionUid, amount
	*
	*/
	function buyPartition( uint256 partitionUid, uint256 amount ) public{
		require(tokenContract.balanceOf(msg.sender) >= amount);
		require(tokenContract.burnFrom(msg.sender, amount));
		
		partitions[partitionUid].owner = msg.sender;
		partitions[partitionUid].amount = amount;
		partitions[partitionUid].creation = now;
		partitions[partitionUid].status = partitionStates.STATUS_ACTIVE;
		
		//nbUid[msg.sender] = nbUid[msg.sender] +1;
		nbUid[msg.sender]++;
		uids[msg.sender][nbUid[msg.sender]] = partitionUid;
	}

	/**
	* Sell a partition through TokenContract payment.
	* Used in ERC20 standard 
	* @param partitionUid, amount
	*
	*/
	function sellPartition( uint256 partitionUid ) public{
		require(tokenContract.mintFrom(msg.sender, partitions[partitionUid].amount));
		
		partitions[partitionUid].amount = 0;
		partitions[partitionUid].status = partitionStates.STATUS_SOLD;
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
		require(tokenContract.transferFrom(receiver, msg.sender, price));  // price may be partitionIndex[partitionuid].amount
		
		partitions[partitionUid].owner = receiver;
	}

}
