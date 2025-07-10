# pragma version 0.4.3

MAX_OUTSIZE: constant(uint256) = 10000
MAX_SIGS: constant(uint256) = 100

import state_init
initializes: state_init
logic: HashMap[bytes4, address]

struct LogicAddress:
    target: address
    sigs: DynArray[bytes4, MAX_SIGS]

@deploy
def __init__(logic_addresses: DynArray[LogicAddress, 10]):
    state_init.__init__()
    
    for logic_addr: LogicAddress in logic_addresses:
        for sig: bytes4 in logic_addr.sigs:
            self.logic[sig] = logic_addr.target


@external
@raw_return
def __default__() -> Bytes[MAX_OUTSIZE]:
    func_sig: bytes4 = convert(slice(msg.data, 0, 4), bytes4)
    target: address = self.logic[func_sig]

    result: Bytes[MAX_OUTSIZE] = b""
    result = raw_call(
        target,
        msg.data,
        is_delegate_call=True,
        max_outsize=MAX_OUTSIZE
    )
    return result