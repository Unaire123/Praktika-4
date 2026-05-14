import requests
import urllib
import webbrowser
from socket import AF_INET, socket, SOCK_STREAM
import json
import helper

app_key = 'yk858315i30mt4y'
app_secret = 'gwdzegoqoauud4a'
server_addr = "localhost"
server_port = 8070
redirect_uri = "http://" + server_addr + ":" + str(server_port)

class Dropbox:
    _access_token = ""
    _path = "/"
    _files = []
    _root = None
    _msg_listbox = None

    def __init__(self, root):
        self._root = root

    def local_server(self):
        # por el puerto 8090 esta escuchando el servidor que generamos
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((server_addr, server_port))
        server_socket.listen(1)
        print("\tLocal server listening on port " + str(server_port))

        # recibe la redireccio 302 del navegador
        client_connection, client_address = server_socket.accept()
        peticion = client_connection.recv(1024)
        print("\tRequest from the browser received at local server:")
        print (peticion)

        # buscar en solicitud el "auth_code"
        primera_linea =peticion.decode('UTF8').split('\n')[0]
        aux_auth_code = primera_linea.split(' ')[1]
        auth_code = aux_auth_code[7:].split('&')[0]
        print ("\tauth_code: " + auth_code)

        # devolver una respuesta al usuario
        http_response = "HTTP/1.1 200 OK\r\n\r\n" \
                        "<html>" \
                        "<head><title>Proba</title></head>" \
                        "<body>The authentication flow has completed. Close this window.</body>" \
                        "</html>"
        client_connection.sendall(http_response.encode("utf-8"))
        client_connection.close()
        server_socket.close()

        return auth_code

    def do_oauth(self):
        #############################################
        # RELLENAR CON CODIGO DE LAS PETICIONES HTTP
        # Y PROCESAMIENTO DE LAS RESPUESTAS HTTP
        # PARA LA OBTENCION DEL ACCESS TOKEN
        #############################################

        #HTTP eskaeraren parametroak prestatu
        servidor = 'www.dropbox.com'
        params = {
            'response_type': 'code',
            'client_id': app_key,
            'redirect_uri': redirect_uri
        }

        #Parametroak parseatu URI barruan sartzeko
        params_encoded = urllib.parse.urlencode(params)
        recurso = '/oauth2/authorize?' + params_encoded
        uri = 'https://' + servidor + recurso
        #Nabigatzailea ireki parseatutako URI-arekin saioa hasteko
        webbrowser.open_new(uri)

        auth_code = self.local_server()

        #Behin saioa hasita, aplikazioan sartzeko eskaera prestatu
        token_url = 'https://api.dropboxapi.com/oauth2/token'
        data = {
            'code': auth_code,
            'grant_type': 'authorization_code',
            'client_id': app_key,
            'client_secret': app_secret,
            'redirect_uri': redirect_uri
        }

        #Aplikazioan sartzeko eskaera egin
        token_resp = requests.post(token_url, data=data)
        token_resp.raise_for_status()
        token_json = token_resp.json()
        self._access_token = token_json.get('access_token', '')
        print(f"Access token: {self._access_token}")

        self._root.destroy()

    def list_folder(self, msg_listbox):
        print("/list_folder")
        uri = 'https://api.dropboxapi.com/2/files/list_folder'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-list_folder
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################
        path = self._path
        if path in (None, "/"):
            path = ""

        datuak = {
            'path': path,
            'recursive': False,
            'include_media_info': False,
            'include_deleted': False,
            'include_has_explicit_shared_members': False,
            'include_mounted_folders': True,
            'include_non_downloadable_files': True
        }
        datuak_encoded = json.dumps(datuak)
        print("Datuak: " + datuak_encoded)
        headers = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json'}
        erantzuna = requests.post(uri, headers=headers, data=datuak_encoded, allow_redirects=False)
        status = erantzuna.status_code
        print("\tStatus: " + str(status))
        print("\tHeaders respuesta: " + str(erantzuna.headers))
        edukia = erantzuna.text
        print("\tEdukia: [" + edukia + "]")
        print("\tContent-Length: " + str(len(edukia)))

        if status != 200:
            print(f"ERROR: Status {status}")
            print(f"Raw content: {erantzuna.content}")
            try:
                error_json = erantzuna.json()
                print(f"Error JSON: {error_json}")
            except:
                print("No se pudo parsear error como JSON")
            return

        try:
            edukia_json = json.loads(edukia)
        except json.JSONDecodeError as e:
            print(f"ERROR JSON: {e}")
            return

        print("Fitxategiak --> " + path)
        for entrie in edukia_json["entries"]:
            print(entrie['name'])
        self._files = helper.update_listbox2(msg_listbox, self._path, edukia_json)

    def transfer_file(self, file_path, file_data):
        print("/upload")
        uri = 'https://content.dropboxapi.com/2/files/upload'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-upload

        datuak = {'path': file_path,
                 'mode': 'add'}
        datuak_encoded = json.dumps(datuak)

        headers = {'Host': 'content.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'DropBox-API-Arg': datuak_encoded,
                     'Content-Type': 'application/octet-stream'}

        erantzuna = requests.post(uri, headers=headers, allow_redirects=False, data=file_data)
        status = erantzuna.status_code
        print("\tStatus: " + str(status))
        if (status == 200):
            print("Fitxategia ondo igo da: " + file_path + "-era")
            edukia = erantzuna.text
            print("\tEdukia:" + edukia)
        else:
            print("\tERROR: Ftixategia igotzean")

    def delete_file(self, file_path):
        print("/delete_file")
        uri = 'https://api.dropboxapi.com/2/files/delete_v2'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-delete
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################
        datuak = {'path': file_path }

        datuak_encoded = json.dumps(datuak)

        headers = {'Host': 'api.dropboxapi.com',
                   'Authorization': 'Bearer ' + self._access_token,
                   'Content-Type': 'application/json'}

        erantzuna = requests.post(uri, headers=headers, allow_redirects=False, data=datuak_encoded)
        status = erantzuna.status_code
        print("\tStatus: " + str(status))
        if (status == 200):
            print("Fitxategia ezabatu da: " + file_path)
            edukia = erantzuna.text
            print("\tEdukia:" + edukia)
        else:
            print("\tERROR: Ftixategia igotzean")

    def create_folder(self, path):
        print("/create_folder")
       # https://www.dropbox.com/developers/documentation/http/documentation#files-create_folder
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################
