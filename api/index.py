from flask import Flask, render_template, request, Response, stream_with_context
import yaml, json, os, base64, binascii, time
from Source.Request import AuthUtils
from Source.Client import CreateClient

# Configure Flask for Vercel folder structure
app = Flask(__name__, template_folder="../templates", static_folder="../static")

# Load configuration and initialize utilities
ConfigJson = yaml.safe_load(open("Config.yaml", "r"))
AuthFunc = AuthUtils(ConfigJson, CreateClient())

def TokenId(Token: str):
    TokenId = Token.split(".")[0]
    for i in range(3):
        try:
            TokenId = base64.b64decode(TokenId)
            break
        except binascii.Error:
            TokenId += "="
    return int(TokenId.decode(encoding="utf-8"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_process():
    data = request.json
    guild_id = data.get('guild_id')
    
    if not guild_id:
        return {"error": "Server ID is required"}, 400

    def generate_logs():
        yield json.dumps({"status": "Connecting...", "type": "info"}) + "\n"
        
        # Read Tokens
        tokens = []
        try:
            with open('Input/Token.txt', encoding="utf-8") as file:
                while lines := file.readline():
                    tokens.append(lines.rstrip())
        except Exception as e:
            yield json.dumps({"status": f"Error reading tokens: {str(e)}", "type": "error"}) + "\n"
            return

        total_tokens = len(tokens)
        yield json.dumps({"status": f"Processing {total_tokens} tokens...", "type": "info", "total": total_tokens}) + "\n"

        for index, token in enumerate(tokens):
            access_token = None # Simplified for the loop, you can integrate Auths.json logic here if needed
            
            # Step 1: Location & Auth
            location_process = AuthFunc.FetchLocation(Token=token)
            if location_process['success']:
                auth_process = AuthFunc.FetchAuth(code=location_process['code'])
                if auth_process['success']:
                    access_token = auth_process['Auth']['AccessToken']
                else:
                    yield json.dumps({"status": f"Auth Denied for token ending in ...{token[-4:]} - {auth_process.get('message')}", "type": "error", "progress": index + 1}) + "\n"
                    continue
            else:
                yield json.dumps({"status": f"Location Denied for token ending in ...{token[-4:]} - {location_process.get('message')}", "type": "error", "progress": index + 1}) + "\n"
                continue

            # Step 2: Join Guild
            if access_token:
                join_process = AuthFunc.AuthJoin(
                    AccessToken=access_token,
                    UserId=TokenId(Token=token),
                    GuildId=int(guild_id)
                )
                
                if join_process['success']:
                    yield json.dumps({"status": f"Successfully joined Server {guild_id} (Token: ...{token[-4:]})", "type": "success", "progress": index + 1}) + "\n"
                else:
                    yield json.dumps({"status": f"Failed to join Server {guild_id} (Token: ...{token[-4:]}) - {join_process.get('message')}", "type": "error", "progress": index + 1}) + "\n"
            
            # Small delay to prevent rate limits
            time.sleep(0.5)

        yield json.dumps({"status": "Completed!", "type": "done"}) + "\n"

    return Response(stream_with_context(generate_logs()), mimetype='application/x-ndjson')
