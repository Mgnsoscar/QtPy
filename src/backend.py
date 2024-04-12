from __future__ import annotations
from typing import Literal, Dict, Union, Optional, List
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import QTimer, QPointF
from frontend import Frontend
from time import perf_counter
import random
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from database import DatabaseHandler, GameModel, UserModel
import json
from time import sleep
from serial_fetcher import SerialDevice
import math
import pandas as pd
import openpyxl

import sys


class Backend:
    
    def __init__(self) -> None:
        
        self.current_user: UserModel = None
        
        self.serial_reader = SerialDevice(
            baudrate = 2000000,
            timeout = 0.01
        )
        
        # Create a database query handler
        self.database_handler = DatabaseHandler("elsys_prosjekt_db")
        
        # Create reference to the frontend GUI
        self.frontend = Frontend(self)
        
        # Create some references to objects in the frontend
        self.plane = self.frontend.plane
        self.target_box = self.frontend.target_box
        self.left_target_box = self.frontend.left_target_box
        self.left_indicator = self.frontend.left_indicator
        self.right_target_box = self.frontend.right_target_box
        self.right_indicator = self.frontend.right_indicator  
        self.text = self.frontend.page_2.center_frame.text

        # Initialize some variables
        self.max_sensor_in = 4000
        self.calibration_constant = 0.023
        self.angle_scaling = 60
        self.start_timestamp = None
        
        self.reset_game()
        
        # Initialize the different timers/threads
        self.init_timers()

    def write_read(self, write_value: str = None):

            data = self.serial_reader.readline()
            self.serial_reader.reset_input_buffer()
            data = data.decode().strip("\r\n").split(",")
            return data
            
    def init_timers(self) -> None:
        
        self.game_timer = QTimer(self.frontend)
        self.game_timer.timeout.connect(self.start_game)
        
        self.sensor_reader = QTimer(self.frontend)
        self.sensor_reader.timeout.connect(self.read_sensors)
        
    def start_game(self) -> None:  
        
        duration = self.checkmarks["game_duration"] 
        
        self.set_new_targets()
        self.checkmarks["game_duration"] += 1
        
        if duration == 10:
            self.start_timestamp = perf_counter()
        
        if duration < 10:
            self.text.set_text(f"Game starting in {10 - duration}")
        elif duration < 20:
            self.text.move(0, 1, 0, 1000)
            self.text.set_text(f"Targets moving in {20 - duration}")
        elif duration < 30:
            self.text.set_text(f"Targets moving in {30 - duration}")
        elif duration < 45:
            self.text.set_text(f"Targets moving in {45 - duration}")
        elif duration < 60:
            self.text.set_text(f"Targets moving in {60 - duration}")
        else:
            self.text.set_text(f"Game finished in {75 - duration}")
        

        
        self.sensor_reader.start(100)
        
        
        
        if duration == 75:
            self.game_timer.stop()
            self.sensor_reader.stop()
            self.checkmarks["game_duration"] = 0  
                       
            left_force = (
                np.array(self.checkmarks["left_forces"])
                * self.max_sensor_in 
                * self.calibration_constant
            )
            right_force = (
                np.array(self.checkmarks["right_forces"])
                * self.max_sensor_in 
                * self.calibration_constant
            )
            left_force_target = (
                np.array(self.checkmarks["left_force_targets"])
                * self.max_sensor_in 
                * self.calibration_constant
            )
            right_force_target = (
                np.array(self.checkmarks["right_force_targets"])
                * self.max_sensor_in 
                * self.calibration_constant
            )
            time_axis = (
                np.array(self.checkmarks["time_axis"])
                * self.max_sensor_in 
                * self.calibration_constant
            )
            
            data = self.get_stability_and_accuracy(
                left_force, left_force_target, right_force, right_force_target
            )
            
            self.database_handler.add_game_to_user(
                user_id = self.current_user.id,
                game = {
                    "time_axis":time_axis,
                    "left_force":left_force,
                    "right_force":right_force,
                    "left_force_target":left_force_target,
                    "right_force_target":right_force_target,
                    "left_error":data["accuracy"]["left"],
                    "left_instability":data["stability"]["left"],
                    "right_error":data["accuracy"]["right"],
                    "right_instability":data["stability"]["right"]
                }
            )
            self.reset_game()
            self.frontend.main_stack.setCurrentIndex(0)
            self.frontend.page_1.user_list.search_input.setText("")
            self.frontend.page_1.user_list.search_user()
            
            
            
   
    def reset_game(self) -> None:
        self.checkmarks = {
            "game_duration" : 0,
            "target_realignments" : 0,
            "left_forces" : [],
            "right_forces" : [],
            "time_axis" : [],
            "right_force_targets" : [],
            "left_force_targets": [] 
        }
        
        self.force = {
            "left" : 0.,
            "right" : 0.
        }
        self.target_box.reset_position()
        self.left_target_box.reset_position()
        self.left_indicator.reset_position()
        self.right_target_box.reset_position()
        self.right_indicator.reset_position()
        self.plane.reset_position()
        self.start_timestamp = None
       
    def get_stability_and_accuracy(self, 
        left_force: np.ndarray, 
        left_force_target: np.ndarray,
        right_force: np.ndarray,
        right_force_target: np.ndarray
    ) -> dict:

        left = [left_force[0]]
        left_target = [left_force_target[0]]
        
        right = [right_force[0]]
        right_target = [right_force_target[0]]
        
        stab_right = {1 : [right_force[0]]}
        stab_left = {1: [left_force[0]]}
        nr = 1
        
        prev = False
        
        for i in range(1, len(left_force_target)):
            
            if (
                (left_force_target[i] == left_force_target[i-1]) and
                (right_force_target[i] == right_force_target[i-1])
            ):
                
                left.append(left_force[i])
                left_target.append(left_force_target[i])
                
                right.append(right_force[i])
                right_target.append(right_force_target[i])
                
                stab_right[nr].append(right_force[i])
                stab_left[nr].append(left_force[i])
                
                prev = True
            
            else:
                
                if prev:
                    nr += 1
                    stab_left[nr] = []
                    stab_right[nr] = []
                    prev = False

        left_std = []
        right_std = []
        for key in stab_left.keys():
            left_std.append(np.std(stab_left[key]))
            right_std.append(np.std(stab_right[key]))
        
        left_stability = np.mean(left_std)
        right_stability = np.mean(right_std)
        total_stability = np.mean(np.array([left_stability, right_stability]))
        
           
        left = np.array(left)
        left_target = np.array(left_target)
        right = np.array(right)
        right_target = np.array(right_target)
        
        squared_error_left = np.square(left - left_target)
        mse_left = np.mean(squared_error_left)
        squared_error_right = np.square(right - right_target)
        mse_right = np.mean(squared_error_right)
        
        mse_tot = np.mean(np.array([squared_error_left, squared_error_right]))

        
        data = {
            "accuracy" : {
                "left" : mse_left,
                "right" : mse_right,
                "total" : mse_tot
            },
            "stability" : {
                "left" : left_stability,
                "right" : right_stability,
                "total" : total_stability
            }
        }           
        
        return data 
    
    def plot_progress(self, user: UserModel) -> None:
        
        left_mse = []
        right_mse = []
        left_stab = []
        right_stab = []
        
        game_nr = []
        
        for game in user.games:
            
            left_mse.append(game.left_error)
            right_mse.append(game.right_error)
            left_stab.append(game.left_instability)
            right_stab.append(game.right_instability)
            
            game_nr.append(len(game_nr) + 1)
        
        self.plot_prog(
            xVals1=game_nr,
            xVals2=game_nr,
            yVals1={
                "Left Hand Error (MSE)":left_mse,
                "Left Hand Instability ($\\sigma$)":left_stab
            },
            yVals2={
                "Right Hand Error (MSE)":right_mse,
                "Right Hand Instability ($\\sigma$)":right_stab
            },
            title=f"Error and instability progression for user: {user.name}",
            xLabel="Game nr.",
            yLabel="Error (MSE)"
        )
        
        plt.show()
        
    def plot_game(self, game: GameModel) -> None:
        
        time_axis = json.loads(game.time_axis)
        left_force = json.loads(game.left_force)
        left_force_target = json.loads(game.left_force_target)
        right_force = json.loads(game.right_force)
        right_force_target = json.loads(game.right_force_target)        
                
        self.plot(
                xVals1 = time_axis,
                xVals2 = time_axis,
                yVals1 = {
                    "Left hand force":left_force, 
                    "Left hand force target":left_force_target,
                },
                yVals2 = {
                    "Right hand force":right_force,
                    "Right hand force target":right_force_target 
                },
                title = "Applied Force vs. Target Force",
                xLabel = "Game duration [s]",
                yLabel = "Force [g]"
            )
        plt.show(block=False)

    def set_new_targets(self) -> None:
        
        game_duration = self.checkmarks["game_duration"]
        
        # Fetch random left an right target forces
        target_right = random.uniform(-0.75, 0.75)
        target_left = random.uniform(-0.75, 0.75)
        
        height = (target_left + target_right)/2
        
        first_target_rotation = target_left * self.angle_scaling
        target_rotation = (target_left - height) * self.angle_scaling
        
        if game_duration  == 20 or game_duration == 30:
            self.target_box.move(
                x_pos = 0,
                y_pos = 0,
                rotation_angle = first_target_rotation,
                duration = 2000
            )
            self.left_target_box.move(
                x_pos = 0,
                y_pos = target_left,
                rotation_angle = 0,
                duration = 2000
            )
            self.right_target_box.move(
                x_pos = 0,
                y_pos = -target_left,
                rotation_angle = 0,
                duration = 2000
            )
        elif game_duration == 45 or game_duration == 60:
            self.target_box.move(
                x_pos = 0,
                y_pos = height,
                rotation_angle = target_rotation,
                duration = 2000
            )
            self.left_target_box.move(
                x_pos = 0,
                y_pos = target_left,
                rotation_angle = 0,
                duration = 2000
            )
            self.right_target_box.move(
                x_pos = 0,
                y_pos = target_right,
                rotation_angle = 0,
                duration = 2000
            )

    def read_sensors(self) -> None:
        
            if self.serial_reader.portConnected():
                data = self.write_read()

                if len(data) == 2:
                    left = float(data[0])
                    right = float(data[1])
                    
                    print(f"Left: {left}\tRight: {right}")
                    
                    if left > self.max_sensor_in: 
                        left = self.max_sensor_in
                    elif left < -self.max_sensor_in:
                        left = -self.max_sensor_in
                    
                    if right > self.max_sensor_in: 
                        right = self.max_sensor_in
                    elif right < -self.max_sensor_in:
                        right = -self.max_sensor_in
                    
                    
                    self.force["left"] = left
                    self.force["right"] = right
                     
            if self.start_timestamp is None:
                return
            
            if self.checkmarks["game_duration"] >= 10:
            
                self.checkmarks["left_forces"].append(
                    self.force["left"]/self.max_sensor_in
                )
                self.checkmarks["right_forces"].append(
                    self.force["right"]/self.max_sensor_in
                )
                self.checkmarks["left_force_targets"].append(
                    self.left_target_box.get_position_in_parent_as_float().y()/1.6
                )
                self.checkmarks["right_force_targets"].append(
                    self.right_target_box.get_position_in_parent_as_float().y()/1.6
                )
                self.checkmarks["time_axis"].append(
                    ( perf_counter() - self.start_timestamp ) / 100
                )
            
            left_force = (self.force["left"]/self.max_sensor_in)
            right_force = (self.force["right"]/self.max_sensor_in)
            
            height = (left_force + right_force) / 2
            rotation = (left_force - height) * self.angle_scaling
            
            self.frontend.move_plane(
                0, 
                height, 
                rotation, 
                200
            )
            self.frontend.left_indicator.move(
                0, left_force, 0, 200
            )
            self.frontend.right_indicator.move(
                0, right_force, 0, 200
            )
            
            self.frontend.page_2.left_force.display_text = (
                f"{round(left_force*self.calibration_constant*self.max_sensor_in, 2) }\tg"
            )
            self.frontend.page_2.right_force.display_text = (
                f"{round(right_force*self.calibration_constant*self.max_sensor_in, 2)}\tg"
            )
            self.frontend.page_2.update()
        
        
    def show(self) -> None:
        self.frontend.show()

    def plot(self, xVals1, xVals2, yVals1: dict, yVals2: dict, title, xLabel, 
             yLabel, log=False, figsize=(20, 12)) -> None:

        font = {'family': 'serif', 'color': 'darkred', 
                'weight': 'normal', 'size': 16}

        # Create subplots
        fig, axs = plt.subplots(2, 1, figsize=figsize, sharex=True)

        # Plot for the first set of data
        axs[0].set_title(title, fontsize=35, fontdict=font, y=1.05)
        axs[0].set_ylabel(yLabel, fontsize=30, fontdict=font)
        axs[0].tick_params(axis='both', which='major', labelsize=20)
        axs[0].grid(True, which='both', linestyle='--', linewidth=0.5)

        for key in yVals1:
            if log:
                axs[0].semilogx(xVals1, yVals1[key], label=key)
            else:
                axs[0].plot(xVals1, yVals1[key], label=key)

        axs[0].legend(fontsize=20)

        # Plot for the second set of data
        axs[1].set_xlabel(xLabel, fontsize=30, fontdict=font)
        axs[1].set_ylabel(yLabel, fontsize=30, fontdict=font)
        axs[1].tick_params(axis='both', which='major', labelsize=20)
        axs[1].grid(True, which='both', linestyle='--', linewidth=0.5)

        for key in yVals2:
            if log:
                axs[1].semilogx(xVals2, yVals2[key], label=key)
            else:
                axs[1].plot(xVals2, yVals2[key], label=key)

        axs[1].legend(fontsize=20)

        plt.tight_layout()
        
    def start_game_clicked(self) -> None:
        self.frontend.main_stack.setCurrentIndex(1)
        self.game_timer.start(1000)

    def plot_prog(self, xVals1, xVals2, yVals1: dict, yVals2: dict, title, xLabel, 
             yLabel, log=False, figsize=(20, 12)) -> None:

        font = {'family': 'serif', 'color': 'darkred', 
                'weight': 'normal', 'size': 16}

        # Create subplots
        fig, axs = plt.subplots(2, 1, figsize=figsize, sharex=True)

        # Plot for the first set of data
        axs[0].set_title(title, fontsize=35, fontdict=font, y=1.05)
        axs[0].set_ylabel(yLabel, fontsize=30, fontdict=font)
        axs[0].tick_params(axis='both', which='major', labelsize=20)
        axs[0].grid(True, which='both', linestyle='--', linewidth=0.5)
        axs0_secondary = axs[0].twinx()
        axs0_secondary.set_ylabel("Instability ($\\sigma$)", fontsize=30, fontdict=font)
        axs0_secondary.tick_params(axis='both', which='major', labelsize=20)

        nr = 0
        handles, labels = [], []
        for key in yVals1.keys():
            if nr == 0:
                handle, = axs[0].plot(xVals1, yVals1[key], label=key, color = "red")
                handles.append(handle)
                labels.append(key)
                nr += 1
            else:
                handle, = axs0_secondary.plot(xVals1, yVals1[key], label = key, color = "blue")
                handles.append(handle)
                labels.append(key)
                nr = 0

        # Create a joined legend
        axs[0].legend(handles, labels, loc="upper left", fontsize=20)
        
        
        # Plot for the second set of data
        axs[1].set_xlabel(xLabel, fontsize=30, fontdict=font)
        axs[1].set_ylabel(yLabel, fontsize=30, fontdict=font)
        axs[1].tick_params(axis='both', which='major', labelsize=20)
        axs[1].grid(True, which='both', linestyle='--', linewidth=0.5)
        axs1_secondary = axs[1].twinx()
        axs1_secondary.set_ylabel("Instability ($\\sigma$)", fontsize=30, fontdict=font)
        axs1_secondary.tick_params(axis='both', which='major', labelsize=20)

        handles, labels = [], []
        for key in yVals2:
            if nr == 0:
                handle, = axs[1].plot(xVals2, yVals2[key], label=key, color = "red")
                handles.append(handle)
                labels.append(key)
                nr += 1
            else: 
                handle, = axs1_secondary.plot(xVals2, yVals2[key], label = key, color="blue")
                handles.append(handle)
                labels.append(key)

        axs[1].legend(handles, labels, loc="upper left", fontsize=20)
        
        

        plt.tight_layout()

    def save_progress_Excel(self, user: UserModel):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self.frontend, "Save Excel File", "", "Excel Files (*.xlsx)", options=options)

        data = {
            "Left hand error (MSE)" : [],
            "Right hand error (MSE)" : [],
            "Left hand instability (std)" : [],
            "Right hand instability (std)" : []
        }
        
        if file_path:
        
            for game in user.games:
                
                data["Left hand error (MSE)"].append(game.left_error)
                data["Right hand error (MSE)"].append(game.right_error)
                data["Left hand instability (std)"].append(game.left_instability)
                data["Right hand instability (std)"].append(game.right_instability)
        
            df = pd.DataFrame(data)
            writer = pd.ExcelWriter(file_path, engine='openpyxl')
            df.to_excel(writer, index=True, sheet_name='Sheet1')
            writer.close()  # Use writer.close() to save the Excel file
            
            # Open the workbook using openpyxl
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            
            # Set column widths based on the length of the text in the first row of each column
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter  # Get the column name
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2) * 1.2  # Adjust width slightly for padding
                ws.column_dimensions[column].width = adjusted_width
            
            wb.save(file_path)
                   
    def save_game_Excel(self, game: GameModel):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self.frontend, "Save Excel File", "", "Excel Files (*.xlsx)", options=options)
        
        time_axis = json.loads(game.time_axis)
        le = [game.left_error]
        re = [game.right_error]
        li = [game.left_instability]
        ri = [game.right_instability]
        le.extend([np.nan for i in range(len(time_axis)-1)])
        re.extend([np.nan for i in range(len(time_axis)-1)])
        li.extend([np.nan for i in range(len(time_axis)-1)])
        ri.extend([np.nan for i in range(len(time_axis)-1)])
        
        if file_path:
            data = {
                "Time" : time_axis,
                "Left hand force" : json.loads(game.left_force),
                "Left hand target" : json.loads(game.left_force_target),
                "Right hand force" : json.loads(game.right_force),
                "Right hand target" : json.loads(game.right_force_target),
                "Left hand error (MSE)" : le,
                "Left hand instability (std)" : li,
                "Right hand error (MSE)" : re,
                "Right hand instability (std)" : ri 
            }
            
            df = pd.DataFrame(data)
            writer = pd.ExcelWriter(file_path, engine='openpyxl')
            df.to_excel(writer, index=True, sheet_name='Sheet1')
            writer.close()  # Use writer.close() to save the Excel file
            
            # Open the workbook using openpyxl
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            
            # Set column widths based on the length of the text in the first row of each column
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter  # Get the column name
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2) * 1.2  # Adjust width slightly for padding
                ws.column_dimensions[column].width = adjusted_width
            
            wb.save(file_path)
            
if __name__ == "__main__":

    application = QApplication(sys.argv)
    ja = Backend()
    #ja.database_handler.add_user("Jakob")
    #ja.database_handler.add_user("Finn Christian")
    #ja.database_handler.add_user("Martin")
    ja.show()
    sys.exit(application.exec_())