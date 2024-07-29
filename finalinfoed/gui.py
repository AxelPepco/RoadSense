import tkinter as tk
from tkinter import PhotoImage
import time
from tkinter import simpledialog
import tkintermapview
import tkinter.ttk as ttk
import concurrent.futures
from camercam import CameraCam
import json
import os
from intersection import Intersection

signimg = None

markers = []
marker_names = []
marker_coords = {}
cameras = []
save_roadpoints = []
save_directions = []
intersections = []
inter_markers = []
comPorts = []

#Initializeaza camerele si intersectiile din data incarcata anterior
def restorevars(map_widget, marker_menu, marker_menu_var, executor):
    cnt = 0
    for marker_name in marker_names:
        coords = marker_coords[marker_name]
        new_marker = map_widget.set_marker(coords[0], coords[1], text=marker_name)
        markers.append(new_marker)
        
        camera = CameraCam(len(markers) - 1)
        camera.port = comPorts[len(markers) -1]
        cameras.append(camera)
        if cnt < len(save_roadpoints):
            camera.roadPoints = save_roadpoints[cnt]
        if cnt < len(save_directions):
            camera.directions = save_directions[cnt]
        camera.processing = True
        cnt += 1

    for intersection in intersections:
        if not any(m.text == intersection.name for m in inter_markers):
            new_intersection_marker = map_widget.set_marker(intersection.coords[0], intersection.coords[1], text=intersection.name, icon=signimg)
            inter_markers.append(new_intersection_marker)

    update_marker_menu(marker_menu, marker_menu_var)


#Incarca data salvata in ultima rulare a programului(Camere, Intersectii, Port-uri, Orientarea Benzilor)
def loadvars():
    file_path = r'finalinfoed\file.json'
    print("Loading data from file...")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r') as file:
            data = json.load(file)
            global marker_names, marker_coords, save_roadpoints, save_directions, intersections,comPorts
            marker_names, marker_coords, save_roadpoints, save_directions = data[:4]
            intersections.clear()  # Clear the intersections list before loading
            intersections = [
                Intersection(inter['name'], inter['coords'], inter.get('cams', []), inter.get('orientations', [])) for inter in data[4]
            ]
            comPorts = data[5]
            print("Data loaded successfully.")
            return data
    print("No data found in file.")
    return []

#Pentru crearea unei camere/intersectii, afiseaza un meniu la apasarea click dreapta pe harta
def right_click_event(root_tk, map_widget, marker_menu, marker_menu_var, coords, executor):
    popup = tk.Toplevel(root_tk)
    popup.title("Create New")
    label = tk.Label(popup, text="Select what you want to add").pack()
    var = tk.StringVar(popup)
    options = ["Camera", "Intersection"]
    option_menu = tk.OptionMenu(popup, var, *options)
    option_menu.pack()
    def select():
        if var.get() == "Camera":
            add_marker_event(root_tk, map_widget, marker_menu, marker_menu_var, coords, executor)
            save(False,"None","None")
            popup.destroy()
        elif var.get() == "Intersection":
            add_intersection(root_tk, coords,map_widget)
            save(False,"None","None")
            popup.destroy()

    button = tk.Button(popup, text="Continue", command=select)
    button.pack()


#Adauga o intersectie creata si o afiseaza
def add_intersection(root_tk, coords,map_widget):


    popup = tk.Toplevel(root_tk)
    label = tk.Label(popup, text="Enter Name").pack()
    popup.title("Create Intersection")

    entry = tk.Entry(popup)
    entry.pack()

    def add_int():
        inter = Intersection(entry.get(), coords)
        intersections.append(inter)
        mrkr = map_widget.set_marker(coords[0], coords[1],text = entry.get(),icon = signimg)
        inter_markers.append(mrkr)

        popup.destroy()

    button = tk.Button(popup, text="Continue", command=add_int)
    button.pack()

#Delay pentru programarea in siguranta actualizarea interfetei grafice in thread-ul principal 
def add_marker_event(root_tk, map_widget, marker_menu, marker_menu_var, coords, executor):
    root_tk.after(1000, add_marker_event_post, root_tk, map_widget, marker_menu, marker_menu_var, coords, executor)


#Salveaza toate datele utile in fisierul file.json
def save(ok,rd, dir):
    if ok:
        save_roadpoints.append(rd)
        save_directions.append(dir)
    savearrs = (marker_names, marker_coords, save_roadpoints, save_directions, [inter.__dict__ for inter in intersections],comPorts)
    with open(r"finalinfoed\file.json", "w") as file:
        json.dump(savearrs, file, default=lambda o: o.__dict__)

#Adauga un marker nou pe harta si configureaza o instanta a clasei CameraCam si ruleaza setup-ul benzilor (functia Camera.SetUpCam) in alt thread 
def add_marker_event_post(root_tk, map_widget, marker_menu, marker_menu_var, coords, executor):
    marker_name = ask_marker_name()
    comPort = simpledialog.askstring("COM Port", "Enter COM Port:")
    if marker_name:
        new_marker = map_widget.set_marker(coords[0], coords[1], text=marker_name)
        markers.append(new_marker)
        marker_names.append(marker_name)
        camera = CameraCam(len(markers)-1)
        camera.port = comPort
        comPorts.append(comPort)
        cameras.append(camera)
        future = executor.submit(camera.SetUpCam, save)
        future.add_done_callback(handle_thread_exception)
        camera.processing = True

        marker_coords[marker_name] = (coords[0], coords[1])
        update_marker_menu(marker_menu, marker_menu_var)

#Delay pentru programarea in siguranta actualizarea interfetei grafice in thread-ul principal 

def handle_thread_exception(future):
    exception = future.exception()
    if exception:
        print(f"Thread raised an exception: {exception}")

#Meniu simplu pentru introducerea numelui marker-ului
def ask_marker_name():
    marker_name = simpledialog.askstring("Marker Name", "Enter marker name:")
    return marker_name

#Schimba zona afisata pe harta in functie de coordonatele introduse
def update_map_position(map_widget, latitude_entry, longitude_entry):
    try:
        lat = float(latitude_entry.get())
        lon = float(longitude_entry.get())
        map_widget.set_position(lat, lon)
    except ValueError:
        print("Invalid coordinates. Please enter valid numbers.")

#Sterge o camera din memorie
def delete_selected_marker(marker_menu_var, marker_names, markers, map_widget, marker_menu):
    selected_marker_name = marker_menu_var.get()
    if selected_marker_name:
        for i, name in enumerate(marker_names):
            if name == selected_marker_name:
                print(f"Deleting marker at index {i}")
                marker_to_delete = markers[i]
                marker_to_delete.delete()
                markers.pop(i)
                marker_names.pop(i)
                camera = cameras[i]
                camera.quit()
                cameras.pop(i)
                save_roadpoints.pop(i)
                save_directions.pop(i)
                update_marker_menu(marker_menu, marker_menu_var)
                break
    else:
        print("No marker selected.")


def update_marker_menu(marker_menu, marker_menu_var):
    menu = marker_menu["menu"]
    menu.delete(0, "end")
    for name in marker_names:
        menu.add_command(label=name, command=lambda n=name: marker_menu_var.set(n))

#Afiseaza numarul de masini pe fiecare banda pe pagina de detalii a camerei
def update_label(label, camera):
    bands = camera.cars
    text = camera.color + "\n"
    for i in range(len(bands)):
        text += f"Banda {i}: {bands[i]} vehicule\n"
    
    label.config(text=text)
    label.after(1000, update_label, label, camera)

#Adauga camera in intersectia selectata
def addCam(cam,inter, orientation):
        intersection_names = [inter.name for inter in intersections]
        temp = intersection_names.index(inter)
        inter = intersections[temp]
        temp = marker_names.index(cam)
        camera = cameras[temp]

        inter.add_cam(cam,orientation)


        save(False,None,None)
        
#Porneste toate camerele care apartin intersectiei si porneste algoritmul Fuzzy
def startInter(cami,inter,executor):

        intersection_names = [inter.name for inter in intersections]
        temp = intersection_names.index(inter)
        inter = intersections[temp]
        usedCams = []
        for cam in inter.cams:
            temp = marker_names.index(cam)
            camera = cameras[temp]
            camera.processing = False
            if camera.processing == False:
                camera.start_processing()
                future = executor.submit(camera.Processing)
                future.add_done_callback(handle_thread_exception)
            usedCams.append(camera)
        inter.loadCameraObjs(usedCams)
        inter.start_managing()
        future2 = executor.submit(inter.ManagingProcess)
        future2.add_done_callback(handle_thread_exception)

#Opreste detectia in gestionarea in intersectie
def stopInter(cam,inter):
        intersection_names = [inter.name for inter in intersections]
        temp = intersection_names.index(inter)
        inter = intersections[temp]
        usedCams = []
        for cam in inter.cams:
            temp = marker_names.index(cam)
            camera = cameras[temp]
            camera.stop_processing()
        inter.stop_managing()


#Meniul pentru gestionarea intersectiei
def open_intersections(root_tk,executor):
    def update_RightSide():
        intersection_names = [inter.name for inter in intersections]
        selected_intersection_name = sel_inter.get()
        if selected_intersection_name != "None":
            selected_intersection = next((inter for inter in intersections if inter.name == selected_intersection_name), None)
            if selected_intersection:
                cam_info = [f"{cam} (Orientation: {orientation})" for cam, orientation in zip(selected_intersection.cams, selected_intersection.orientations)]
                camera_list_label.config(text="\n".join(cam_info))

    popup = tk.Toplevel(root_tk)
    popup.title("Manage Intersections")
    left_frame = tk.Frame(popup, bg="lightgrey", width=600, height=6700)
    right_frame = tk.Frame(popup, bg="white", width=700, height=700)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    tk.Label(left_frame, text="Gestionează intersecțiile", font=("Helvetica", 18), bg="lightgrey").pack()
    tk.Label(left_frame, text="Selectează intersecția:",  font=("Helvetica", 15), bg="lightgrey").pack(pady=13)
    sel_inter = tk.StringVar()
    sel_inter.set("Niciuna")
    intersection_names = [inter.name for inter in intersections]
    op_menu = tk.OptionMenu(left_frame, sel_inter,"", *intersection_names)
    op_menu.pack()

    tk.Button(left_frame, text="Update", command=update_RightSide).pack(pady=10)
    strcam = tk.StringVar()
    cam_op= tk.OptionMenu(left_frame,strcam, "Select", *marker_names)
    cam_op.pack()
    stror = tk.StringVar()
    oroptions = ["North", "South" ,"East", "West"]
    orient_op = tk.OptionMenu(left_frame,stror, *oroptions)
    orient_op.pack(pady=10)
    buttonAdd = tk.Button(left_frame,text = "Adaugă", command=lambda: addCam(strcam.get(), sel_inter.get(),stror.get()))
    buttonAdd.pack(pady=10)
    buttonOn = tk.Button(left_frame, text = "Pornește", command=lambda:startInter(strcam.get(),sel_inter.get(),executor))
    buttonOn.pack(pady=10)
    buttonOff = tk.Button(left_frame, text = "Oprește", command=lambda:stopInter(strcam.get(),sel_inter.get()))
    buttonOff.pack(pady=10)


    tk.Label(right_frame, text="Camere în intersecție", font=("Helvetica", 18), bg="white").pack()
    camera_list_label = tk.Label(right_frame, text="", bg="white",  font=("Helvetica", 12))
    camera_list_label.pack()

    update_RightSide()

#Meniul de gestionare a camerei
def open_camstatus(root_tk, executor, marker_names, marker_coords, marker_menu_var):
    cam_status_window = tk.Toplevel()
    cam_status_window.title("Camera Status")
    cam_status_window.geometry("800x600")

    notebook = ttk.Notebook(cam_status_window)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def open_camera_tab(marker_name):
        camera_tab = ttk.Frame(notebook)
        notebook.add(camera_tab, text=marker_name)

        tk.Label(camera_tab, text=f"Camera: {marker_name}", font=("Helvetica", 14)).pack(anchor=tk.NW)
        status_label = tk.Label(camera_tab, text="Status: ACTIVE", font=("Helvetica", 12))
        status_label.pack(anchor=tk.NW)
        camera = cameras[marker_names.index(marker_name)]
        coords_label = tk.Label(camera_tab, text=f"Coordinates: {marker_coords.get(marker_name, '')}", font=("Helvetica", 10))
        coords_label.pack(anchor=tk.NW)
        carsLabel = tk.Label(camera_tab, text="Not Started", font=("Helvetica", 10))
        carsLabel.pack(anchor=tk.NW)
        update_label(carsLabel, camera)
        camera = None
        for i, name in enumerate(marker_names):
            if name == marker_name:
                camera = cameras[i]
                break

        def turn_on_camera():
            camera.start_processing()
            if camera:
                future = executor.submit(camera.Processing)
                future.add_done_callback(handle_thread_exception)
                status_label.config(text="Status: ACTIVE")

        def turn_off_camera():
            camera.stop_processing()

        tk.Button(camera_tab, text="Turn On", command=turn_on_camera).pack()
        tk.Button(camera_tab, text="Turn Off", command=turn_off_camera).pack()
        tk.Button(camera_tab, text="Back to Main Menu", command=lambda: notebook.forget(camera_tab)).pack(side=tk.BOTTOM, pady=20)

    marker_label = tk.Label(cam_status_window, text="Select camera:")
    marker_label.pack(pady=10)

    selected_marker_var = tk.StringVar(cam_status_window)
    selected_marker_var.set("")

    marker_menu = tk.OptionMenu(cam_status_window, selected_marker_var, *marker_names)
    marker_menu.pack(pady=10)

    def on_marker_select(*args):
        selected_marker_name = selected_marker_var.get()
        if selected_marker_name:
            open_camera_tab(selected_marker_name)

    selected_marker_var.trace("w", on_marker_select)

#Initiaza fereastra principala de GUI si incarca variabilele
def create_gui(executor):
    print("Creating GUI...")
    varsarr = loadvars()
    print("Vars loaded:", varsarr)
    if len(varsarr) > 0:
        global intersections,marker_names, marker_coords, save_roadpoints, save_directions,intersections,comPorts
        marker_names, marker_coords, save_roadpoints, save_directions,intersectionsTemp,comPorts = varsarr
        for inter in intersectionsTemp:
            print(inter)
            intersections.append(Intersection(inter["name"], inter["coords"], inter.get("cams", []), inter.get("orientations", [])))
    root_tk = tk.Tk()
    print("Tk instance created.")
    root_tk.geometry("800x600")
    root_tk.title("RoadSense")
    global signimg
    
    signimg = PhotoImage(file=r"finalinfoed\sign.png")
    map_frame = tk.Frame(root_tk)
    map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    map_widget = tkintermapview.TkinterMapView(map_frame, width=600, height=600, corner_radius=0)
    map_widget.pack(fill=tk.BOTH, expand=True)
    map_widget.set_position(45.28575, 27.97103)
    map_widget.set_zoom(15)

    left_frame = tk.Frame(root_tk, width=200, bg="black")
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tk.Label(left_frame, text="RoadSense GUI", font=("Helvetica", 16), bg="black", fg="white").pack(pady=20)

    tk.Label(left_frame, text="Latitude:", bg="black", fg="white").pack()
    latitude_entry = tk.Entry(left_frame)
    latitude_entry.pack(pady=5)

    tk.Label(left_frame, text="Longitude:", bg="black", fg="white").pack()
    longitude_entry = tk.Entry(left_frame)
    longitude_entry.pack(pady=5)

    update_button = tk.Button(left_frame, text="Update Map", command=lambda: update_map_position(map_widget, latitude_entry, longitude_entry))
    update_button.pack(pady=10)

    tk.Button(left_frame, text="Add Marker", command=lambda: add_marker_event(root_tk, map_widget, marker_menu, marker_menu_var, map_widget.get_position(), executor)).pack(pady=10)
    tk.Button(left_frame, text="CAM Status", command=lambda: open_camstatus(root_tk, executor, marker_names, marker_coords, marker_menu_var)).pack(pady=10)

    tk.Button(left_frame, text="Intersections", command=lambda: open_intersections(root_tk,executor)).pack(pady=10)

    entry_label = tk.Label(left_frame, text="Enter Value:", bg="black", fg="white")
    entry_label.pack(pady=10)

    selected_value = tk.StringVar(value="50")
    entry = tk.Entry(left_frame, textvariable=selected_value)
    entry.pack(pady=10)

    marker_menu_var = tk.StringVar(left_frame)
    marker_menu_var.set("")

    marker_menu_label = tk.Label(left_frame, text="Select camera:", bg="black", fg="white")
    marker_menu_label.pack(pady=5)

    marker_menu = tk.OptionMenu(left_frame, marker_menu_var, "")
    marker_menu.pack(pady=5)

    tk.Button(left_frame, text="Delete Marker", command=lambda: delete_selected_marker(marker_menu_var, marker_names, markers, map_widget, marker_menu)).pack(pady=10)

    map_widget.add_right_click_menu_command(label="Add Marker", command=lambda coords: right_click_event(root_tk, map_widget, marker_menu, marker_menu_var, coords, executor), pass_coords=True)
    restorevars(map_widget, marker_menu, marker_menu_var, executor)
    root_tk.mainloop()

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor() as executor:
        create_gui(executor)
