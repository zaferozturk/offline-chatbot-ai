from flask import Flask, request, jsonify
import paramiko

app = Flask(__name__)

def ssh_command(host, username, password, command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, timeout=10)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        client.close()

        if error:
            return f"[SSH Error] {error.strip()}"
        return output.strip()
    except Exception as e:
        return f"[SSH connection error] {e}"

def get_system_info(host, username, password):
    commands = {
        "Hostname": "hostname",
        "OS Version": "uname -a",
        "Disk Usage": "df -h /",
        "RAM Usage": "free -h",
        "CPU Info": "lscpu",
        "Network Info": "ifconfig",
        "Routing Table": "route -n"
    }

    results = []
    for title, cmd in commands.items():
        output = ssh_command(host, username, password, cmd)
        if output.startswith("[SSH connection error]") or output.startswith("[SSH Error]"):
            return output
        results.append(f"### {title}\n```\n{output}\n```")

    return "\n\n".join(results)

@app.route("/mcp", methods=["POST"])
def handle_command():
    data = request.get_json()
    host = data.get("host")
    username = data.get("username")
    password = data.get("password")
    command = data.get("command", "").lower()

    if not all([host, username, password]):
        return jsonify({"result": "❗ Missing SSH credentials (host, username, password)."}), 400

    if command == "system_info":
        output = get_system_info(host, username, password)
    else:
        return jsonify({"result": "❗ Command not recognized by MCP agent."}), 400

    return jsonify({"result": output})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
