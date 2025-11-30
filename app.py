import streamlit as st
from web3 import Web3
from streamlit_metamask import login_with_metamask

# 1. Configuración de la página
st.set_page_config(page_title="Validador de NFT", page_icon="🛡️")

st.title("🛡️ Acceso Exclusivo para Holders")
st.markdown("Conecta tu wallet y firma el mensaje para verificar que posees el NFT requerido.")

# 2. Configuración de la Red Arbitrum y el NFT
# Usamos un RPC público de Arbitrum
ARBITRUM_RPC = "https://arb1.arbitrum.io/rpc"
NFT_ADDRESS = "0xF4820467171695F4d2760614C77503147A9CB1E8"

# ABI Mínimo: Solo necesitamos la función 'balanceOf' para saber si tienes el NFT
ERC721_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    }
]

# 3. Función para verificar el NFT en la Blockchain
def check_nft_ownership(user_address):
    try:
        # Conexión a Arbitrum
        w3 = Web3(Web3.HTTPProvider(ARBITRUM_RPC))
        
        if not w3.is_connected():
            st.error("Error conectando a la red Arbitrum.")
            return False

        # Asegurarse de que la dirección tiene el formato correcto (Checksum)
        checksum_address = w3.to_checksum_address(user_address)
        checksum_nft = w3.to_checksum_address(NFT_ADDRESS)

        # Instanciar el contrato
        contract = w3.eth.contract(address=checksum_nft, abi=ERC721_ABI)

        # Consultar balance
        balance = contract.functions.balanceOf(checksum_address).call()
        
        return balance > 0
    except Exception as e:
        st.error(f"Error al verificar la blockchain: {e}")
        return False

# 4. Interfaz de Usuario y Lógica de Login
# El componente login_with_metamask maneja la conexión y firma offchain
event = login_with_metamask(
    event="Login",
    message="Bienvenido. Firma este mensaje para validar que eres dueño del NFT.",
    key="login_button"
)

st.divider()

# 5. Lógica de Validación
if event and "account" in event:
    user_wallet = event["account"]
    st.info(f"Wallet conectada: `{user_wallet}`")
    
    with st.spinner("Verificando posesión del NFT en Arbitrum..."):
        has_nft = check_nft_ownership(user_wallet)

    if has_nft:
        st.success("✅ ¡Validación Exitosa! Tienes el NFT.")
        st.balloons()
        
        # --- AQUÍ VA EL CONTENIDO EXCLUSIVO ---
        st.header("🔓 Contenido Secreto")
        st.write("Bienvenido al área exclusiva. Aquí tienes tu contenido desbloqueado.")
        st.image("https://placekitten.com/800/400", caption="Contenido solo para holders")
        # ---------------------------------------
        
    else:
        st.error("⛔ Acceso Denegado")
        st.warning("No se ha detectado el NFT requerido en tu billetera en la red Arbitrum.")
        st.markdown(f"**NFT Requerido:** [`{NFT_ADDRESS}`](https://arbiscan.io/address/{NFT_ADDRESS})")

elif event is None:
    st.info("👋 Por favor, pulsa el botón naranja para conectar tu MetaMask.")
