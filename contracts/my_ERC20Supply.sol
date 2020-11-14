pragma solidity ^0.6.0;

import "contracts/openzeppelin_ERC20.sol";

contract ERC20FixedSupply is ERC20('LETI','LTC') {
    constructor() public {
        _mint(msg.sender, 1000);
    }
}
