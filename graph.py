import os
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import io
from PIL import Image
import config

def get_trend_color(current, next):
    if next > current:
        return 'green' 
    elif next < current:
        return 'red'
    else:
        return 'yellow'

def get_rating_color(rating):
    if rating < 5:
        return 'green'
    elif rating < 8:
        return 'yellow'
    else:
        return 'green'
    
async def rating_vs_bsctype(dates, ratings, bsctype):
    x = np.arange(len(dates))

    cmap = cm.RdYlGn  
    norm = plt.Normalize(min(ratings), max(ratings))

    fig, ax1 = plt.subplots()

    ax1.set_xlabel('Time')
    ax1.set_ylabel('Poop Rating', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.set_xticks(x)
    ax1.set_xticklabels([date.strftime('%m-%d %H:%M') for date in dates], rotation=45)
    ax1.grid(True, axis='x', linestyle='dotted', alpha=0.7)
    
    for i in range(len(x)-1):
        ax1.plot(x[i:i+2], ratings[i:i+2], color='blue', lw=1)
        ax1.scatter(x[i], ratings[i], color=cmap(norm(ratings[i])), s=50, zorder=5)

    ax1.scatter(x[-1], ratings[-1], color=cmap(norm(ratings[-1])), s=50, zorder=5)

    ax2 = ax1.twinx()

    image_path = os.path.join(os.getcwd(), "poopemoji.png")
    image = Image.open(image_path) 
    image_array = np.array(image)
    
    for i in range(len(bsctype)):
        imagebox = OffsetImage(image_array, zoom=0.25, resample=True, dpi_cor=True)
        ab = AnnotationBbox(imagebox, (x[i], bsctype[i]), frameon=False)
        ax2.add_artist(ab)
        ax2.scatter(x[i], bsctype[i], color='brown', marker='s', alpha=0.7)

    ax2.set_ylabel('Bristol Type', color='brown')
    ax2.set_yticks(range(1, 8))
    ax2.tick_params(axis='y', labelcolor='brown')

    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=config.GRAPH_DPI)
    plt.close()
    buffer.seek(0)
    
    return buffer