pragma solidity ^0.6.0;

import "contracts/my_ERC20.sol";

contract ERC20FixedSupply is ERC20('LETI','LTC') {
    constructor() public {
        _mint(msg.sender, 1000);
    }
}
