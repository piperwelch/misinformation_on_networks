import matplotlib.pyplot as plt
import glob
import numpy as np
files = glob.glob("*applied_*.csv")
for file in files:
    f = open(file, "r")
    data_list = [0]*6
    mis_counts = []
    inf_counts = []
    neu_counts = []

    fig, ax = plt.subplots(6, 2,  figsize = (20, 20), sharey=True, sharex=True)
    
    ax = ax.flatten()

    for line in f:
        spl = line.split("[")
        
        mis_inf = spl[0].split(",")
        mis_counts_raw = spl[1].split(",")
        fig.suptitle("Reduction Applied on Day {}\n Initial Informed Node Percentile: {}".format(file[-5], float(mis_inf[2])*100), fontsize = 25)
        for count in mis_counts_raw:
            count = count.strip("]\n")
            if count != '':
                mis_counts.append(float(count))

        inf_counts_raw = spl[2].split(",")
        for count in inf_counts_raw:
            count = count.strip("]\n")
            if count != '':
                inf_counts.append(float(count))
        
        neu_counts_raw = spl[3].split(",")
        cont = False
        for count in neu_counts_raw:
            count = count.strip("]\n")
            if count != '':
                neu_counts.append(float(count))
        
        if float(mis_inf[0]) == 1.0:
            num = 0
        elif float(mis_inf[0]) == 0.9:
            num = 1
        elif float(mis_inf[0]) == 0.8:
            num = 2
        elif float(mis_inf[0]) == 0.7:
            num = 3
        elif float(mis_inf[0]) == 0.6:
            num = 4   
        elif float(mis_inf[0]) == 0.5:
            num = 5
        elif float(mis_inf[0]) == 0.4:
            num = 6
        elif float(mis_inf[0]) == 0.3:
            num = 7
        elif float(mis_inf[0]) == 0.2:
            num = 8
        elif float(mis_inf[0]) == 0.1:
            num = 9
        elif float(mis_inf[0]) == 0.0:
            num = 10
        print(file, num)

        ax[num].plot(mis_counts, label = "misinformed")
        ax[num].plot(inf_counts, label = "informed")
        ax[num].plot(neu_counts, label = "neutral")
        ax[num].set_title("Target Node Spread Reduction: " + str(mis_inf[0]), fontsize = 15)
        ax[num].set_xlabel("Time", fontsize = 15)
        ax[num].set_ylabel("Number Nodes", fontsize = 15)
        ax[num].set_ylim(0, 500000)
        ax[num].legend()

        # ax[num].set_xticks(np.arange(0, 20, 1), np.arange(0, 20, 1))


        mis_counts = []
        inf_counts = []
        neu_counts = []
    plt.subplots_adjust(top=0.9, bottom = 0.02)
    fig.delaxes(ax[10])
    fig.delaxes(ax[11])
    plt.xticks(np.arange(0, 20, 1), np.arange(0, 20, 1))
    
    plt.savefig("plot_{}.png".format(file))