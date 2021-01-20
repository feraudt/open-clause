pragma solidity ^0.6.0;

interface IERC1400 {

	function getPartitionOwner(uint256 partitionUid) external view returns (address);

	function getPartitionStatus(uint256 partitionUid) external view returns (uint);

	function getPartitionAmount(uint256 partitionUid) external view returns (uint);

	function getHolderNbuid(address user) external view returns (uint);

	function getUid(address user, uint index) external view returns (uint256);

	//------------------------------------------------------------
	// specifications ERC1410 - Partially Fungible Token functions
	//------------------------------------------------------------

	function registerAccount() external view;

	function partitionsOf(address owner) external view returns ( uint256[] memory );

	function balanceByPartition(uint256 partitionUid) external view returns ( uint256 );

	function balanceOf(address owner) external view returns ( uint256 );

	function buyPartition( uint256 partitionUid, uint256 amount ) external view;

	function sellPartition( uint256 partitionUid ) external view;

	function transferByPartition( uint256 partitionUid, address receiver, uint256 price ) external view;


	//----------------------------------------------
	// specifications ERC1644 - Controller functions
	//----------------------------------------------

	function registerController(address controller) external view;

	function revokeController( address controller) external view;

	function isControllable() external view returns (bool);

	function controllerTransfer(address sender, address receiver, uint256 price, uint256 partitionUid) external view;

    function controllerRedeem(address sender, uint256 price, uint256 partitionUid) external view;

	//---------------------------------------
	// addition to ERC1400 - Escrow functions
	//---------------------------------------

	function registerEscrow(address escrow) external view returns (bool);

	function approveEscrow(address escrow, uint256 partitionUid, uint256 price) external view returns (bool);

	function allowanceEscrow(address owner, address escrow, uint256 partitionUid) external view returns (uint256);

	function whoissender() external returns (address);

	function confinePartition(address recipient, uint256 partitionUid, uint256 expirationDate, uint256 priceExercise) external returns (bool);
	function deconfinePartition(address recipient, uint256 partitionUid) external returns (bool);

	function stopOptionByPromisor(uint256 partitionUid) external returns (bool);
	function stopOptionByRecipient(uint256 partitionUid) external returns (bool);

	function escrowTransfer(address seller, uint256 price, uint256 partitionUid) external;
	function escrowExplicitTransfer(address seller, address recipient, uint256 price, uint256 partitionUid) external;

	function whoIsOrigin() external returns (address);

}
