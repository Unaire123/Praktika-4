# -*- coding: UTF-8 -*-
from tkinter import messagebox
import requests
import urllib
from urllib.parse import unquote
from bs4 import BeautifulSoup
import time
import helper

class eGela:
    _login = 0
    _cookie = ""
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
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        progress = 25
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)


        print("\n##### 2. PETICION #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        progress = 50
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        print("\n##### 3. PETICION #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        progress = 75
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)
        popup.destroy()

        print("\n##### 4. PETICION #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        progress = 100
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)
        popup.destroy()


        if COMPROBACION_DE_LOG_IN:
            #############################################
            # ACTUALIZAR VARIABLES
            #############################################
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
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        return pdf_name, pdf_content