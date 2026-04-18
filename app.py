from flask import Flask, request, jsonify
from datetime import datetime
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib3
import base64
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()

def decode_jwt(token):
    """فك تشفير التوكن JWT لاستخراج البيانات"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        payload = parts[1]
        
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        
        decoded_bytes = base64.urlsafe_b64decode(payload)
        decoded_data = json.loads(decoded_bytes)
        
        return decoded_data
    except Exception as e:
        print(f"Error decoding JWT: {e}")
        return None

def get_server_from_region(region):
    """تحديد السيرفر بناءً على المنطقة"""
    server_mapping = {
        "EUROPE": "Europe Server",
        "ASIA": "Asia Server",
        "MIDDLE_EAST": "Middle East Server",
        "NORTH_AMERICA": "North America Server",
        "SOUTH_AMERICA": "South America Server",
        
    }
    return server_mapping.get(region, f"Unknown Server ({region})")

def TOKEN_MAKER(OLD_ACCESS_TOKEN, NEW_ACCESS_TOKEN, OLD_OPEN_ID, NEW_OPEN_ID, uid):
    now = datetime.now()
    now = str(now)[:len(str(now)) - 7]
    data = bytes.fromhex('1a13323032352d31312d32362030313a35313a3238220966726565206669726528013a07312e3132332e314232416e64726f6964204f532039202f204150492d3238202850492f72656c2e636a772e32303232303531382e313134313333294a0848616e6468656c64520c4d544e2f537061636574656c5a045749464960800a68d00572033234307a2d7838362d3634205353453320535345342e3120535345342e32204156582041565832207c2032343030207c20348001e61e8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e329a012b476f6f676c657c36323566373136662d393161372d343935622d396631362d303866653964336336353333a2010e3137362e32382e3133392e313835aa01026172b201203433303632343537393364653836646134323561353263616164663231656564ba010134c2010848616e6468656c64ca010d4f6e65506c7573204135303130ea014063363961653230386661643732373338623637346232383437623530613361316466613235643161313966616537343566633736616334613065343134633934f00101ca020c4d544e2f537061636574656cd2020457494649ca03203161633462383065636630343738613434323033626638666163363132306635e003b5ee02e8039a8002f003af13f80384078004a78f028804b5ee029004a78f029804b5ee02b00404c80401d2043d2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f6c69622f61726de00401ea045f65363261623933353464386662356662303831646233333861636233333439317c2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f626173652e61706bf00406f804018a050233329a050a32303139313139303236a80503b205094f70656e474c455332b805ff01c00504e005be7eea05093372645f7061727479f205704b717348543857393347646347335a6f7a454e6646775648746d377171316552554e6149444e67526f626f7a4942744c4f695943633459367a767670634943787a514632734f453463627974774c7334785a62526e70524d706d5752514b6d654f35766373386e51594268777148374bf805e7e4068806019006019a060134a2060134b2062213521146500e590349510e460900115843395f005b510f685b560a6107576d0f0366')
    data = data.replace(OLD_OPEN_ID.encode(), NEW_OPEN_ID.encode())
    data = data.replace(OLD_ACCESS_TOKEN.encode(), NEW_ACCESS_TOKEN.encode())
    d = encrypt_api(data.hex())
    Final_Payload = bytes.fromhex(d)
    
    headers = {
        "Host": "loginbp.ggblueshark.com",
        "X-Unity-Version": "2018.4.36f1",
        "Accept": "*/*",
        "Authorization": "Bearer",
        "ReleaseVersion": "OB53",
        "X-GA": "v1 1",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(Final_Payload)),
        "User-Agent": "Free%20Fire/2019119624 CFNetwork/3826.500.111.2.2 Darwin/24.4.0",
        "Connection": "keep-alive"
    }
    
    URL = "https://loginbp.ggblueshark.com/MajorLogin"
    RESPONSE = requests.post(URL, headers=headers, data=Final_Payload, verify=False)
    
    if RESPONSE.status_code == 200:
        if len(RESPONSE.text) < 10:
            return False
        BASE64_TOKEN = RESPONSE.text[RESPONSE.text.find("eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ"):-1]
        second_dot_index = BASE64_TOKEN.find(".", BASE64_TOKEN.find(".") + 1)
        BASE64_TOKEN = BASE64_TOKEN[:second_dot_index + 44]
        return BASE64_TOKEN
    else:
        print(f"MajorLogin failed with status: {RESPONSE.status_code}")
        print(f"Response: {RESPONSE.text}")
        return False

@app.route('/get', methods=['GET'])
def check_token():
    try:
        uid = request.args.get('uid')
        password = request.args.get('password')
        
        if not uid or not password:
            return jsonify({
                "status": "error",
                "message": "Missing uid or password parameter",
                "TEAM": "CTX",
                "Dev": "@VINOX_HUB"
            })
        
        
        TEAM = "VINOX_HUB"
        DEV = "@VINOX_HUB"
        
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close",
        }
        data = {
            "uid": f"{uid}",
            "password": f"{password}",
            "response_type": "token",
            "client_type": "2",
            "client_secret": "",
            "client_id": "100067",
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        try:
            garena_data = response.json()
            print("RESPONSE JSON:", garena_data)
        except Exception as e:
            print("FAILED TO PARSE JSON:", response.text)
            return jsonify({
                "status": "error", 
                "message": "Invalid response from Garena",
                "TEAM": TEAM,
                "Dev": DEV
            })

        if "access_token" not in garena_data or "open_id" not in garena_data:
            return jsonify({
                "status": "error", 
                "message": f"Missing keys in response: {garena_data}",
                "TEAM": TEAM,
                "Dev": DEV
            })

        NEW_ACCESS_TOKEN = garena_data['access_token']
        NEW_OPEN_ID = garena_data['open_id']
        
        
        access_token_garena = garena_data.get('access_token', 'N/A')
        
        OLD_ACCESS_TOKEN = "c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94"
        OLD_OPEN_ID = "4306245793de86da425a52caadf21eed"
        
        token = TOKEN_MAKER(OLD_ACCESS_TOKEN, NEW_ACCESS_TOKEN, OLD_OPEN_ID, NEW_OPEN_ID, uid)
        
        if token:
           
            token_data = decode_jwt(token)
            
            if token_data:
            
                account_id = token_data.get('account_id', 'N/A')
                nickname = token_data.get('nickname', 'N/A')
                noti_region = token_data.get('noti_region', 'N/A')
                lock_region = token_data.get('lock_region', 'N/A')
                external_id = token_data.get('external_id', 'N/A')
                country_code = token_data.get('country_code', 'N/A')
                external_uid = token_data.get('external_uid', 'N/A')
                
                
                exp_timestamp = token_data.get('exp', 'N/A')
                exp_date = 'N/A'
                if exp_timestamp != 'N/A':
                    try:
                        exp_date = datetime.fromtimestamp(exp_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        exp_date = str(exp_timestamp)
                
                
                server = get_server_from_region(lock_region or noti_region)
                
                return jsonify({
                    "status": "success",
                    "token": token,
                    "access_token": access_token_garena,  
                    "account_info": {
                        "account_id": account_id,
                        "uid": uid,
                        "password": password,
                        "external_uid": external_uid,
                        "nickname": nickname,
                        "server": server,
                        "region": lock_region or noti_region,
                        "country_code": country_code,
                        "external_id": external_id,
                        "token_expiry": exp_date
                    },
                    "garena_tokens": {  
                        "access_token": access_token_garena,
                        "open_id": garena_data.get('open_id', 'N/A'),
                        "refresh_token": garena_data.get('refresh_token', 'N/A'),
                        "expires_in": garena_data.get('expires_in', 'N/A'),
                        "scope": garena_data.get('scope', 'N/A')
                    },
                    "decoded_token": token_data,
                    "response_data": garena_data,  
                    "TEAM": TEAM,
                    "Dev": DEV
                })
            else:
               
                return jsonify({
                    "status": "success",
                    "token": token,
                    "access_token": access_token_garena,  
                    "account_info": {
                        "uid": uid,
                        "password": password,
                        "message": "Token generated successfully but could not decode for additional info"
                    },
                    "garena_tokens": {
                        "access_token": access_token_garena,
                        "open_id": garena_data.get('open_id', 'N/A')
                    },
                    "TEAM": TEAM,
                    "Dev": DEV
                })
        else:
            return jsonify({
                "status": "failure", 
                "message": "Failed to generate token",
                "TEAM": TEAM,
                "Dev": DEV
            })
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e),
            "TEAM": "VIP",
            "Dev": "@VINOX_HUB"
        })

@app.route('/decode_token', methods=['GET'])
def decode_token_endpoint():
    try:
        token = request.args.get('token')
        if not token:
            return jsonify({"status": "error", "message": "Token missing"})
        
        token_data = decode_jwt(token)
        
        if token_data:
           
            account_id = token_data.get('account_id', token_data.get('uid', 'N/A'))
            nickname = token_data.get('nickname', 'N/A')
            
            
            region = token_data.get('region', token_data.get('lock_region', token_data.get('noti_region', 'N/A')))
            
          
            external_id = token_data.get('external_id', token_data.get('access_token', 'N/A'))
            
            exp_timestamp = token_data.get('exp', 'N/A')
            exp_date = 'N/A'
            if exp_timestamp != 'N/A':
                try:
                    exp_date = datetime.fromtimestamp(exp_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    exp_date = str(exp_timestamp)
            
         
            server = get_server_from_region(region)
            
            return jsonify({
                "status": "success",
                "decoded_token": token_data,
                "account_info": {
                    "account_id": account_id,
                    "nickname": nickname,
                    "server": server,
                    "region": region,
                    "country_code": token_data.get('country_code', 'N/A'),
                    "external_id": external_id,
                    "token_expiry": exp_date
                },
                "TEAM": "VNX",
                "Dev": "@VINOX_HUB"
            })
        else:
            return jsonify({"status": "error", "message": "Failed to decode token"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=25715, debug=True)