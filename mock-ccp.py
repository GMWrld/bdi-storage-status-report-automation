from flask import Flask, request, jsonify

app = Flask(__name__)

# 🗄️ Mock database of credentials (pretend these are stored in CyberArk)
mock_credentials = {
    "esbroot_worker_node": {
        "Username": "esbroot",
        "Address": "10.10.10.101",
        "Password": "SuperSecurePassword123!"
    },
    "esbroot_efk1": {
        "Username": "esbroot_efk1",
        "Address": "10.10.10.102",
        "Password": "SuperSecurePassword123!"
    },
    "db_admin": {
        "Username": "dbadmin",
        "Address": "10.10.10.102",
        "Password": "DBpassword#2024"
    },
    "jenkins_agent": {
        "Username": "jenkinsuser",
        "Address": "10.10.10.103",
        "Password": "Jenkins@Pass123"
    }
}


@app.route("/AIMWebService/api/Accounts", methods=["GET"])
def get_account():
    """
    Mock endpoint for CyberArk CCP API
    Example request:
      GET /AIMWebService/api/Accounts?AppID=jenkins_automation&Safe=Linux_Servers&Object=esbroot_worker_node
    """
    obj = request.args.get("Object")
    if not obj:
        return jsonify({"Error": "Missing Object parameter"}), 400

    creds = mock_credentials.get(obj)
    if creds:
        return jsonify(creds)
    else:
        return jsonify({"Error": f"No credentials found for {obj}"}), 404


if __name__ == "__main__":
    print("Mock CyberArk CCP server running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000)
