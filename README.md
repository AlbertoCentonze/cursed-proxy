# Cursed POC
The idea is that we can use delegate calls to keep the storage in the same contract (`proxy.vy`) and dispatch calls to multiple contracts (`view.vy` and `controller.vy`).

To access storage variables we use state.vy (it basically gives a common reference of where the storage slots are to all contracts) and we can write the constructor in `state_init.vy` (this one was just to have the compiler not enforce the constructor to be called in every implementation).

Infinite contract storage.