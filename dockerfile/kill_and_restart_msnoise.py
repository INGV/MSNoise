import subprocess
import os

# Function to kill the process using port 5000
def kill_process_on_port(port):
    try:
        # Find the process using the port
        result = subprocess.run(
            ['netstat', '-tulpn'],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if f':{port}' in line:
                # Extract PID (7th column and cut before "/")
                pid = line.split()[6].split('/')[0]
                # Kill the process
                os.kill(int(pid), 9)
                print(f"Killed process with PID {pid} using port {port}.")
    except Exception as e:
        print(f"Error killing process: {e}")

# Function to restart msnoise admin
def restart_msnoise():
    try:
        subprocess.run(['/home/msnoise/.local/bin/msnoise', 'admin'], check=True)
        print("Restarted msnoise admin successfully.")
    except Exception as e:
        print(f"Error restarting msnoise: {e}")

# Main function
def main():
    port = 5000
    kill_process_on_port(port)
    restart_msnoise()

if __name__ == "__main__":
    main()
