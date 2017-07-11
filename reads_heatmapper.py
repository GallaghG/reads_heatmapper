import pandas as pd
import os

#heatmap vis imports
#bokeh imports
from bokeh.io import output_notebook
from bokeh.io import save
from bokeh.io import show

from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LinearColorMapper,
    BasicTicker,
    PrintfTickFormatter,
    ColorBar
)
from bokeh.palettes import brewer
#from bokeh.core.properties import Enum

from bokeh.plotting import figure
from math import pi


def file_import(directory):
    combined_df=pd.DataFrame()
    all_run_ID=[]
    for filename in os.listdir(directory):
            if filename.endswith('mapping.csv'):  #find the associated mapping.csv files
                runID=str(filename.split("_L001")[0])
                #all_run_ID.append(runID)
                new_df = pd.read_csv(os.path.join(directory, filename),names=['Length', 'Read_Count' , 'Ref_ID', 'Strain', 'Virus'])
                new_df['RunID']=runID
                new_df.drop([0], axis=0, inplace=True)
                combined_df = combined_df.append(new_df)
    combined_df['Read_Count']=pd.to_numeric(combined_df['Read_Count'])
    
    return combined_df 

def heatmap_vis(combined_df):
    #rearrange and sort the data
    combined_df['Barcode']=combined_df['RunID'].apply(lambda x: re.split("[-_]+",x)[3])
    combined_df.sort_values(by=['Barcode'],axis=0)
    
    #prepare the colorbar scale
    min_reads = combined_df['Read_Count'].min()
    max_reads = combined_df['Read_Count'].max()
    stdev_reads = combined_df['Read_Count'].std()
    mapper = LinearColorMapper(brewer['RdGy'][10], low=min_reads, high=max_reads)
    
    
    #prepare variables for construction of the heatmap
    refID = list(combined_df['Ref_ID'].unique())
    runID = list(combined_df['RunID'].unique())
    source = ColumnDataSource(combined_df)
    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
    
    p = figure(title= directory.split('\\')[-1],
           x_range=runID, y_range=refID,
           x_axis_location="above", plot_width=900, plot_height=400,
           tools=TOOLS, toolbar_location='below')

    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.yaxis.major_label_text_font_size = "10pt"
    p.yaxis.major_label_text_font_size = "8pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = pi / 5


    p.rect(x="RunID", y="Ref_ID", width=1, height=1,
       source=source,
       fill_color={'field': 'Read_Count', 'transform': mapper},
       line_color=None)


    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="7pt",
                     ticker=BasicTicker(desired_num_ticks=10),
                     formatter=PrintfTickFormatter(format="%e"),
                     label_standoff=6, border_line_color=None, location=(0, 0),
                    major_tick_line_color=None, 
                     major_label_text_baseline='bottom')
    p.add_layout(color_bar, 'right')

    p.select_one(HoverTool).tooltips = [
        ('reads', '@Read_Count'),
        ('runID', '@RunID'),
        ('refID', '@Ref_ID'),
        ('virus', '@Virus'), 
        ('strain', '@Strain')]
    
    return(p)
    

    
directory = input('What is the analysis folder path? ')

combined_df = file_import(directory)
show(heatmap_vis(combined_df))
