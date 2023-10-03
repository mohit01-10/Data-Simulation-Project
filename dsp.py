from tkinter import font
import simpy
import numpy as np
import tkinter as tk
import math
import io
from PIL import Image, ImageTk
import time
import plotly.graph_objs as go
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

rocket_mass = 1000.0  
thrust_force = 50000.0  
drag_coefficient = 0.5
gravity = 9.81  
time_step = 1
rocket_velocity = 0
abort_flag = True

env = simpy.rt.RealtimeEnvironment(factor=1.0, strict= False)
alt = [0]
tim = [0]

def rocket(env, speed_var, altitude_var, gauge_canvas, graph_canvas):
    global rocket_mass, thrust_force, drag_coefficient, gravity, time_step, rocket_velocity
    global alt, tim, abort_flag, c

    c = 12
    time = 0
    altitude = 0
    velocity = 0
    acceleration = 0

    while True:
        if not abort_flag and c != 0:
            Time_var.set(f"T - {c:.1f}\n seconds")
            c = c - 1
            yield env.timeout(time_step)
        else:
            break

    while True:
        if not abort_flag:
            drag_force = drag_coefficient * velocity**2
            net_force = thrust_force - drag_force - rocket_mass * gravity

            acceleration = net_force / rocket_mass
            velocity += acceleration * time_step
            altitude += velocity * time_step
            time += time_step

            speed_var.set(f"{velocity:.1f} m/s")
            altitude_var.set(f"{altitude:.1f}\n meters")
            Time_var.set(f"T + {time:.1f}\n seconds")
            rocket_velocity = velocity
            alt.append(altitude) 
            tim.append(time)

            update_gauge(gauge_canvas, velocity)
            update_graph(graph_canvas, tim, alt)

            print(f"Time: {time:.1f}s, Altitude: {altitude:.1f}m, Velocity: {velocity:.1f}m/s, Acceleration: {acceleration:.1f}m/s^2")

            yield env.timeout(time_step)

def update_graph(canvas, tim, alt):
    fig, ax = plt.subplots(figsize=(5, 4), dpi=75)
    line, = ax.plot(tim, alt, lw=2)
    ax.set_xlabel('Time (sec)')
    ax.set_ylabel('Altitude (meter)')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1700)
    canvas.delete("all")
    canvas.create_window(200, 153, window=FigureCanvasTkAgg(fig, master=canvas).get_tk_widget())

def update_gauge(canvas, velocity):
    global gauge_photo

    fig = go.Figure(go.Indicator(
        domain = {'x': [0.2, 0.8], 'y': [0.2, 0.8]},
        value = velocity,
        mode = "gauge+number",
        gauge = {
            'axis': {'range': [0, 300], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "black"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "black",
            'steps': [
                {'range': [0, 50], 'color': '#00ff00'},
                {'range': [50, 100], 'color': '#55ff00'},  
                {'range': [100, 125], 'color': '#aaff00'}, 
                {'range': [125, 150], 'color': '#ffff00'}, 
                {'range': [150, 175], 'color': '#ffa500'}, 
                {'range': [175, 200], 'color': '#ff7f00'},  
                {'range': [200, 225], 'color': '#ff0000'},  
                {'range': [225, 250], 'color': '#aa0000'},  
                {'range': [250, 300], 'color': '#550000'} 
            ]
        }
    ))

    image_bytes = fig.to_image(format='png')
    image_data = io.BytesIO(image_bytes)
    image = Image.open(image_data)
    gauge_photo = ImageTk.PhotoImage(image)

    canvas.delete("all")
    canvas.create_image(200, 160, image=gauge_photo, anchor='center')

def animate_gauge(canvas):
    global rocket_velocity
    for velocity in range(round(rocket_velocity)+1): 
        update_gauge(canvas, velocity)
        canvas.update()  
        time.sleep(0.0001) 
    update_gauge(canvas_1, rocket_velocity)
    canvas.update() 

window = tk.Tk()
window.title("Rocket Flight Simulation")
window.geometry("1000x1000")
window.configure(bg='black')

speed_frame = tk.LabelFrame(window, text="Speedometer", font=("Arial", 20), bg="black", fg="white")
speed_frame.place(x=40, y=100)

canvas_1 = tk.Canvas(speed_frame, width=400, height=300)
canvas_1.pack()

speed_label = tk.Label(speed_frame, text="Velocity : ", font=("Arial", 20))
speed_label.place(x=10, y=20)

speed_var = tk.StringVar()
speed_var.set("0.0 m/s")

speed_value_label = tk.Label(speed_frame, textvariable=speed_var, font=("Arial", 20))
speed_value_label.place(x=150, y=20)

update_gauge(canvas_1, 0)

altitude_frame = tk.LabelFrame(window, text="Altitude", font=("Arial", 20), bg="black", fg="white")
altitude_frame.place(x=500, y=100)

canvas_2 = tk.Canvas(altitude_frame, width=400, height=300)
canvas_2.pack()

altitude_label = tk.Label(altitude_frame, text="Altitude: ", font=("Arial", 20))
altitude_label.place(x=10, y=20)

altitude_var = tk.StringVar()
altitude_var.set("0.0\n meters")

altitude_value_label = tk.Label(altitude_frame, textvariable=altitude_var, font=("Arial", 50))
altitude_value_label.place(x=80, y=100)

Time_frame = tk.LabelFrame(window, text="Time", font=("Arial", 20), bg="black", fg="white")
Time_frame.place(x=40, y=500)

canvas_3 = tk.Canvas(Time_frame, width=400, height=300)
canvas_3.pack()

Time_label = tk.Label(Time_frame, text="Time: ", font=("Arial", 20))
Time_label.place(x=10, y=20)

Time_var = tk.StringVar()
Time_var.set("0.0\n seconds")

Time_value_label = tk.Label(Time_frame, textvariable=Time_var, font=("Arial", 50))
Time_value_label.place(x=70, y=80)

Trajectory_frame = tk.LabelFrame(window, text="Trajectory", font=("Arial", 20), bg="black", fg="white")
Trajectory_frame.place(x=500, y=500)

canvas_4 = tk.Canvas(Trajectory_frame, width=400, height=300)
canvas_4.pack()

update_graph(canvas_4, tim, alt)
animate_gauge(canvas_1)

def run1():
    global abort_flag
    abort_flag = False
    env.process(rocket(env, speed_var, altitude_var, canvas_1, canvas_4))
    env.run(until=40)

def run_env():
    env_thread = threading.Thread(target=run1)
    env_thread.start()

def stop_env():
    global abort_flag
    abort_flag = True

button_font = font.Font(family='Helvetica', size=18)
bt = tk.Button(window, text="Launch", command=run_env, width=10, height=2, font=button_font)
bt.place(x=300, y=30)

bt2 = tk.Button(window, text="Abort", command=stop_env, width=10, height=2, font=button_font)
bt2.place(x=600, y=30)

lc = tk.Label(window, text="LAUNCH CONTROLS", font=("Arial", 20))
lc.place(x=370, y=880)

window.mainloop()
