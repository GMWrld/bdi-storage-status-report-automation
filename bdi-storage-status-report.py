import requests
import paramiko
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
import smtplib
from email.message import EmailMessage
import io

# ============================================================
# CONFIG SECTION (DUMMY VALUES — REPLACE IN REAL SETUP)
# ============================================================

# CYBERARK_API_URL = "https://cyberark.company.com/AIMWebService/api/Accounts"

CYBERARK_API_URL = "http://127.0.0.1:5000/AIMWebService/api/Accounts" #Dummy Url
APP_ID = "crdb_jenkins_automation"
SAFE_NAME = "Linux_Servers"

# Dummy server list (replace later)
SERVERS = [
    {"name": "Worker Node", "object": "esbroot_worker_node", "mount": "/nfsdata"},
    {"name": "EFK1", "object": "esbroot_efk1", "mount": "/elasticsearch"},
    {"name": "EFK2", "object": "esbroot_efk2", "mount": "/elasticsearch"},
    {"name": "EFK3", "object": "esbroot_efk3", "mount": "/elasticsearch"},
]

# Email settings (dummy for now)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "gm.wrld.13@gmail.com"
EMAIL_PASSWORD = "kseyxiyxnznkwvwd"
EMAIL_RECIPIENTS = ["gm.wrld.13@icloud.com"]

# ============================================================
# FUNCTION DEFINITIONS
# ============================================================


#OG Code
# def fetch_credentials(object_name):
#     """Fetch credentials from CyberArk CCP API"""
#     params = {"AppID": APP_ID, "Safe": SAFE_NAME, "Object": object_name}
#     resp = requests.get(CYBERARK_API_URL, params=params, verify=False)
#     resp.raise_for_status()
#     data = resp.json()
#     return data["UserName"], data["Address"], data["Password"]


#Dummy CyberArk
def fetch_credentials(object_name):
    """Fetch credentials from CyberArk CCP API (mock for testing)"""
    try:
        params = {"AppID": APP_ID, "Safe": SAFE_NAME, "Object": object_name}
        resp = requests.get(CYBERARK_API_URL, params=params, verify=False, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(data["Username"], data["Address"], data["Password"])
            return data["Username"], data["Address"], data["Password"]
        else:
            print(f"CyberArk API not reachable (status {resp.status_code}), using dummy creds...")
    except Exception as e:
        print(f"Could not connect to CyberArk: {e}, using dummy creds...")

    # Dummy fallback for testing
    return "testuser", "127.0.0.1", "testpass"


#OG Code
# def get_disk_usage(host, username, password, mount):
#     """SSH into the host and get df -h output"""
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(host, username=username, password=password, timeout=10)

#     cmd = f"df -h {mount} | tail -1"
#     stdin, stdout, stderr = ssh.exec_command(cmd)
#     line = stdout.read().decode().strip()
#     ssh.close()

#     parts = line.split()
#     filesystem, size, used, avail, use_perc, mount_point = parts
#     use_percent = int(use_perc.strip('%'))
#     return size, used, avail, use_percent, mount_point


#Dummy SSH
def get_disk_usage(host, username, password, mount):
    """Mock SSH logic for testing without real servers."""
    print(f"Mock SSH connection to {host} as {username} for mount {mount}")
    # Return fake data to simulate df -h output
    return "100G", "40G", "60G", 40, mount


def determine_status(usage):
    """Determine health status based on disk usage"""
    if usage < 75:
        return "Normal"
    elif 75 <= usage < 85:
        return "Monitor"
    else:
        return "Critical"

def send_email_report(df, filename):
    """Send the Excel report via email"""
    with io.BytesIO() as output:
        df.to_excel(output, index=False)
        output.seek(0)

        msg = EmailMessage()
        msg["Subject"] = "Disk Usage Report – Worker & EFK Nodes (Burundi)"
        msg["From"] = EMAIL_SENDER
        msg["To"] = ", ".join(EMAIL_RECIPIENTS)
        msg.set_content("Attached is the latest disk usage report.")

        msg.add_attachment(output.read(),
                           maintype="application",
                           subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           filename=filename)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            print("Email sent successfully.")

# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    records = []

    for s in SERVERS:
        print(f"Checking {s['name']}...")
        username, host, password = fetch_credentials(s["object"])
        size, used, avail, usage, mount = get_disk_usage(host, username, password, s["mount"])
        status = determine_status(usage)

        records.append({
            "Component": s["name"],
            "Total Size": size,
            "Used": used,
            "Available": avail,
            "Used%": f"{usage}%",
            "Mounted Point": mount,
            "Status": status
        })

    df = pd.DataFrame(records)
    filename = f"Disk_Usage_Report_Burundi_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    df.to_excel(filename, index=False)
    print(f"Report generated: {filename}")

    send_email_report(df, filename)

if __name__ == "__main__":
    main()
