import csv
import sys
import time
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# import geopandas as gpd

import denforest
import lctree

# Input data is in format (x, y, timestamps) and sorted in time order
# Use count-based window
# The data points in the same stride are processed together

# ex) python3.8 main.py ../dataset/input.csv 5 1.5 100 10
inputFile = sys.argv[1]
tau = int(sys.argv[2])
eps = float(sys.argv[3])
window = int(sys.argv[4])
stride = int(sys.argv[5])

data = np.loadtxt(open(inputFile), delimiter=",") # dataset

# start time set to zero
currentTime = 0

# hash table for n-cores
ncoreTable = {}

for i in range(0, int(len(data) / stride)):
    
    # New data points in the same stride
    spts = data[i * stride:(i + 1) * stride]

    # add timestamp for each data points
    spts = np.insert(spts, 2, currentTime, axis=1)

    # insert data points into the window (wpts)
    if i == 0:
        wpts = spts
    else:
        wpts = np.vstack((wpts, spts))

    # Insert
    for p in spts:
        # TODO: insert p into the SpatialIndex
        
        # STEP 1: Point Classification
        # make N_eps_prev set
        N_eps_prev = np.empty([0, 3])
        for d in wpts:
            dist = math.dist(p[0:2], d[0:2])
            if p is not d and dist <= eps:
                N_eps_prev = np.vstack((N_eps_prev, d))
        
        # if p is nostalgic core
        if len(N_eps_prev) >= tau:
            mst = 0
            # STEP 2: Determination of Core-expiration Time
            # sort the eps-neighbors in the order of timestamps
            sorted_N_eps_prev = N_eps_prev[N_eps_prev[:,2].argsort()]

            # q is a point such that its timestamp q.T is the tau-th largest
            # p.Tc = q.T + |W|
            expT = sorted_N_eps_prev[tau - 1][2] + window

            # hashmap with core-expiration time as key and (x, y, T) as value
            ncoreTable.update({int(expT):p})

            for key in ncoreTable:
                n = ncoreTable[key]

                if p is not n and n in N_eps_prev:
                    if key >= currentTime and denforest.Connect(p, n):
                        mst += 1

            # determine the type of cluster evolution by the mst value
            if mst == 0:
                evol_type = "emerges"
            elif mst == 1:
                evol_type = "expands"
            else:
                evol_type = "merged"

        # TODO: STEP 4: Updating Borders
    Eq = []
    # Delete
    if(i * stride > window):
        # Outdated data points in the stride
        spts = data[(i * stride) - window:(i + 1) * stride - window]

        for q in spts:
            # Delete q from the SpatialIndex
            # 순서를 바꾸어도 괜찮은지..?
            wpts = np.delete(wpts,0,0)

            # print(q)
            # Step1 : q가 deletion 됐을 때 주변점들의 n-core 여부
            for ncore in ncoreTable[currentTime]:
                dist = math.dist(q, ncore[0:2])
                if q is not ncore and dist <= eps:
                    Eq.append(ncore)
        
        # Step 2
        for x in Eq:
            lenOfL = len(edgeTable[x])
            if lenOfL == 0:
                evol_type = "dissipates"
            elif lenOfL == 1:
                evol_type = "shrinks"
            else:
                evol_type = "split"

            for y in edgeTable[x]:
                Cut(x, y)

            # Reclassify x as either border or noise by the |L| value
            for d in wpts:
                dist = math.dist(x[0:2], d[0:2])
                if(d is not x and dist < eps):


            

    currentTime += 1