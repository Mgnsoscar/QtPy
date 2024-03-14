from __future__ import annotations
from typing import Literal, Dict, Union, Optional, List
from PyQt5.QtWidgets import QApplication
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

import sys


class Backend:
    
    def __init__(self) -> None:
        
        self.current_user: UserModel = None
        
        self.serial_reader = SerialDevice(
            baudrate = 115200,
            timeout = 0.01
        )
        try: self.serial_reader.newPort("COM4")
        except: pass
        
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

        # Initialize some variables
        self.max_sensor_in = 4000
        self.calibration_constant = 0.023
        self.angle_scaling = 60
        
        self.reset_game()
        
        # Initialize the different timers/threads
        self.init_timers()

    def write_read(self, write_value: str = None):
        #if self.serial_reader.portConnected():
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
        
        if self.checkmarks["game_duration"] == -1:
            self.start_timestamp = perf_counter()
        
        self.sensor_reader.start(100)
             
        self.set_new_targets()
        self.checkmarks["game_duration"] += 1
        
        if self.checkmarks["game_duration"] == 60:
            self.game_timer.stop()
            self.sensor_reader.stop()
            self.checkmarks["game_duration"] = -1  
                       
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
            
            self.database_handler.add_game_to_user(
                user_id = self.current_user.id,
                game = {
                    "time_axis":time_axis,
                    "left_force":left_force,
                    "right_force":right_force,
                    "left_force_target":left_force_target,
                    "right_force_target":right_force_target
                }
            )
            self.frontend.main_stack.setCurrentIndex(0)
            self.frontend.page_1.user_list.search_input.setText("")
            self.frontend.page_1.user_list.search_user()
            self.reset_game()
   
    def reset_game(self) -> None:
        self.checkmarks = {
            "game_duration" : -1,
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
        
        if game_duration  == 5 or game_duration == 15:
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
        elif game_duration == 30 or game_duration == 45:
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
        
        #if self.serial_reader.portConnected():
        #    data = self.write_read()
        #    if len(data) == 4:
        #        self.force["left"] = - float(data[0])
        
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
            perf_counter() - self.start_timestamp
        )
        
        self.move_plane_with_keys(False, False, False, False, False, False)
        
    def move_plane_with_keys(self, up, down, left, right, a, d):
        
        self.force["left"] += (-50 * a) + (50 * d)
        self.force["right"] += (-50 * down) + (50 * up)
        
        if self.force["left"] > self.max_sensor_in: 
            self.force["left"] = self.max_sensor_in
        elif self.force["left"] < -self.max_sensor_in:
            self.force["left"] = -self.max_sensor_in
        
        if self.force["right"] > self.max_sensor_in: 
            self.force["right"] = self.max_sensor_in
        elif self.force["right"] < -self.max_sensor_in:
            self.force["right"] = -self.max_sensor_in
        
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




if __name__ == "__main__":

    application = QApplication(sys.argv)
    ja = Backend()
    #ja.database_handler.add_user("Jakob")
    #ja.database_handler.add_user("Finn Christian")
    #ja.database_handler.add_user("Martin")
    ja.show()
    sys.exit(application.exec_())