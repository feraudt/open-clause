pragma solidity ^0.6.0;

interface IERC1410 {

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


	//-------------------------------------------
	// specifications ERC1644 - Controller Events
	//-------------------------------------------
    event ControllerTransfer(
        address _controller,
        address indexed _from,
        address indexed _to,
        uint256 _value,
        uint256 _data
    );

    event ControllerRedemption(
        address _controller,
        address indexed _tokenHolder,
        uint256 _value,
        uint256 _data
    );
}
