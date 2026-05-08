# -*- coding: UTF-8 -*-
import sys
from tkinter import messagebox
import requests
import urllib
from urllib.parse import unquote
from bs4 import BeautifulSoup
import time
import helper
import json

class eGela:
    _login = 0
    _cookie = {"MoodleSessionegela":""}
    _curso = ""
    _refs = []
    _root = None

    def __init__(self, root):
        self._root = root

    def check_credentials(self, username, password, event=None):
        popup, progress_var, progress_bar = helper.progress("check_credentials", "Logging into eGela...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("##### 1. PETICION #####")
        metodo = 'GET'
        uri = "https://egela.ehu.eus/login/index.php"

        erantzuna = requests.request(method=metodo, url=uri, allow_redirects=False)
        print(erantzuna.request.method + " " + erantzuna.url)
        print(str(erantzuna.status_code) + " " + erantzuna.reason)
        print("")

        edukia = erantzuna.content
        ref_doc = BeautifulSoup(edukia, "html.parser")
        logintoken = ref_doc.find('input', {'name': 'logintoken'}).get('value')
        if not logintoken:
            print("Errorea: Ez da aurkitu logintoken.")
            sys.exit(1)

        cookie = erantzuna.cookies.get("MoodleSessionegela")
        if cookie:
            _cookie = {"MoodleSessionegela": cookie}
        else:
            print("Errorea: Ez da aurkitu MoodleSessionegela.")
            sys.exit(1)

        progress = 25
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)


        print("\n##### 2. PETICION #####")

        metodo = 'POST'
        uri = "https://egela.ehu.eus/login/index.php"
        payload = {
            'logintoken': logintoken,
            'username': username,
            'password': password
        }
        erantzuna = requests.request(method=metodo, url=uri, data=payload, cookies=_cookie, allow_redirects=False)
        print(erantzuna.request.method + " " + erantzuna.url)
        print(str(erantzuna.status_code) + " " + erantzuna.reason)
        print("")

        if erantzuna.status_code == 303:
            cookie = erantzuna.cookies.get("MoodleSessionegela")
            if cookie:
                _cookie = {"MoodleSessionegela": cookie}
            else:
                print("Errorea: Ez da aurkitu MoodleSessionegela.")
                sys.exit(1)

            location = erantzuna.headers.get("Location")
            if not location:
                print("Errorea: Ez da aurkitu hurrengo helbidea.")
                sys.exit(1)

            print("")
        else:
            print("\nERROREA: Erabiltzailea edo pasahitza txarto sartu dituzu!")
            sys.exit(1)

        progress = 50
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        print("\n##### 3. PETICION #####")
        metodo = 'POST'
        erantzuna = requests.request(method=metodo, url=location, cookies=_cookie, allow_redirects=False)
        print(erantzuna.request.method + " " + erantzuna.url)
        print(str(erantzuna.status_code) + " " + erantzuna.reason)
        print("")

        if erantzuna.status_code == 303:
            location = erantzuna.headers.get("Location")
            if not location:
                print("Errorea: Ez da aurkitu hurrengo helbidea.")
                sys.exit(1)
        else:
            print("\nERROREA: Erabiltzailea edo pasahitza txarto sartu dituzu!")
            sys.exit(1)

        progress = 75
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)
        popup.destroy()

        print("\n##### 4. PETICION #####")

        metodo = 'GET'
        erantzuna = requests.request(method=metodo, url=location, cookies=_cookie, allow_redirects=False)
        print(erantzuna.request.method + " " + erantzuna.url)
        print(str(erantzuna.status_code) + " " + erantzuna.reason)
        print("")

        progress = 100
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)
        popup.destroy()

        if erantzuna.status_code == 200:
            self._login = 1
            self._root.destroy()
        else:
            messagebox.showinfo("Alert Message", "Login incorrect!")

    def get_pdf_refs(self):
        popup, progress_var, progress_bar = helper.progress("get_pdf_refs", "Downloading PDF list...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("\n##### 4. PETICION (Página principal de la asignatura en eGela) #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################
        url = self._curso
        headers = {
            'Host': 'egela.ehu.eus',
            'Cookie': self._cookie
        }

        resp = requests.get(url, headers=headers, allow_redirects=False)
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        if requests.status_code == 303 and 'Location':
            print("Berbideraketa bat gertatu da, berbideratzen...")
            url_erreala = resp.headers['Location']
            resp = requests.get(url_erreala, headers=headers, allow_redirects=False)


        print("\n##### Analisis del HTML... #####")
        #############################################
        # ANALISIS DE LA PAGINA DEL AULA EN EGELA
        # PARA BUSCAR PDFs
        #############################################
        pdf_links = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "mod/resource" in href or "pluginfile.php" in href:
                pdf_links.append(href)

        progress_step = float(100.0 / len(pdf_links))

        for href in pdf_links:
            abs_url = urllib.parse.urljoin("https://egela.ehu.eus/", href)
            self._refs.append(abs_url)

            progress += progress_step
            progress_var.set(progress)
            progress_bar.update()
            time.sleep(0.1)

        popup.destroy()
        return self._refs

    def get_pdf(self, selection):

        print("\t##### descargando  PDF... #####")
        cookie = self._cookie
        if cookie == "":
            print("Cookie-a ez dago oraindik ezarrita")
        else:
            print("Cookie-a = " + cookie)
        # ARRAY-a KUDEATU
        print(" -----> FITXATEGIAREN INFORMAZIOA ESKURATZEN")
        pdf_ref = self._refs[selection]
        print("pdf_ref raw: " + pdf_ref)
        pdf_info = json.loads(pdf_ref)
        print("pdf_ref json:" + pdf_info)
        pdf_name = pdf_info["pdf_name"]
        print("pdf_izena:" + pdf_name)
        pdf_link = pdf_info["pdf_link"]
        print("pdf_link:" + pdf_link)

        # HTTP ESKAERA
        print(" -----> HTTP ESKAERA EGITEN")
        erantzuna = requests.get(pdf_link, cookies=cookie, allow_redirects=False)
        print(erantzuna.request.method + " " + erantzuna.url)
        print(str(erantzuna.status_code) + " " + erantzuna.reason)
        print("")

        # EDUKIA KUDEATZEN
        pdf_content = erantzuna.content

        return pdf_name, pdf_content