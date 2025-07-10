# pragma version 0.4.3
import state 
initializes: state

@external
@payable
def get_a() -> uint256:
    a: uint256 = state.a
    return a