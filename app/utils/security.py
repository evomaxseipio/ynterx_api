"""Security utilities for password hashing and verification."""
import bcrypt


def get_password_hash(password: str) -> tuple[str, str]:
    """
    Hash a password using bcrypt.

    Args:
        password: The plain text password to hash.

    Returns:
        A tuple containing (password_hash, password_salt).
        The password_hash is the complete bcrypt hash including the salt.
        The password_salt is stored separately for verification purposes.
    """
    # Generate a random salt
    salt = bcrypt.gensalt()
    # Convert the password to bytes
    password_bytes = password.encode('utf-8')
    # Hash the password with the salt
    password_hash = bcrypt.hashpw(password_bytes, salt)
    # Convert salt and hash to hex strings for storage
    salt_hex = salt.hex()
    hash_hex = password_hash.hex()

    return hash_hex, salt_hex


def verify_password(plain_password: str, hashed_password: str, password_salt: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: The password to verify.
        hashed_password: The stored password hash in hex format.
        password_salt: The stored salt in hex format.

    Returns:
        True if the password matches, False otherwise.
    """
    try:
        # Convert hex strings back to bytes
        salt_bytes = bytes.fromhex(password_salt)
        hash_bytes = bytes.fromhex(hashed_password)
        # Convert password to bytes
        password_bytes = plain_password.encode('utf-8')
        # Hash the input password with the stored salt
        calculated_hash = bcrypt.hashpw(password_bytes, salt_bytes)
        # Compare the calculated hash with the stored hash
        return calculated_hash == hash_bytes
    except Exception:
        return False
