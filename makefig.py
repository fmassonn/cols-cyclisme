# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 22:38:31 2019

@author: massonnetf
"""


# Imports
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
import os
from   mpl_toolkits.basemap import Basemap
from   scipy import interpolate
from   mpl_toolkits.mplot3d import Axes3D



# Input files
filein = [
          ["Col Agnel (depuis Casteldelfino)"        ],
          #["", 0], ["", 0], ["", 0], ["", 0], ["", 0], ["", 0], ["", 0], 
          #["", 0], ["", 0], ["", 0], ["", 0], ["", 0], ["", 0], ["", 0], 
          #["", 0], ["", 0], ["", 0], ["", 0], ["", 0], ["", 0], ["", 0], 
          #["", 0], ["", 0], ["", 0], ["", 0], ["", 0], ["", 0], ["", 0], 
          #["", 0], ["", 0], ["", 0], ["", 0], ["", 0], ["", 0], ["", 0], 
          #["", 0], ["", 0], ["", 0], ["", 0], ["", 0], ["", 0], 
          ["L'Alpe d'Huez (depuis Le Bourg-d'Oisans)"],
          ["Andorre Arcalis (depuis Ordino)"         ],
          ["Col d'Aubisque (depuis Argelès-Gazost)"  ],
          ["Port de Balès (depuis Mauléon-Barousse)" ],
          ["Plateau de Beille (depuis Les Cabannes)" ],
          ["Col de la Biche (depuis Gignez)"         ],
          ["Montée de Bisanne (depuis Villard-Sur-Doron)"],
          ["Cime de la Bonette (depuis Saint-Etienne-de-Tinée)"],
          ["Chamrousse (depuis Uriage-les-Bains)"]
         ]

# Colors
colors = [[ccc / 255 for ccc in cc] for cc in 
          [
           [4  , 139, 154],
           [170, 240, 209],
           [207, 160, 233],
          ]
         ]

colors = [np.random.random(3) for i in range(len(filein))]
# Define projection
def projection(lon, lat):
    lon = np.array(lon)
    lat = np.array(lat)
    m = Basemap(width=12000000,height=9000000,
            rsphere=(6378137.00,6356752.3142),\
            resolution='l',area_thresh=1000.,projection='lcc',\
            lat_1=45.,lat_0=51.0,lon_0=4.0)
    
    x, y = m(lon, lat)
    
    return (x - x[0]) / 1e3, (y - y[0]) / 1e3


def difficulty_index(H, D, T):
    # From https://www.climbbybike.com/fr/climbbybike_index.asp
    # H : altitude gain in meters
    # D : distance riden in meters
    # T : top altitude
    out = (H*100/D)*4 + H**2/D + D/1000 
    if T > 1000.0:
        out += (T-1000)/100
    return out

# Projection for final map

m = Basemap(llcrnrlon = -1.7 ,llcrnrlat = 41.3, urcrnrlon = 9.0 ,
            urcrnrlat = 48.8,
            projection='lcc',lat_1=43.5, lat_2=45.3, lon_0 = 2.4,
            resolution ='c', area_thresh=1000.)
 
print('TACHY')

# Loop over files
    
fig = plt.figure("figall", figsize = (32, 16))

for file in enumerate(filein):
    id = file[0] + 1
    jf = file[0]
    if jf + 1 >= 34:
        plt.subplot(4, 12, jf + 4)
    else:
        plt.subplot(4, 12, jf + 1)

    if not os.path.exists("./data/" + file[1][0] + ".gpx"):
        print("hello")
        plt.plot((0, 1), (0, 1))
        plt.title(file[0] + 1)
    else:
        
        print(file)
        f = file[1][0] + ".gpx"

        
        # Initialize coordinates
        lon = list()
        lat = list()
        z   = list()

        # Parse XML file
        tree = ET.parse("./data/" + f)
        root = tree.getroot()
        
        # Load data
        for j in range(len(root[1][3])):
            lon.append(float(root[1][3][j].attrib["lon"]))
            lat.append(float(root[1][3][j].attrib["lat"]))
            z.append(float(root[1][3][j][0].text))
        
        # Convert (lon,lat) to (x,y)
        x, y = projection(lon, lat)
        # Convert elevation to array
        z = np.array(z)
        
        
        # Smooth
        #neighb = d[1:] - d[:-1]
        #num_true_pts = len(z) * 2
        #num_sample_pts = len(z)
        #tck, u = interpolate.splprep([x, y, z], s = 0.5, k = 5)
        #u_fine = np.linspace(0,1,num_true_pts)
        #x_fine, y_fine, z_fine = interpolate.splev(u_fine, tck)
        
        # Compute distance from start
        d = np.append([0.0], np.cumsum(np.sqrt(np.diff(x     ) ** 2 + 
                                               np.diff(y     ) ** 2)))
        #d_fine = np.append([0.0], np.cumsum(np.sqrt(np.diff(x_fine) ** 2 + np.diff(y_fine) ** 2)))
        #sl_fine = np.diff(z_fine) / np.diff(d_fine * 1000.0) * 100.0
        
        # Compute slopes, per dd horizontal steps
        slope = list()
        
        dd = 0.2 # step, km. 200 m is a good tradeoff that avoids overestimating
                 # slopes when two successive points miss a needle turn, and is 
                 # short enough to render realistic max values. And the mean is well
                 # estimated
        d2 = d[-1]
        d1 = d2 - dd
        
        while d1 > 0:
          xx = d[(d>d1) * (d<=d2)]
          zz = z[(d>d1) * (d<=d2)]
          try:
              slope.append(np.polyfit(xx * 1000, zz, 1)[0] * 100.0)
          except TypeError:
              pass
          d1 -= dd# / 10.0
          d2 -= dd# / 10.0
          
        slope = np.array(slope)
        
        score = difficulty_index((z[-1] - z[0]), (d[-1] - d[0]) * 1000.0, z[-1])
        
        # Plots
        plt.fill_between(d, z, color = colors[jf])
        plt.ylim(0, 3000)
        plt.xlim(0, d[-1])
        plt.text(0, 0, str(np.round(np.mean(slope), 1)) + "% (" + str(np.round(np.max(slope))) + "%)")
        plt.title(str(id) + ". " + f.split(" (")[0] + "\n" + str(np.round(score)))
        
        plt.tight_layout()
    
        plt.subplot(2, 4, 8)
        xx, yy = m(lon[-1], lat[-1])
        plt.scatter(xx, yy, 50, colors[jf])
        plt.text(xx, yy, str(id), color = "white", ha = "center", va = "center")
 
plt.subplot(2, 4, 8)           
m.drawcoastlines(linewidth = 1)
m.drawcountries(linewidth = 1)   
#
#m = Basemap(llcrnrlon = -1.7 ,llcrnrlat = 41.3, urcrnrlon = 9.0 ,
#            urcrnrlat = 48.8,
#            projection='lcc',lat_1=43.5, lat_2=45.3, lon_0 = 2.4,
#            resolution ='l', area_thresh=1000.)
#m.drawcoastlines(linewidth = 1)
#m.drawcountries(linewidth = 1)

    
plt.subplots_adjust(hspace = 0.2)
plt.savefig("./figs/figall.png", dpi = 300)

    #plt.savefig("./figs/" + f[:-4] + ".pdf")
    
#    plt.subplot(2, 2, 1)
#    plt.scatter(x, y, 0.1)
#    plt.xlabel("x [km]")
#    plt.ylabel("y [km]")
#    plt.grid()
#    plt.title("Tracé")
#    
#    plt.subplot(2, 2, 2)
#    plt.plot(d, z)
#    plt.xlabel("d [km]")
#    plt.ylabel("z [m]")
#    plt.grid()
#    plt.title("Profil")
#    #plt.plot(d_fine, z_fine, "g")
#    
#    ax3d = fig.add_subplot(223, projection = '3d')
#    ax3d.plot(x, y, z, "b")
#    ax3d.set_xlabel("x [km]")
#    ax3d.set_ylabel("y [km]")
#    ax3d.set_zlabel("z [m]")
#    
#    plt.subplot(2, 2, 4)
#    plt.hist(slope, bins = np.arange(-5, 20), density = False)
#    plt.xlabel("Pente moyenne sur " + str(1000 * dd) + " m " + " [%]")
#    plt.ylabel("Nombre de segments")
#    plt.title("Distribution des pentes")
#    plt.grid()
#    #ax3d.plot(x, y, z, 'g')
#    plt.tight_layout()
#    plt.savefig("./fig.png", dpi = 500)