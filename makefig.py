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
import pyglet

from   scipy import interpolate
from   mpl_toolkits.mplot3d import Axes3D

import cartopy.crs as ccrs
import cartopy.feature as cf

# Input files
filein = [
          ["Col Agnel (depuis Casteldelfino)"                         ],
          ["L'Alpe d'Huez (depuis Le Bourg-d'Oisans)"                 ],
          ["Andorre Arcalis (depuis Ordino)"                          ],
          ["Col d'Aubisque (depuis Argelès-Gazost)"                   ],
          ["Port de Balès (depuis Mauléon-Barousse)"                  ],
          ["Plateau de Beille (depuis Les Cabannes)"                  ],
          ["Col de la Biche (depuis Gignez)"                          ],
          ["Montée de Bisanne (depuis Villard-Sur-Doron)"             ],
          ["Cime de la Bonette (depuis Saint-Etienne-de-Tinée)"       ],
          ["Chamrousse (depuis Uriage-les-Bains)"                     ],
          ["Mont du Chat (depuis Yenne)"                              ],
          ["Col de la Croix-de-Fer (depuis Saint-Jean-de-Maurienne)"  ],
          ["Finhaut-Émosson (depuis Giétroz)"                         ],
          ["Col du Galibier (depuis le Col du Lautaret)"              ],
          ["Col du Glandon (depuis le Barrage du Verney)"             ],
          ["Plateau des Glières (depuis Le-Petit-Bornand-les-Glières)"],
          ["Col du Grand Colombier (depuis Artemare)"                 ], 
          ["Col du Grand-Saint-Bernard (depuis Sembrancher)"          ],
          ["Col de Granon (depuis Saint-Chaffrey)"                    ],
          ["Hautacam (depuis Argelès-Gazost)"                         ],
          ["Col de l'Iseran (depuis Lanslebourg-Mont-Cenis)"          ],
          ["Col d'Izoard (depuis Montbardon)"                         ],
          ["Col de Joux-Plane (depuis Samoëns)"                       ],
          ["La Plagne (depuis Aime)"                                  ],
          ["Port de Larrau (depuis l'Auberge Logibar)"                ],
          ["La Ruchère en Chartreuse (depuis Saint-Christophe-sur-Guiers)"],
          ["Col de la Lombarde (depuis Pratolungo)"                   ],
          ["Col de la Loze (depuis Brides-les-Bains)"                 ],    
          ["Luz-Ardiden (depuis Luz-Saint-Sauveur)"                   ],
          ["Col de la Madeleine (depuis Feissonnet)"                  ],
          ["Col du Mont-Cenis (depuis Susa)"                          ],
          ["Port de Pailhères (depuis Usson-les-Bains)"               ],
          ["Pla d'Adet (depuis Vignec)"                               ],
          ["Col de Portet (depuis Vignec)"                            ],
          ["Col du Pré (depuis Beaufort)"                             ],
          ["Puy de Dôme (depuis Clermont-Ferrand)"                    ],
          ["Semnoz (depuis Quintal)"                                  ],
          ["Col de Soudet (depuis Arette)"                            ],
          ["Col du Soulor (depuis Ferrières)"                         ],
          ["Superbagnères (depuis Bagnères-de-Luchon)"                ],
          ["Col du Tourmalet (depuis Luz-Saint-Sauveur)"              ],
          ["Val Thorens (depuis Moutiers)"                            ],
          ["Mont Ventoux (depuis Bédoin)"                             ],          
         ]

# Colors
colors = [
          "#6C1B72",
          "#9016B2",
          "#A24CC8",
          "#9950B2",
          "#A276CC",
          "#C084DC",
          
          "#00496E",
          "#00529B",
          "#0067C6",
          "#0076CC",
          "#00A0E2",
          "#40BDE8",
          
          "#006068",
          "#006F7A",
          "#008193",
          "#0097AC",
          "#36CCDA",
          "#8EDBE5",
          
          "#006651",
          "#007B63",
          "#00B08B",
          "#00C590",
          "#3BD6B2",
          "#81E0C7",
          
          "#E0CA00",
          "#EADB1B",
          "#EDE25E",
          "#EEE88D",
          "#EEEAA5",
          "#EEEBB6",
          
          "#ED8000",
          "#FF7200",
          "#FF963B",
          "#FFB754",
          "#FDC87D",
          "#FFB57B",
          
          "#F02233",
          "#F9455B",
          "#FF5B60",
          "#FB6581",
          "#FF818C",
          "#FFB6B1",         ]

# Rearrange colors by row
colors = [c for j in range(7) for c in colors[j::6]]
#colors = [np.random.random(3) for i in range(len(filein))]

# Font stuff
fontfile = "ERASLGHT"
fontname = "Eras Medium ITC"

fontfilet = "GOTHIC"
fontnamet = "Century Gothic"

#fontfile = "Existence-Light"
#fontname = "Existence Light"

pyglet.font.add_file("./fonts/" + fontfile + ".ttf")
font = pyglet.font.load(fontname, bold = True)

pyglet.font.add_file("./fonts/" + fontfilet + ".ttf")
font = pyglet.font.load(fontnamet)

# Define projection
def projection(lon, lat):
    
    """
    lat and lon in degrees
    Converts a path expressed as two 1-d arrays of lon and lat into a path
    expressed as  two 1-d arrays of x and y
    
    """
    lat0 = 46.8473939
    lon0 = 3.0766819
    

    a = 6356000 # Earth radius
    
        
    lon = np.array(lon)
    lat = np.array(lat)
    
    x = np.pi / 180 * (lon - lon0) * a * np.cos(lat * np.pi / 180)
    y = a * np.pi / 180 * (lat - lat0) 
     
    
    
    return x / 1e3 , y / 1e3


def difficulty_index(H, D, T):
    # From https://www.climbbybike.com/fr/climbbybike_index.asp
    # H : altitude gain in meters
    # D : distance riden in meters
    # T : top altitude
    out = (H*100/D)*2 + H**2/D + D/1000 
    if T > 1000.0:
        out += (T-1000)/100
    return out

# Function used later to map a set of points to [0, 1[]]
def map_coordinates(x, y, x1, x2, y1, y2, minx, maxx, miny, maxy):
        xx = x1 + (x - minx) * (x2 - x1) / (maxx - minx)
        yy = y1 + (y - miny) * (y2 - y1) / (maxy - miny)
        return xx, yy
            


plt.close("all")
# Loop over files

myStats = list() # Will contain data for plotting difficulty etc.

fig = plt.figure("figall", figsize = (39 / 2.54 , 29 / 2.54), dpi = 600)
for file in enumerate(filein):
    id = file[0] + 1
    jf = file[0]
    plt.subplot(7, 7, id)


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
        
        myStats.append([f.split(" (")[0], z[-1] - z[0], (d[-1] - d[0]) * 1000.0, z[-1], score])
        
        # Plots
        plt.fill_between(d / d[-1], (z - z[0]) / (z[-1] - z[0]), color = colors[jf])

        plt.title(f.split(" (")[0] + "\n", color = colors[jf], 
                      fontname = fontname)
        
        plt.text(0.92, 0.5,  str(int((z[-1] - z[0]))) + " m ", 
                 color = "white", rotation = 90, va = "center", fontname = fontname, fontsize = 6)
        plt.text(0.5, 0.02, str(np.round(d[-1], 1)) +
                 " km", color = "white", ha = "center", fontname = fontname, fontsize = 6)
        plt.text(1.0, 1.0,  " " + str(int(z[-1])) + " m", 
                 color = colors[jf], ha = "left", fontname = fontname, fontsize = 6)
        plt.text(0.0, 0.0,  str(int(z[0])) + " m ", 
                 color = colors[jf], ha = "right", fontname = fontname, fontsize = 6)
        plt.text(0.7, 0.3,  str(np.round((z[-1] - z[0]) / 
                                         ((d[-1] - d[0]) * 1000) * 100, 1)) + 
            " %", rotation = 45, ha = "center", 
            va = "center", color = "white", fontname = fontname, fontsize = 6   )
        

        # Plot road in box. Scale data depending on the dimension that has 
        # the largest span.
        # Box coordinates
        x1, x2 = -0.10, 0.2
        y1, y2 = 0.7, 1.0
               
        if np.max(x) - np.min(x) > np.max(y) - np.min(y):
            # Scale factor: along x so that when divided by this number we have x2 - x1
            scalef = (np.max(x) - np.min(x)) / (x2 - x1)
        else:
            scalef = (np.max(y) - np.min(y)) / (y2 - y1)
        
        # Squeeze data and make mean of data pass through mean of box. 
        xx = (x - np.mean(x)) / scalef  + (x2 - np.max((x - np.mean(x)) / scalef))   #(x1 + x2) / 2.0 + (x - x[0]) / scalef - np.sign(x[-1] - x[0]) * (x2 - x1) / 2
        yy = (y - np.mean(y)) / scalef  + (y2 - np.max((y - np.mean(y)) / scalef))   #(y1 + y2) / 2.0 + (y - y[0]) / scalef - np.sign(y[-1] - y[0]) * (y2 - y1) / 2       

        ha = "center"
        va = "center"
        
        if x[-1] - np.mean(x) > 0:
            ha = "right"
        elif x[-1] - np.mean(x) <= 0:
            ha = "left"
            
        if y[-1] - np.mean(y) < 0:
            va = "bottom"
        elif y[-1] - np.mean(y) >=0 :
            va = "top"
            

            
        from_place = f.split(" (")[1].split(")")[0].split("depuis ")[1]
        from_place = from_place[0].upper() + from_place[1:]
        if from_place == "Saint-Etienne-de-Tinée" or  \
                from_place == "Lanslebourg-Mont-Cenis" or \
                from_place == "Le Barrage du Verney":

            ha = "center"

        x_txt = xx[0] + np.sign(xx[0] - np.mean(xx)) * (x2 - x1) * 0.1
        y_txt = yy[0] + np.sign(yy[0] - np.mean(yy)) * (y2 - y1) * 0.1
        plt.text(x_txt, y_txt, from_place, color = colors[jf], 
                 fontsize = 4, ha = ha, va = va, fontname = fontname)
        plt.plot(xx, yy, lw = 0.5, color = colors[jf])
        plt.scatter(xx[0], yy[0], 2, marker = "o", color = colors[jf], 
                    zorder = 1000)
        plt.scatter(xx[-1], yy[-1], 4, marker = "o", color = "black", 
                    zorder = 1000, facecolors = "none", lw = 0.4)
        plt.scatter(xx[-1], yy[-1], 0.3, marker = "o", color = "black", 
                    zorder = 1001, lw = 0.3)
        

        



        # ax = plt.axes(projection = ccrs.LambertConformal(central_longitude=3.0, \
        #                                                  central_latitude=43.0,\
        #                 false_easting=0.0, false_northing=0.0, secant_latitudes=None, \
        #                     standard_parallels=None, globe=None, cutoff=-30))
        # ax.set_extent([-5, 10, 42, 52])
        # ax.add_feature(cf.COASTLINE)
        # ax.add_feature(cf.BORDERS)
        
        #ax.set_xlim(0.0, 5.0)
        plt.axis("off")
        plt.tight_layout()
    
     
        
   
plt.subplots_adjust(hspace = 0.6)
sup = plt.suptitle( "HORS CATÉGORIE", fontsize = 122, fontname = fontnamet, color = [0.0, 0.0, 0.0])
plt.subplots_adjust(top = 0.80)


# Save figure
plt.savefig("./figs/figall.png")
plt.savefig("./figs/figall.pdf")



# Produce some stats
fig, ax = plt.subplots(1, 2, figsize = (8, 4))
for j, m in enumerate(myStats):
  ax[0].scatter(m[2] / 1e3, m[1], m[3] - 1100 , marker = ".", alpha = 0.5, color = colors[j])
  ax[0].text(m[2] / 1e3, m[1], m[0].replace(" ", "\n"), ha = "center", va = "center", fontsize = 3)


# Plot avg slope
for slope in [4, 5, 6, 7, 8, 9, 10]:
    ax[0].plot((0, 100), (0, slope * 1000), color = [0.8, 0.8, 0.8], linestyle = ":", lw = 1, zorder = 0)
    
    R = 7
    
    ax[0].text(R * np.cos(np.arctan(slope / 100)),  \
            1000 * R * np.sin(np.arctan(slope / 100)), str(slope) + " %", fontsize = 6,\
                color = [0.5, 0.5, 0.5], ha = "center", va = "center")
ax[0].set_xlim(0.0, 40.0)
ax[0].set_ylim(0.0, 2000)
ax[0].set_xlabel("Longueur (km)")
ax[0].set_ylabel("Dénivelé (m)")


# Plot difficulty index sorted
myStats_sorted = sorted(myStats, key = lambda x: x[4], reverse = False)


for j, m in enumerate(myStats_sorted):
    ax[1].plot((0, m[4]), (j, j), lw = 5)
    ax[1].text(180, j, m[0], fontsize = 6, va = "center")

ax[1].set_title("Score difficulté")
ax[1].set_xlim(0.0, 300)

fig.tight_layout()
fig.savefig("./figs/stats.png", dpi = 300)














 