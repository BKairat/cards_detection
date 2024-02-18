import cv2
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np
import json
import sys


if __name__ == "__main__":
    assert len(sys.argv) == 2, "calibration require 1 argument: mode (test or camera)"
    mode = sys.argv[1]
    assert mode in ["test", "camera"], "mode must be test or camera"
    
    file_path = f"masks_{mode}.json"
    image_path = f"images/{mode}/calibration_image.png"
    
    for color in ["red", "green", "blue", "yellow", "violet"]:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            colors = json.load(json_file)

        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        fig, ax = plt.subplots()
        
        plt.title(color)
        plt.subplots_adjust(left=0.25, bottom=0.45)
        
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        thresh = cv2.inRange(image_hsv, np.asarray(colors[color]["low"], dtype=np.uint8), np.asarray(colors[color]["high"], dtype=np.uint8))
        thresh = (thresh > 0.0001).astype(int)
        thresh = np.expand_dims(thresh, axis=2)
        thresh = np.repeat(thresh, 3, axis=2)
        
        img_plot = ax.imshow(image_rgb*thresh)
        
        ax_h_low = plt.axes([0.25, 0.3, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        ax_s_low = plt.axes([0.25, 0.25, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        ax_v_low = plt.axes([0.25, 0.2, 0.65, 0.03], facecolor='lightgoldenrodyellow')

        h_low_slider = Slider(ax_h_low, 'H_low', 0, 255, valinit=1)
        s_low_slider = Slider(ax_s_low, 'S_low', 0, 255, valinit=1)
        v_low_slider = Slider(ax_v_low, 'V_low', 0, 255, valinit=1)
        
        ax_h_high = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        ax_s_high = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        ax_v_high = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')

        h_high_slider = Slider(ax_h_high, 'H_high', 0, 255, valinit=1)
        s_high_slider = Slider(ax_s_high, 'S_high', 0, 255, valinit=1)
        v_high_slider = Slider(ax_v_high, 'V_high', 0, 255, valinit=1)
        

        def update(val):
            colors[color]["low"][0] = h_low_slider.val
            colors[color]["low"][1] = s_low_slider.val
            colors[color]["low"][2] = v_low_slider.val
            
            colors[color]["high"][0] = h_high_slider.val
            colors[color]["high"][1] = s_high_slider.val
            colors[color]["high"][2] = v_high_slider.val
            
            thresh = cv2.inRange(image_hsv, np.asarray(colors[color]["low"], dtype=np.uint8), np.asarray(colors[color]["high"], dtype=np.uint8))
            thresh = (thresh > 0.0001).astype(int)
            thresh = np.expand_dims(thresh, axis=2)
            thresh = np.repeat(thresh, 3, axis=2)

            adjusted_image = image_rgb * thresh
            img_plot.set_data(adjusted_image)
            fig.canvas.draw_idle()
            
        h_low_slider.on_changed(update)
        s_low_slider.on_changed(update)
        v_low_slider.on_changed(update)
        
        h_high_slider.on_changed(update)
        s_high_slider.on_changed(update)
        v_high_slider.on_changed(update)
        
        plt.show()
        
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(colors, json_file)
