import tkinter as tk
import time
from tkinter import simpledialog
import tkintermapview
import tkinter.ttk as ttk
import concurrent.futures
from camercam import CameraCam

markers = []
marker_names = []
marker_coords = {}

cameras = []

def threads(funcs):
    if funcs:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(test, func): func for func in funcs}

def test(func):
    while True:
        time.sleep(5)
        print(func)

def add_marker_event(root_tk,map_widget, marker_menu, marker_menu_var, coords,executor):
    root_tk.after(1000,add_marker_event_post(root_tk,map_widget, marker_menu, marker_menu_var, coords,executor))


def after(root_tk,func,args):
    root_tk.after(1000,func(args))

def add_marker_event_post(root_tk,map_widget, marker_menu, marker_menu_var, coords,executor):
    marker_name = ask_marker_name()
    if marker_name:
        new_marker = map_widget.set_marker(coords[0], coords[1], text=marker_name)
        markers.append(new_marker)
        marker_names.append(marker_name)
        camera = CameraCam(len(markers)-1)
        cameras.append(camera)
        executor.submit(camera.SetUpCam)
        camera.processing = True
        marker_coords[marker_name] = (coords[0], coords[1])
        update_marker_menu(marker_menu, marker_menu_var)

def ask_marker_name():
    marker_name = simpledialog.askstring("Marker Name", "Enter marker name:")
    return marker_name

def update_map_position(map_widget, latitude_entry, longitude_entry):
    try:
        lat = float(latitude_entry.get())
        lon = float(longitude_entry.get())
        map_widget.set_position(lat, lon)
    except ValueError:
        print("Invalid coordinates. Please enter valid numbers.")

def delete_selected_marker(marker_menu_var, marker_names, markers, map_widget):
    global marker_menu
    selected_marker_name = marker_menu_var.get()
    if selected_marker_name:
        for i, name in enumerate(marker_names):
            if name == selected_marker_name:
                marker_to_delete = markers[i]
                marker_to_delete.delete()
                markers.pop(i)
                marker_names.pop(i)
                camera = cameras[i]
                camera.quit()
                cameras.pop(i)
                update_marker_menu(marker_menu, marker_menu_var)
                break
    else:
        print("No marker selected.")

def update_marker_menu(
        marker_menu, marker_menu_var):
    menu = marker_menu["menu"]
    menu.delete(0, "end")
    for name in marker_names:
        menu.add_command(label=name, command=lambda n=name: marker_menu_var.set(n))

def open_camstatus(root_tk,executor,marker_names, marker_coords, marker_menu_var):
    cam_status_window = tk.Toplevel()
    cam_status_window.title("Camera Status")
    cam_status_window.geometry("800x600")

    notebook = ttk.Notebook(cam_status_window)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def open_camera_tab(root_tk,executor,marker_name):
        camera_tab = ttk.Frame(notebook)
        notebook.add(camera_tab, text=marker_name)

        tk.Label(camera_tab, text=f"Camera: {marker_name}", font=("Helvetica", 14)).pack(pady=20)
        status_label = tk.Label(camera_tab, text="Status: INACTIVE", font=("Helvetica", 12))
        status_label.place( anchor=tk.NW)

        coords_label = tk.Label(camera_tab, text=f"Coordinates: {marker_coords.get(marker_name, '')}", font=("Helvetica", 10))
        coords_label.place( anchor=tk.NW)
        camera = []
        for i, name in enumerate(marker_names):
            if name == marker_name:
                camera = cameras[i]
                break
        tk.Button(camera_tab, text="Turn On", command= executor.submit(camera.Processing)).pack()




        tk.Button(camera_tab, text="Back to Main Menu", command=lambda: notebook.forget(camera_tab)).pack(side=tk.BOTTOM, pady=20)

    marker_label = tk.Label(cam_status_window, text="Select camera:")
    marker_label.pack(pady=10)

    selected_marker_var = tk.StringVar(cam_status_window)
    selected_marker_var.set("")

    marker_menu = tk.OptionMenu(cam_status_window, selected_marker_var, *marker_names)
    marker_menu.pack(pady=10)

    def on_marker_select():
        selected_marker_name = selected_marker_var.get()
        if selected_marker_name:
            open_camera_tab(root_tk,executor,selected_marker_name)

    selected_marker_var.trace("w", lambda *args: on_marker_select())


def createGui(executor):
    root_tk = tk.Tk()
    root_tk.geometry("800x600")
    root_tk.title("RoadSense")

    map_frame = tk.Frame(root_tk)
    map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    map_widget = tkintermapview.TkinterMapView(map_frame, width=600, height=600, corner_radius=0)
    map_widget.pack(fill=tk.BOTH, expand=True)
    map_widget.set_position(45.28575, 27.97103)
    map_widget.set_zoom(15)

    left_frame = tk.Frame(root_tk, width=200, bg="lightpink")
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tk.Label(left_frame, text="RoadSense GUI", font=("Helvetica", 16), bg="lightpink").pack(pady=20)

    tk.Label(left_frame, text="Latitude:", bg="lightpink").pack()
    latitude_entry = tk.Entry(left_frame)
    latitude_entry.pack(pady=5)

    tk.Label(left_frame, text="Longitude:", bg="lightpink").pack()
    longitude_entry = tk.Entry(left_frame)
    longitude_entry.pack(pady=5)

    update_button = tk.Button(left_frame, text="Update Map", command=lambda: update_map_position(map_widget, latitude_entry, longitude_entry))
    update_button.pack(pady=10)

    tk.Button(left_frame, text="Add Marker", command=lambda: add_marker_event(root_tk,map_widget, marker_menu, marker_menu_var, map_widget.get_position(),executor)).pack(pady=10)

    tk.Button(left_frame, text="CAM Status", command=lambda: open_camstatus(root_tk,executor,marker_names, marker_coords, marker_menu_var)).pack(pady=10)

    entry_label = tk.Label(left_frame, text="Enter Value:", bg="lightpink")
    entry_label.pack(pady=10)

    selected_value = tk.StringVar(value="50")
    entry = tk.Entry(left_frame, textvariable=selected_value)
    entry.pack(pady=10)

    marker_menu_var = tk.StringVar(left_frame)
    marker_menu_var.set("")

    marker_menu_label = tk.Label(left_frame, text="Select camera:", bg="lightpink")
    marker_menu_label.pack(pady=5)

    marker_menu = tk.OptionMenu(left_frame, marker_menu_var, "")
    marker_menu.pack(pady=5)

    tk.Button(left_frame, text="Delete Marker", command=lambda: delete_selected_marker(marker_menu_var, marker_names, markers, map_widget)).pack(pady=10)

    map_widget.add_right_click_menu_command(label="Add Marker", command=lambda coords: add_marker_event(root_tk,map_widget, marker_menu, marker_menu_var, coords,executor), pass_coords=True)

    update_marker_menu(marker_menu, marker_menu_var)

    root_tk.mainloop()

