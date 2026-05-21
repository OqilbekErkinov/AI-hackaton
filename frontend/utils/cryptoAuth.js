// utils/cryptoAuth.js
// Web Crypto PBKDF2 yordamida parolni salt bilan derivatsiya qilish

function bufToHex(buf) {
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
}
function hexToBuf(hex) {
  const bytes = new Uint8Array(hex.length/2);
  for (let i=0;i<bytes.length;i++){
    bytes[i] = parseInt(hex.substr(i*2,2),16);
  }
  return bytes.buffer;
}

export async function genSalt(len = 16) {
  const a = new Uint8Array(len);
  crypto.getRandomValues(a);
  return bufToHex(a.buffer);
}

export async function deriveKey(password, saltHex, iterations = 120000, keyLen = 32) {
  const enc = new TextEncoder();
  const passKey = await crypto.subtle.importKey(
    'raw',
    enc.encode(password),
    { name: 'PBKDF2' },
    false,
    ['deriveBits']
  );
  const saltBuf = hexToBuf(saltHex);
  const derived = await crypto.subtle.deriveBits(
    {
      name: 'PBKDF2',
      salt: saltBuf,
      iterations,
      hash: 'SHA-256'
    },
    passKey,
    keyLen * 8
  );
  return bufToHex(derived);
}
