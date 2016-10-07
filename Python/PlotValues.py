import numpy as np
import matplotlib.pyplot as plt
import PIL.Image as Image
import gtk


#Build a graph, spread over a constant interval
#@param yValues     an array containing y values to be plotted
#       form        the form of the line, for example: 'b-' is a continuous blue line
#       legend      the title of the function, for example: 'title' will name the curve title

def plotValues1(xValues, yValues, form, legend):
    fig, ax = plt.subplots()
    ax.plot(xValues, yValues, form, label=legend)


    # Now add the legend with some customizations.
    legend = ax.legend(loc='upper center', shadow=True)

    # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
    frame  = legend.get_frame()
    frame.set_facecolor('0.90')

    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('large')

    for label in legend.get_lines():
        label.set_linewidth(1.5)  # the legend line width
    
##    plt.savefig('plot.png', dpi=350)
##    Image.open('plot.png').resize((600, 300)).save('plot.png')
    img = getGtkImage(fig2img(plt.gcf()))
    plt.clf()
    plt.close()
    return img

def plotValues2(xValues, yValues1,form1, legend1, yValues2, form2, legend2):
    fig, ax = plt.subplots()
    ax.plot(xValues, yValues1, form1, label=legend1)
    ax.plot(xValues, yValues2, form2, label=legend2)


    # Now add the legend with some customizations.
    legend = ax.legend(loc='upper center', shadow=True)

    # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
    frame  = legend.get_frame()
    frame.set_facecolor('0.90')

    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('large')

    for label in legend.get_lines():
        label.set_linewidth(1.5)  # the legend line width
##    plt.savefig('plot.png', dpi=350)
##    Image.open('plot.png').resize((600, 300)).save('plot.png')
    img = getGtkImage(fig2img(plt.gcf()))
    plt.clf()
    plt.close()
    return img

def plotValues3(xValues, yValues1,form1, legend1, yValues2, form2, legend2, yValues3, form3, legend3):
    fig, ax = plt.subplots()
    ax.plot(xValues, yValues1, form1, label=legend1)
    ax.plot(xValues, yValues2, form2, label=legend2)
    ax.plot(xValues, yValues3, form3, label=legend3)


    # Now add the legend with some customizations.
    legend = ax.legend(loc='upper center', shadow=True)

    # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
    frame  = legend.get_frame()
    frame.set_facecolor('0.90')

    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('large')

    for label in legend.get_lines():
        label.set_linewidth(1.5)  # the legend line width
    #plt.savefig('plot.png', dpi=350)
    #Image.open('plot.png').resize((600, 300)).save('plot.png')
    img = getGtkImage(fig2img(plt.gcf()))
    plt.clf()
    plt.close()
    return img
def getGtkImage(img):
    arr = np.array(img)
    return gtk.gdk.pixbuf_new_from_array(arr, gtk.gdk.COLORSPACE_RGB, 8)
#plotValues1(([0]*20), 'b-', 'Verbruik')


def fig2data ( fig ):
    """
    @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    # draw the renderer
    fig.canvas.draw ( )

    # Get the RGBA buffer from the figure
    w,h = fig.canvas.get_width_height()
    buf = np.fromstring ( fig.canvas.tostring_argb(), dtype=np.uint8 )
    buf.shape = ( w, h,4 )

    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = np.roll ( buf, 3, axis = 2 )
    return buf

def fig2img ( fig ):
    """
    @brief Convert a Matplotlib figure to a PIL Image in RGBA format and return it
    @param fig a matplotlib figure
    @return a Python Imaging Library ( PIL ) image
    """
    # put the figure pixmap into a numpy array
    buf = fig2data ( fig )
    w, h, d = buf.shape
    return Image.fromstring( "RGBA", ( w ,h ), buf.tostring( ) )





#plotValues1(([0]*20), 'b-', 'Verbruik')


