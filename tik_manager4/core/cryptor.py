import uuid
import base64


class Cryptor:
    def __init__(self):
        # Retrieve the MAC address as the machine identifier
        self.key = self._get_mac_address_key()
        self.machine_id = uuid.getnode()  # Store the full MAC address for validation

    @staticmethod
    def _get_mac_address_key():
        """Retrieve a single-byte key derived from the MAC address."""
        mac_address = uuid.getnode()
        return mac_address & 0xFF  # Use the last byte of the MAC address

    def _xor_with_key(self, data):
        """Apply XOR operation with the MAC address key."""
        return "".join(chr(ord(char) ^ self.key) for char in data)

    def encrypt(self, plain_text):
        """
        Encrypt the given plain text.
        - Appends the machine identifier to the plain text.
        - XOR obfuscates the text with the MAC-derived key.
        - Encodes the result in Base64.
        """
        text_with_machine_id = f"{plain_text}:{self.machine_id}"
        xor_obfuscated = self._xor_with_key(text_with_machine_id)
        return base64.b64encode(xor_obfuscated.encode()).decode()

    def decrypt(self, encrypted_text):
        """
        Decrypt the given encrypted text.
        - Decodes the Base64-encoded string.
        - Applies XOR de-obfuscation with the MAC-derived key.
        - Validates the machine identifier.
        """
        decoded_data = base64.b64decode(encrypted_text).decode()
        decrypted = self._xor_with_key(decoded_data)
        try:
            plain_text, machine_id = decrypted.rsplit(":", 1)
        except ValueError:
            raise ValueError(
                "Decryption failed: invalid format or missing machine identifier."
            )

        # Verify the machine identifier
        if int(machine_id) != self.machine_id:
            raise ValueError("Decryption failed: machine identifier mismatch.")

        return plain_text


# Example usage
if __name__ == "__main__":
    encryptor = Cryptor()
    secret = "user_password"

    # Encrypt the string
    encrypted = encryptor.encrypt(secret)
    print(f"Encrypted: {encrypted}")

    # Decrypt the string
    try:
        decrypted = encryptor.decrypt(encrypted)
        print(f"Decrypted: {decrypted}")
    except ValueError as e:
        print(f"Error: {e}")
