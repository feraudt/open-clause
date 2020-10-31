pragma solidity ^0.6.0;

import "interfaces/openzeppelin_IERC20.sol";


contract storeServiceContract {
  
    address creator; // Developper who can receive tokens
	IERC20 tokenContract; // TokenContract managing payement 

	mapping (address => uint256) public dataBase;
	

	/* Constructor */
	constructor (address _tokenContractAddress) public payable {
	    creator = msg.sender;
		tokenContract = IERC20(_tokenContractAddress);
	}
	
	/**
	 *  Function 
	 *  Check the caller and obtain the required tokens then store data 
	 */
	function receiveApproval (address _sender, /*uint256 _value ,*/ address _tokenContractAddress, uint256 payload) public {    
	    require(tokenContract == IERC20(_tokenContractAddress));
		/* Obtain the required tokens. if not enough tokens sent then the service will not take place */
		require(tokenContract.transferFrom(_sender, address(this), 1));

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
		require(tokenContract.transferFrom(msg.sender,address(this),1));
		dataBase[msg.sender] = _data;
	}
}

