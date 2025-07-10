# pragma version 0.4.3

import state
initializes: state

@deploy
def __init__():
    state.a = 1
    state.b = empty(address)