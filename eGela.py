# -*- coding: UTF-8 -*-
import sys
from tkinter import messagebox
import requests
import urllib
from urllib.parse import unquote
from bs4 import BeautifulSoup
import time
import helper

class eGela:
    _login = 0
    _cookie = {"MoodleSessionegela":""}
    _curso = "https://egela.ehu.eus/course/view.php?id=107232"
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
            'username': username.get().strip(),
            'password': password.get().strip()
        }
        erantzuna = requests.request(method=metodo, url=uri, data=payload, cookies=_cookie, allow_redirects=False)
        print(erantzuna.request.method + " " + erantzuna.url)
        print(str(erantzuna.status_code) + " " + erantzuna.reason)
        print("")

        if erantzuna.status_code == 303:
            cookie = erantzuna.cookies.get("MoodleSessionegela")
            if cookie:
                self._cookie = {"MoodleSessionegela": cookie}
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
        erantzuna = requests.request(method=metodo, url=location, cookies=self._cookie, allow_redirects=False)
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
        erantzuna = requests.request(method=metodo, url=location, cookies=self._cookie, allow_redirects=False)
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
        if not self._cookie.get("MoodleSessionegela"):
            print("Ez da aurkitu MoodleSessionegela cookie-a")
            sys.exit(1)

        URI = self._curso
        goiburuak = {
            'Host': 'egela.ehu.eus'
        }

        #eGelara sartzeko eskaera egin
        erantzuna = requests.get(URI, headers=goiburuak, cookies=self._cookie, allow_redirects=False)

        if erantzuna.status_code == 303 and 'Location' in erantzuna.headers:
            print("Berbideraketa bat gertatu da, berbideratzen...")
            URI_erreala = erantzuna.headers['Location']
            erantzuna = requests.get(URI_erreala, headers=goiburuak, cookies=self._cookie, allow_redirects=False)

        html = erantzuna.text
        soup = BeautifulSoup(html, "html.parser")

        print("\n##### Analisis del HTML... #####")
        #############################################
        # ANALISIS DE LA PAGINA DEL AULA EN EGELA
        # PARA BUSCAR PDFs
        #############################################
        bisitatutako_link = set()

        #Kurtsoaren ID-a lortu azpi atalak bilatzeko
        kurtsoaren_id = None
        parsed_course = urllib.parse.urlparse(self._curso)
        qs_course = urllib.parse.parse_qs(parsed_course.query)
        if "id" in qs_course and qs_course["id"]:
            kurtsoaren_id = qs_course["id"][0]

        #Azpi atal guztien estekak lortu eta gorde
        atalenEstekak = {self._curso}
        for a in soup.find_all("a", href=True):
            href = a["href"]
            pdfLinka = urllib.parse.urljoin("https://egela.ehu.eus/", href)
            if "course/view.php" in pdfLinka:
                if kurtsoaren_id is None:
                    atalenEstekak.add(pdfLinka)
                else:
                    qs = urllib.parse.parse_qs(urllib.parse.urlparse(pdfLinka).query)
                    if qs.get("id", [None])[0] == kurtsoaren_id:
                        atalenEstekak.add(pdfLinka)

        #Atal bakoitzen esteketan PDF-k bilatu
        for orriarenURI in atalenEstekak:
            orriarenErantzuna = requests.get(orriarenURI, headers=goiburuak, cookies=self._cookie, allow_redirects=True)
            orriSoup = BeautifulSoup(orriarenErantzuna.text, "html.parser")

            #Atal horretan dagoen link-ak bilatu
            for a in orriSoup.find_all("a", href=True):
                href = a["href"]
                #Konprobatu PDF bat den bi modu desberdinetan
                #1. Modua: PDF-aren ikonoa bilatzen
                if "mod/resource" in href or "pluginfile.php" in href:
                    pdfLinka = urllib.parse.urljoin("https://egela.ehu.eus/", href)
                    estekarenTextua = a.get_text(strip=True).lower()
                    estekarenIkonoa = a.find_previous("img", class_="activityicon")
                    pdfDa = False
                    if estekarenIkonoa and estekarenIkonoa.get("src"):
                        pdfDa = "/f/pdf" in estekarenIkonoa["src"]
                #2. Modua: PDF-aren estekaren textuan .pdf hitza badagoen
                    if "pluginfile.php" in href:
                        parsed = urllib.parse.urlparse(pdfLinka)
                        if ".pdf" not in parsed.path.lower() and ".pdf" not in estekarenTextua:
                            continue
                    #PDF bat ez bada paso egin
                    else:
                        if not pdfDa:
                            continue
                    #Atalaren link-a gorde bisitatutako link-etan berriro ez bisitatzeko
                    if pdfLinka in bisitatutako_link:
                        continue
                    bisitatutako_link.add(pdfLinka)
                    a_copy = a
                    if a_copy.find("span", class_="accesshide"):
                        for span in a_copy.find_all("span", class_="accesshide"):
                            span.decompose()
                        pdfIzena = unquote(a_copy.get_text(strip=True))
                    else:
                        pdfIzena = unquote(a.get_text(strip=True))

                    if not pdfIzena.lower().endswith('.pdf'):
                        pdfIzena = pdfIzena + '.pdf'

                    #Zerrendan gorde
                    self._refs.append({
                        "pdf_name": pdfIzena,
                        "pdf_link": pdfLinka
                    })

        if len(self._refs) == 0:
            print(erantzuna.text)
            print("Ez da PDF estekarik aurkitu.")
            sys.exit(1)

        progress_step = float(100.0 / len(self._refs))

        #Bezeroak ikusten duen progresu barra eguneratu
        for _ in self._refs:
            progress += progress_step
            progress_var.set(progress)
            progress_bar.update()
            print("PDF izena: " + _["pdf_name"])
            print("PDF link: " + _["pdf_link"])
            print ("Progresoa: " + progress.__str__() + "%")
            print("")
            time.sleep(0.1)
        print("Fitxategi kopuru finala: " + len(self._refs).__str__() + " pdf")

        popup.destroy()
        return self._refs

    def get_pdf(self, selection):

        print("\t##### descargando  PDF... #####")
        cookie = self._cookie
        if not cookie.get("MoodleSessionegela"):
            print("Cookie-a ez dago oraindik ezarrita")
        else:
            print("Cookie-a = " + self._cookie["MoodleSessionegela"])
        # ARRAY-a KUDEATU
        print(" -----> FITXATEGIAREN INFORMAZIOA ESKURATZEN")
        pdf_info = self._refs[selection]
        pdf_name = pdf_info["pdf_name"]
        pdf_link = pdf_info["pdf_link"]

        try:
            import json as _json
            print("pdf_ref json: " + _json.dumps(pdf_info, ensure_ascii=False))
        except Exception:
            print(f"pdf_ref: {pdf_info}")

        print("pdf_izena:" + pdf_name)
        print("pdf_link:" + pdf_link)

        # HTTP ESKAERA
        print(" -----> HTTP ESKAERA EGITEN")
        erantzuna = requests.get(pdf_link, cookies=cookie, allow_redirects=True)
        print(erantzuna.request.method + " " + erantzuna.url)
        print(str(erantzuna.status_code) + " " + erantzuna.reason)
        print("")

        if erantzuna.status_code != 200:
            print(f"ERROR al descargar PDF: status {erantzuna.status_code}")
            return pdf_name, None

        # EDUKIA KUDEATZEN
        # Konprobatu PDF edo HTML den
        content_type = erantzuna.headers.get('Content-Type', '')
        print(f"Content-Type: {content_type}")

        if 'application/pdf' in content_type:
            pdf_content = erantzuna.content
        elif 'text/html' in content_type:
            print("Se detectó HTML, buscando el enlace al PDF...")
            soup = BeautifulSoup(erantzuna.text, "html.parser")

            resource_div = soup.find("div", class_="resourceworkaround")

            if resource_div:
                link_element = resource_div.find("a", href=True)

                if link_element:
                    real_pdf_link = link_element["href"]
                    print(f"Enlace al PDF encontrado: {real_pdf_link}")

                    real_pdf_link = urllib.parse.urljoin("https://egela.ehu.eus/", real_pdf_link)
                    erantzuna = requests.get(real_pdf_link, cookies=cookie, allow_redirects=True)
                    print(erantzuna.request.method + " " + erantzuna.url)
                    print(str(erantzuna.status_code) + " " + erantzuna.reason)
                    print("")

                    if erantzuna.status_code != 200:
                        print(f"ERROR al descargar el PDF del enlace encontrado: status {erantzuna.status_code}")
                        return pdf_name, None

                    pdf_content = erantzuna.content
                else:
                    print("ERROR: No se encontró elemento 'a' dentro del div resourceworkaround")
                    return pdf_name, None
            else:
                print("ERROR: No se encontró div con clase resourceworkaround")
                return pdf_name, None
        else:
            print(f"ERROR: Tipo de contenido no esperado: {content_type}")
            return pdf_name, None

        return pdf_name, pdf_content