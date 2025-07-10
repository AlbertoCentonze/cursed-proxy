import boa
from eth_utils import function_signature_to_4byte_selector
from typing import List, Dict, Any

BASE_PATH = "contracts/router-proxy/"

def extract_function_signatures(contract):
    """Extract function signatures from a contract's ABI."""
    abi = contract.abi
    signatures = []
    
    for item in abi:
        if item['type'] == 'function' and item['name'] != '__init__':
            # Build the function signature
            name = item['name']
            inputs = ','.join([inp['type'] for inp in item.get('inputs', [])])
            signature = f"{name}({inputs})"
            
            # Calculate the 4-byte selector
            selector = function_signature_to_4byte_selector(signature)
            signatures.append(selector)
    
    return signatures

def deploy_router_proxy(
    proxy_path: str,
    logic_contract_paths: List[str],
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Deploy a router proxy that forwards calls to multiple logic contracts.
    
    Note: Logic contracts must not have constructor arguments as they are 
    meant to be stateless implementations for delegatecall.
    
    Args:
        proxy_path: Path to the proxy contract vyper file
        logic_contract_paths: List of paths to logic contract vyper files
        verbose: Whether to print deployment information
    
    Returns:
        Dictionary containing:
            - proxy: The deployed proxy contract
            - logic_contracts: Dict mapping contract names to deployed contracts
            - function_mappings: List of (selector, target_address) tuples
    """
    deployed_logic = {}
    logic_addresses = []
    all_mappings = []
    
    # Deploy each logic contract and extract its function signatures
    for contract_path in logic_contract_paths:
        # Extract contract name from path
        contract_name = contract_path.split('/')[-1].replace('.vy', '')
        
        # Load and deploy the contract (no constructor args)
        deployer = boa.load_partial(contract_path)
        contract = deployer.deploy()
        
        deployed_logic[contract_name] = contract
        
        # Extract function signatures
        signatures = extract_function_signatures(contract)
        
        if signatures:
            logic_addresses.append((
                contract.address,
                signatures
            ))
            
            # Store mappings for return value
            for sig in signatures:
                all_mappings.append((sig, contract.address))
        
        if verbose:
            print(f"{contract_name.capitalize()} deployed at: {contract.address}")
    
    # Deploy the proxy with the logic addresses
    proxy_deployer = boa.load_partial(proxy_path)
    proxy = proxy_deployer.deploy(logic_addresses)
    
    if verbose:
        print(f"\nProxy deployed at: {proxy.address}")
        print("\nFunction mappings:")
        for contract_name, contract in deployed_logic.items():
            sigs = extract_function_signatures(contract)
            if sigs:
                print(f"\n{contract_name.capitalize()}:")
                for sig in sigs:
                    print(f"  - {sig.hex()} -> {contract.address}")
    
    return {
        "proxy": proxy,
        "logic_contracts": deployed_logic,
        "function_mappings": all_mappings
    }

def test_deploy():
    """Test the generic proxy deployment function."""
    # Define the logic contracts to deploy
    logic_contract_paths = [
        BASE_PATH + "controller.vy",
        BASE_PATH + "view.vy",
    ]
    
    # Deploy using the generic function
    result = deploy_router_proxy(
        proxy_path=BASE_PATH + "proxy.vy",
        logic_contract_paths=logic_contract_paths,
        verbose=True
    )

    source = """
    interface View:
        def get_a() -> uint256: view
        
    """

    VIEW = result["logic_contracts"]["view"]
    proxy_as_view = VIEW.at(result["proxy"].address)
    CONTROLLER = result["logic_contracts"]["controller"]
    proxy_as_controller = CONTROLLER.at(result["proxy"].address)

    print(proxy_as_view.get_a())
    proxy_as_controller.create_loan()
    print(proxy_as_view.get_a())
    


