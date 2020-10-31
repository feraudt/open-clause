pragma solidity ^0.6.0;

import "interfaces/openzeppelin_IERC20.sol";


contract storeServiceAccount {
  
    address creator; // Developper who can receive tokens
	address receiver; //Person who will receive tokens 
	IERC20 tokenContract; // TokenContract managing payement 

	mapping (address => uint256) public dataBase;
	

	/* Constructor */
	constructor (address _tokenContractAddress, address _receiver) public payable {
	    creator = msg.sender;
		receiver = _receiver;
		tokenContract = IERC20(_tokenContractAddress);
	}
	
	/**
	 *  Function 
	 *  Check the caller and obtain the required tokens then store data 
	 */
	function receiveApproval (address _sender, /*uint256 _value ,*/ address _tokenContractAddress, uint256 payload) public {    
	    require(tokenContract == IERC20(_tokenContractAddress));
		/* Obtain the required tokens. if not enough tokens sent then the service will not take place */
		require(tokenContract.transferFrom(_sender, receiver, 1));

		/* Store data in dataBase */
		dataBase[_sender] = payload;
	}


    function tokenFallback(address _sender, uint256 _value, uint256 _payload ) public returns (bool) {
		require(tokenContract == IERC20(msg.sender));
		require(_value == 1);
		dataBase[_sender] = _payload;
		return true;
    }

	/**
	* Store a given data in dataBase at a given adress.
	* Used in ERC20 standard 
	* @param _data to store
	*
	*/
	function storeData( uint256 _data ) public{
		require(tokenContract.transferFrom(msg.sender, receiver, 1));
		dataBase[msg.sender] = _data;
	}
}

