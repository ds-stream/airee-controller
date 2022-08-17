"""
Module to generate public and private key pair using different algorithms.
https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/?highlight=rsa#key-serialization
https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ec/#cryptography.hazmat.primitives.asymmetric.ec.generate_private_key
"""
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ec
from cryptography.hazmat.primitives import serialization
import config
import logging

logger = logging.getLogger(__name__)
logger.setLevel(config.log_lvl)
logger.addHandler(config.ch)
logger.propagate = False

class PairKey:
    """Class to generate key pair object
    
    There are three algorithms available:
    - RSA
    - ED25519
    - EDCSA (working with pygit2 and accepted by github)
    """
    def __init__(self):
        """"""
        pass
    
    def generate_pair_rsa(public_exponent=65537, key_size=2048):
        """Method to generate RSA key pair.
        
        Args:
            public_exponent: int 3 (for legacy compatibility) or 65537. For more info check cryptography framework.
            key_size: int key size in bits. Must be > 512.
        Returns:
            pem_priv - private key
            pem_pub - public key
            """
        private_key = rsa.generate_private_key(public_exponent,key_size)

        pem_priv = private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption())
        
        public_key = private_key.public_key()
        
        pem_pub = public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.OpenSSH)
        logger.debug("created RSA keypair")
        return pem_priv, pem_pub

    def generate_pair_ed25519():
        """Method to generate ED25519 key pair.
        
        Returns:
            private_bytes - private key
            public_bytes - public key"""
        private_key = ed25519.Ed25519PrivateKey.generate()
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.OpenSSH,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        )
        logger.debug("created ed25519 keypair")
        return private_bytes, public_bytes

    # working with pygit2 :)
    def generate_pair_ecdsa():
        """Method to generate ED25519 key pair.
        
        Returns:
            ed_priv - private key
            ed_pub - public key"""
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()
        # serializing into PEM

        ed_priv = private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.OpenSSH,
            serialization.NoEncryption()
        )

        ed_pub = public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH)
        logger.debug("created ecdsa keypair")
        return ed_priv, ed_pub
        
    
    def save_keys(priv_b, pub_b, priv_name, pub_name, path):
        """Method to write given key pair into files.
        
        Args:
            priv_b: private key in bytes
            pub_b: public key in bytes
            priv_name: string name of file with private key
            pub_name: string name of file with public key
            path: string path where file will be saved
        """
        with open(f'{path}/{priv_name}', 'wb') as f:
            f.write(priv_b)
            logger.debug(f"Priv key saved on {path}/{priv_name}")
        with open(f'{path}/{pub_name}', 'wb') as f:
            f.write(pub_b)
            logger.debug(f"Priv key saved on {path}/{pub_name}")
        return 0