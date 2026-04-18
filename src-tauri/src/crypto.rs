use aes_gcm::{
    aead::{Aead, KeyInit, OsRng},
    Aes256Gcm, Nonce,
};
use argon2::{Argon2, PasswordHash, PasswordHasher, PasswordVerifier};
use argon2::password_hash::{rand_core::RngCore, SaltString};
use base64::{engine::general_purpose::STANDARD as BASE64, Engine};

pub struct CryptoManager {
    cipher: Aes256Gcm,
}

impl CryptoManager {
    /// Derive an encryption key from the master password using Argon2id
    pub fn derive_key(master_password: &str, salt: &[u8]) -> Result<[u8; 32], String> {
        let argon2 = Argon2::default();
        let mut key = [0u8; 32];
        argon2
            .hash_password_into(master_password.as_bytes(), salt, &mut key)
            .map_err(|e| format!("Key derivation failed: {}", e))?;
        Ok(key)
    }

    /// Hash the master password for verification storage
    pub fn hash_master_password(password: &str) -> Result<String, String> {
        let salt = SaltString::generate(&mut OsRng);
        let argon2 = Argon2::default();
        let hash = argon2
            .hash_password(password.as_bytes(), &salt)
            .map_err(|e| format!("Password hashing failed: {}", e))?;
        Ok(hash.to_string())
    }

    /// Verify master password against stored hash
    pub fn verify_master_password(password: &str, hash: &str) -> Result<bool, String> {
        let parsed_hash =
            PasswordHash::new(hash).map_err(|e| format!("Invalid hash format: {}", e))?;
        let argon2 = Argon2::default();
        Ok(argon2
            .verify_password(password.as_bytes(), &parsed_hash)
            .is_ok())
    }

    /// Create a new CryptoManager from a derived key
    pub fn new(key: &[u8; 32]) -> Self {
        let cipher = Aes256Gcm::new_from_slice(key).expect("Invalid key length");
        Self { cipher }
    }

    /// Encrypt plaintext, returns base64(nonce + ciphertext)
    pub fn encrypt(&self, plaintext: &str) -> Result<String, String> {
        let mut nonce_bytes = [0u8; 12];
        OsRng.fill_bytes(&mut nonce_bytes);
        let nonce = Nonce::from_slice(&nonce_bytes);

        let ciphertext = self
            .cipher
            .encrypt(nonce, plaintext.as_bytes())
            .map_err(|e| format!("Encryption failed: {}", e))?;

        let mut combined = nonce_bytes.to_vec();
        combined.extend_from_slice(&ciphertext);
        Ok(BASE64.encode(&combined))
    }

    /// Decrypt base64(nonce + ciphertext), returns plaintext
    pub fn decrypt(&self, encrypted: &str) -> Result<String, String> {
        let data = BASE64
            .decode(encrypted)
            .map_err(|e| format!("Base64 decode failed: {}", e))?;

        if data.len() < 12 {
            return Err("Invalid encrypted data".to_string());
        }

        let nonce = Nonce::from_slice(&data[..12]);
        let plaintext = self
            .cipher
            .decrypt(nonce, &data[12..])
            .map_err(|e| format!("Decryption failed: {}", e))?;

        String::from_utf8(plaintext).map_err(|e| format!("Invalid UTF-8: {}", e))
    }
}

impl Drop for CryptoManager {
    fn drop(&mut self) {
        // Zeroize is handled by Aes256Gcm's Drop
    }
}

/// Generate a random salt for database encryption
pub fn generate_salt() -> [u8; 32] {
    let mut salt = [0u8; 32];
    OsRng.fill_bytes(&mut salt);
    salt
}
