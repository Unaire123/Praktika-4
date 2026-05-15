# -*- coding: UTF-8 -*-
import tkinter as tk
import os
from tkinter import messagebox

import eGela
import Dropbox
import helper
import time
from urllib.parse import unquote

##########################################################################################################

def make_entry(parent, caption, width=None, **options):
    label = tk.Label(parent, text=caption)
    label.pack(side=tk.TOP)
    entry = tk.Entry(parent, **options)
    entry.config(width=width)
    entry.pack(side=tk.TOP, padx=10, fill=tk.BOTH)
    return entry

def make_listbox(messages_frame):
    messages_frame.config(bd=1, relief="ridge")
    scrollbar = tk.Scrollbar(messages_frame)
    msg_listbox = tk.Listbox(messages_frame, height=20, width=70, exportselection=0, selectmode=tk.EXTENDED)
    msg_listbox.configure(yscrollcommand=scrollbar.set)
    scrollbar.configure(command=msg_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    return msg_listbox

def transfer_files():
    popup, progress_var, progress_bar = helper.progress("transfer_file", "Transfering files...")
    progress = 0
    progress_var.set(progress)
    progress_bar.update()
    progress_step = float(100.0 / len(selected_items1))

    for each in selected_items1:
        pdf_name, pdf_file = egela.get_pdf(each)

        progress_bar.update()
        newroot.update()

        if dropbox._path == "/":
            path = "/" + unquote(pdf_name)
            print ("----------------------: "+ pdf_name)
            print("----------------------: " + unquote(pdf_name))

        else:
            path = dropbox._path + "/" + pdf_name
        dropbox.transfer_file(path, pdf_file)

        progress += progress_step
        progress_var.set(progress)
        progress_bar.update()
        newroot.update()

        time.sleep(0.1)

    popup.destroy()
    dropbox.list_folder(msg_listbox2)
    msg_listbox2.yview(tk.END)

def delete_files():
    popup, progress_var, progress_bar = helper.progress("delete_file", "Deleting files...")
    progress = 0
    progress_var.set(progress)
    progress_bar.update()
    progress_step = float(100.0 / len(selected_items2))

    for each in selected_items2:
        if dropbox._path == "/":
            path = "/" + dropbox._files[each]['name']
        else:
            path = dropbox._path + "/" + dropbox._files[each]['name']
            print (path)
        dropbox.delete_file(path)

        progress += progress_step
        progress_var.set(progress)
        progress_bar.update()

    popup.destroy()
    dropbox.list_folder(msg_listbox2)

def name_folder(folder_name):
    if dropbox._path == "/":
        dropbox._path = dropbox._path + str(folder_name)
    else:
        dropbox._path = dropbox._path + '/' + str(folder_name)
    dropbox.create_folder(dropbox._path)
    var.set(dropbox._path)
    dropbox._root.destroy()
    dropbox.list_folder(msg_listbox2)

def create_folder():
    popup = tk.Toplevel(newroot)
    popup.geometry('200x100')
    popup.title('Dropbox')
    helper.set_icon(popup)
    helper.center(popup)

    login_frame = tk.Frame(popup, padx=10, pady=10)
    login_frame.pack(fill=tk.BOTH, expand=True)

    label = tk.Label(login_frame, text="Create folder")
    label.pack(side=tk.TOP)
    entry_field = tk.Entry(login_frame, width=35)
    entry_field.bind("<Return>", name_folder)
    entry_field.pack(side=tk.TOP)
    send_button = tk.Button(login_frame, text="Send", command=lambda: name_folder(entry_field.get()))
    send_button.pack(side=tk.TOP)
    dropbox._root = popup


def rename_file():
    widget = msg_listbox2
    selection = widget.curselection()

    if not selection:
        print("Ez da ezer aukeratu")
        return

    if selection[0] == 0 and dropbox._path != "/":
        print("Ezin da erroa izenez aldatu")
        return

    selected_file = dropbox._files[selection[0]]
    old_name = selected_file['name']

    popup = tk.Toplevel(newroot)
    popup.geometry('250x120')
    popup.title('Izena aldatu')
    helper.set_icon(popup)
    helper.center(popup)

    rename_frame = tk.Frame(popup, padx=10, pady=10)
    rename_frame.pack(fill=tk.BOTH, expand=True)

    label = tk.Label(rename_frame, text=f"Oraingo izena: {old_name}")
    label.pack(side=tk.TOP, pady=5)

    label2 = tk.Label(rename_frame, text="Izen berria:")
    label2.pack(side=tk.TOP)

    entry_field = tk.Entry(rename_frame, width=35)
    entry_field.insert(0, old_name)  # Pre-rellenar con el nombre actual
    entry_field.pack(side=tk.TOP, pady=5)

    def do_rename(new_name):
        if not new_name.strip():
            print("Izena ezin da zuriz hutsi")
            return

        if dropbox._path == "/":
            old_path = "/" + old_name
            new_path_full = "/" + new_name
        else:
            old_path = dropbox._path + "/" + old_name
            new_path_full = dropbox._path + "/" + new_name

        print(f"Izena aldatzen: {old_path} -> {new_path_full}")
        dropbox.rename_file(old_path, new_name)
        popup.destroy()
        dropbox.list_folder(msg_listbox2)

    send_button = tk.Button(rename_frame, text="Rename",
                            command=lambda: do_rename(entry_field.get()))
    send_button.pack(side=tk.TOP, pady=5)

    entry_field.bind("<Return>", lambda e: do_rename(entry_field.get()))

def move_file():
    widget = msg_listbox2
    selection = widget.curselection()

    if not selection:
        messagebox.showwarning("Move File", "Ez da ezer aukeratu")
        return

    if selection[0] == 0 and dropbox._path != "/":
        messagebox.showwarning("Move File", "Ezin da erroa mugitu")
        return

    selected_file = dropbox._files[selection[0]]
    file_name = selected_file['name']

    directories = dropbox.get_all_directories("/")

    if not directories:
        messagebox.showwarning("Move File", "Ez dago direktorio erabilgarririk. Sortu karpeta bat lehenengo")
        return

    popup = tk.Toplevel(newroot)
    popup.geometry('300x400')
    popup.title('Mugitu fitxategia')
    helper.set_icon(popup)
    helper.center(popup)

    move_frame = tk.Frame(popup, padx=10, pady=10)
    move_frame.pack(fill=tk.BOTH, expand=True)

    label = tk.Label(move_frame, text=f"Aukeratu helmugua:\n{file_name}")
    label.pack(side=tk.TOP, pady=10)

    scrollbar = tk.Scrollbar(move_frame)
    dir_listbox = tk.Listbox(move_frame, height=15, width=40, yscrollcommand=scrollbar.set)
    dir_listbox.configure(yscrollcommand=scrollbar.set)
    scrollbar.configure(command=dir_listbox.yview)

    for dir_path in directories:
        dir_listbox.insert(tk.END, dir_path)

    dir_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def do_move():
        selection_dir = dir_listbox.curselection()

        if not selection_dir:
            messagebox.showwarning("Move File", "Aukeratu helmuga direktorioa")
            return

        destination = directories[selection_dir[0]]

        if dropbox._path == "/":
            old_path = "/" + file_name
        else:
            old_path = dropbox._path + "/" + file_name

        if old_path == destination + "/" + file_name:
            messagebox.showwarning("Move File", "Jatorria eta helmuga berdinak dira")
            return

        print(f"Fitxategia mugitzen: {old_path} -> {destination}/{file_name}")
        dropbox.move_file(old_path, destination, file_name)
        popup.destroy()
        dropbox.list_folder(msg_listbox2)

    button_frame = tk.Frame(move_frame)
    button_frame.pack(side=tk.BOTTOM, pady=10)

    accept_button = tk.Button(button_frame, text="Mugitu", width=10, pady=5, command=do_move)
    accept_button.pack(side=tk.LEFT, padx=5)

    cancel_button = tk.Button(button_frame, text="Utzi", width=10, pady=5, command=popup.destroy)
    cancel_button.pack(side=tk.LEFT, padx=5)

##########################################################################################################

def check_credentials(event= None):
    egela.check_credentials(username, password)

def on_selecting1(event):
    global selected_items1
    widget = event.widget
    selected_items1 = widget.curselection()
    print (selected_items1)

def on_selecting2(event):
    global selected_items2
    widget = event.widget
    selected_items2 = widget.curselection()
    print (selected_items2)

def on_double_clicking2(event):
    widget = event.widget
    selection = widget.curselection()
    if selection[0] == 0 and dropbox._path != "/":
        head, tail = os.path.split(dropbox._path)
        dropbox._path = head
    else:
        selected_file = dropbox._files[selection[0]]
        if selected_file['.tag'] == 'folder':
            if dropbox._path == "/":
                dropbox._path = dropbox._path + selected_file['name']
            else:
                dropbox._path = dropbox._path + '/' + selected_file['name']
    var.set(dropbox._path)
    dropbox.list_folder(msg_listbox2)
##########################################################################################################
# Login eGela
root = tk.Tk()
root.geometry('250x150')
helper.set_icon(root)
root.title('Login eGela')
helper.center(root)
egela = eGela.eGela(root)

login_frame = tk.Frame(root, padx=10, pady=10)
login_frame.pack(fill=tk.BOTH, expand=True)

username = make_entry(login_frame, "User name:", 16)
password = make_entry(login_frame, "Password:", 16, show="*")
password.bind("<Return>", check_credentials)

button = tk.Button(login_frame, borderwidth=4, text="Login", width=10, pady=8, command=check_credentials)
button.pack(side=tk.BOTTOM)

root.mainloop()

if not egela._login:
    exit()
# Si nos logeamos en eGela cogemos las referencias a los pdfs
pdfs = egela.get_pdf_refs()

##########################################################################################################
# Login Dropbox
root = tk.Tk()
root.geometry('250x100')
helper.set_icon(root)
root.title('Login Dropbox')
helper.center(root)

login_frame = tk.Frame(root, padx=10, pady=10)
login_frame.pack(fill=tk.BOTH, expand=True)
# Login and Authorize in Drobpox
dropbox = Dropbox.Dropbox(root)

label = tk.Label(login_frame, text="Login and Authorize\nin Drobpox")
label.pack(side=tk.TOP)
button = tk.Button(login_frame, borderwidth=4, text="Login", width=10, pady=8, command=dropbox.do_oauth)
button.pack(side=tk.BOTTOM)

root.mainloop()

##########################################################################################################
# eGela -> Dropbox

newroot = tk.Tk()
newroot.geometry("850x400")
helper.set_icon(newroot)
newroot.title("eGela -> Dropbox") #
helper.center(newroot)

newroot.rowconfigure(0, weight=1)
newroot.rowconfigure(1, weight=5)
newroot.columnconfigure(0, weight=6)
newroot.columnconfigure(1, weight=1)
newroot.columnconfigure(2, weight=6)
newroot.columnconfigure(3, weight=1)

# Etigueta PDFs en Sistemas Web (0,0)   #
var2 = tk.StringVar()
var2.set("PDFs en Sistemas Web")
label2 = tk.Label(newroot, textvariable=var2)
label2.grid(column=0, row=0, ipadx=5, ipady=5)

# Etigueta del directorio de Dropbox (0,2)
var = tk.StringVar()
var.set(dropbox._path)
label = tk.Label(newroot, textvariable=var)
label.grid( row=0, column=2, ipadx=5, ipady=5)

# Frame con lista de PDFs e eGela (1,0)
selected_items1 = None
messages_frame1 = tk.Frame(newroot)
msg_listbox1 = make_listbox(messages_frame1)
msg_listbox1.bind('<<ListboxSelect>>', on_selecting1)
msg_listbox1.pack(side=tk.LEFT, fill=tk.BOTH)
#messages_frame1.pack()
messages_frame1.grid(row=1, column=0, ipadx=10, ipady=10, padx=2, pady=2) #

# Frame con boton >>> (1,1)
frame1 = tk.Frame(newroot)
button1 = tk.Button(frame1, borderwidth=4, text=">>>", width=10, pady=8, command=transfer_files)
button1.pack()
frame1.grid(row=1, column=1, ipadx=5, ipady=5)

# Frame con ficheros en Dropbox (1,2)
selected_items2 = None
messages_frame2 = tk.Frame(newroot)
msg_listbox2 = make_listbox(messages_frame2)
msg_listbox2.bind('<<ListboxSelect>>', on_selecting2)
msg_listbox2.bind('<Double-Button-1>', on_double_clicking2)
msg_listbox2.pack(side=tk.RIGHT, fill=tk.BOTH)

#messages_frame2.pack()
messages_frame2.grid(row=1, column=2, ipadx=10, ipady=10, padx=2, pady=2)

# Frame con botones Create y Delete (1,3)

frame2 = tk.Frame(newroot)
button2 = tk.Button(frame2, borderwidth=4,  background="#C6185C",fg="white", text="Delete", width=10, pady=8, command=delete_files)
button2.pack(padx=2, pady=2)
button3 = tk.Button(frame2, borderwidth=4, background="#7C86FF",fg="white", text="Create folder", width=10, pady=8, command=create_folder)
button3.pack(padx=2, pady=2)
button4 = tk.Button(frame2, borderwidth=4, background="#FFA500",fg="white", text="Rename", width=10, pady=8, command=rename_file)
button4.pack(padx=2, pady=2)
button5 = tk.Button(frame2, borderwidth=4, background="#4CAF50",fg="white", text="Move", width=10, pady=8, command=move_file)
button5.pack(padx=2, pady=2)
frame2.grid(row=1, column=3,  ipadx=10, ipady=10)

for each in pdfs:
    msg_listbox1.insert(tk.END, each['pdf_name'])
    msg_listbox1.yview(tk.END)

dropbox.list_folder(msg_listbox2)

newroot.mainloop()