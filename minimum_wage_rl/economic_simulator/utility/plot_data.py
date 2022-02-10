import time
import matplotlib.pyplot as plt
from numpy.core import umath
from numpy.core.numeric import count_nonzero
from numpy.lib.function_base import average
plt.ion()
import numpy as np
import pandas as pd

plt.style.use("dark_background")

class DynamicUpdate():
    #Suppose we know the x range
    min_x = 0
    max_x = 10

    def __init__(self) -> None:

        self.y_values_1 = 2
        self.y_values_2 = 2
        self.y_values_3 = 3
        self.y_values_4 = 1

        self.xdata = []
        self.ydata_1 = [[] for _ in range(self.y_values_1)]
        self.ydata_2 = [[] for _ in range(self.y_values_2)]
        self.ydata_3 = [[] for _ in range(self.y_values_3)]
        self.ydata_4 = [[] for _ in range(self.y_values_4)]

    def on_launch(self):
        #Set up plot
        self.figure, self.ax = plt.subplots(2,2)
        self.figure.suptitle('AI Scenario', fontweight="bold", fontsize=18)

        self.y_values_1 = 2
        self.y_values_2 = 2
        self.y_values_3 = 3
        self.y_values_4 = 1

        self.lines_1 = [[] for _ in range(self.y_values_1)]
        self.lines_2 = [[] for _ in range(self.y_values_2)]
        self.lines_3 = [[] for _ in range(self.y_values_3)]
        self.lines_4 = [[] for _ in range(self.y_values_4)]

        self.lines_1[0], = self.ax[0,0].plot([],[], label="Expense")
        self.lines_1[1], = self.ax[0,0].plot([],[], label="Avg Salary")

        self.lines_2[0], = self.ax[0,1].plot([],[],label="Poverty")
        self.lines_2[1], = self.ax[0,1].plot([],[], label="Unemployment")

        self.lines_3[0], = self.ax[1,0].plot([],[],label="Junior")
        self.lines_3[1], = self.ax[1,0].plot([],[],label="Senior")
        self.lines_3[2], = self.ax[1,0].plot([],[],label="Executive")

        self.lines_4[0], = self.ax[1,1].plot([],[], label="Minimum Wage")

        self.ax[0,0].legend(loc="upper left")
        self.ax[0,1].legend(loc="upper right")
        self.ax[1,0].legend(loc="upper left")
        self.ax[1,1].legend(loc="upper left")

        for i in range(2):
            for j in range(2):
                self.ax[i,j].set_autoscaley_on(True)
                self.ax[i,j].set_autoscalex_on(True)
                self.ax[i,j].grid(linewidth=0.2)

        self.ax[0,0].set_title("Expense vs Average Salary", fontweight="bold", fontsize=12)
        self.ax[0,1].set_title("Poverty vs Unemployment", fontweight="bold", fontsize=12)
        self.ax[1,0].set_title("Jobs", fontweight="bold", fontsize=12)
        self.ax[1,1].set_title("Minimum wage", fontweight="bold", fontsize=12)

    def on_running(self, xdata, ydata,ax_value):
        #Update data (with the new _and_ the old points)

        # running_start_time = time.time()

        color_vals = ["blue","yellow"]
        if ax_value == 1:
            for i in range(self.y_values_1):
                self.lines_1[i].set_xdata(xdata)
                self.lines_1[i].set_ydata(ydata[i])
            
            self.ax[0,0].relim()
            self.ax[0,0].autoscale_view()
        
        elif ax_value == 2:
            for i in range(self.y_values_2):
                self.lines_2[i].set_xdata(xdata)
                self.lines_2[i].set_ydata(ydata[i])
                self.ax[0,1].fill_between(xdata,ydata[i], alpha=0.04, facecolor=color_vals[i])    
            
            self.ax[0,1].relim()
            self.ax[0,1].autoscale_view()

        elif ax_value == 3:
            for i in range(self.y_values_3):
                self.lines_3[i].set_xdata(xdata)
                self.lines_3[i].set_ydata(ydata[i])

            self.ax[1,0].relim()
            self.ax[1,0].autoscale_view()

        # Minimum wage
        else:
            ax4_colors = "green"
            for i in range(self.y_values_4):
                self.lines_4[i].set_xdata(xdata)
                self.lines_4[i].set_ydata(ydata[i])
                
            self.ax[1,1].fill_between(xdata,ydata[i], alpha=0.04, facecolor=ax4_colors)
            self.ax[1,1].relim()
            self.ax[1,1].autoscale_view()
        #Need both of these in order to rescale
        #We need to draw *and* flush

        # print("On Runnung  - ", time.time() - running_start_time)

    def draw(self):
        # running_start_time_2 = time.time()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        # print("Drawing canvas - ", time.time() - running_start_time_2)

    #Example
    def __call__(self):
        self.on_launch()

    def update_xdata(self,x):
        self.xdata.append(x)

    def plot_repeated(self,x,y,ax_val, block_value):
        import numpy as np
        
        # repeated_start_time = time.time()

        if ax_val == 1:
            for i in range(self.y_values_1):
                self.ydata_1[i].append(y[i])
            self.on_running(self.xdata, self.ydata_1,ax_val)
        
        if ax_val == 2:
            for i in range(self.y_values_2):
                self.ydata_2[i].append(y[i])            
            self.on_running(self.xdata, self.ydata_2,ax_val)
        
        if ax_val == 3:
            for i in range(self.y_values_3):
                self.ydata_3[i].append(y[i])
            self.on_running(self.xdata, self.ydata_3,ax_val)
        
        if ax_val == 4:
            for i in range(self.y_values_4):
                self.ydata_4[i].append(y[i])
            self.on_running(self.xdata, self.ydata_4,ax_val)
        
        # print("In Repeated  -  ", time.time() - repeated_start_time)

        plt.show(block=block_value)
        

d = DynamicUpdate()
d()


df_1 = pd.read_excel("data\\ai_scenario_data.xlsx")

mini_wage = df_1["Minimum Wage"].tolist()

monthly_expense = (df_1["productPrice"]*30).tolist()
average_salary = df_1["Average Salary"].tolist()

poverty_rate = df_1["Poverty"].tolist()
unemployment_rate = df_1["Unemployment"].tolist()

junior_pos = df_1["Junior"].tolist() 
senior_pos = df_1["Senior"].tolist()
exec_pos = df_1["Executive"].tolist()

count = 0
x = 1
y = 2
z = 3

all_count = len(mini_wage)

for year_val,wage in enumerate(mini_wage):

    if year_val < all_count-1:
        block_value = False
    else:
        block_value = True

    d.update_xdata(year_val)
    d.plot_repeated(year_val, [monthly_expense[count],average_salary[count]], 1, block_value)
    d.plot_repeated(year_val, [poverty_rate[count],unemployment_rate[count]], 2, block_value)
    d.plot_repeated(year_val, [junior_pos[count], senior_pos[count], exec_pos[count]], 3, block_value)
    d.plot_repeated(year_val,[mini_wage[count]],4, block_value)
    count = count + 1
    d.draw()