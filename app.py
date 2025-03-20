import streamlit as st
import rasterio as rio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import contextily as ctx

def transitions_calc(raster1, raster2, lc1, lc2):
    """function to outline the transition between two rasters and two land cover types"""

    # Read raster data
    with rio.open(raster1) as src:
        raster1 = src.read(1)
        raster1[(raster1 != lc1) & (raster1 != lc2)] = np.nan
        map_extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
    
    with rio.open(raster2) as src:
        raster2 = src.read(1)
        raster2[(raster2 != lc1) & (raster2 != lc2)] = np.nan

    # Calculate transition
    transition = np.zeros_like(raster1)
    transition[(raster1 == lc1) & (raster2 == lc2)] = 1
    transition[(raster1 == lc2) & (raster2 == lc1)] = -1

    return transition, map_extent

def transition_viz(transition, lc1, lc2, map_extent):
    """function to visualize the transition"""

    # Plot transition
    print(map_extent)
    fig, ax = plt.subplots(figsize=(20, 18))
    ax.imshow(transition, cmap='coolwarm', vmin=-1, vmax=1)
    ax.set_title(f"Transition from {lc1} to {lc2}")
    ax.axis('off')
    plt.tight_layout()
    
    return fig

# Define available scenarios and time periods
scenarios = ["RCP45", "RCP85"]
time_periods = ["2020_2045", "2045_2074", "2070_2099"]

# Mapping between scenarios and raster paths
raster_paths = {
    "2020_2045_RCP45": "clipped_raster/2020_2045_RCP45_clipped.tif",
    "2020_2045_RCP85": "clipped_raster/2020_2045_RCP85_clipped.tif",
    "2045_2074_RCP45": "clipped_raster/2045_2074_RCP45_clipped.tif",
    "2045_2074_RCP85": "clipped_raster/2045_2074_RCP85_clipped.tif",
    "2070_2099_RCP45": "clipped_raster/2070_2099_RCP45_clipped.tif",
    "2070_2099_RCP85": "clipped_raster/2070_2099_RCP85_clipped.tif"
}

# Load color mapping from file
color_file_path = "Visualization/ColourPalette.txt"
land_cover_colors = {}
land_cover_labels = {}

with open(color_file_path, 'r') as file:
    for line in file:
        parts = line.strip().split(',')
        if len(parts) >= 6:
            class_id = int(parts[0])
            r, g, b, a = float(parts[1])/255, float(parts[2])/255, float(parts[3])/255, float(parts[4])/255
            label = ' '.join(parts[5:])
            land_cover_colors[class_id] = (r, g, b, a)
            land_cover_labels[class_id] = label

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Land Cover Scenario Viewer")

# Layout division
scenarios_col, transition_col = st.columns(2)

with scenarios_col:
    st.header("Land Cover Scenarios")
    selected_scenario = st.radio("Select Climate Scenario:", scenarios)
    time_period = st.radio("Select Time Period:",time_periods)
    raster_key = f"{time_period}_{selected_scenario}"

    if raster_key in raster_paths:
        raster_file = raster_paths[raster_key]
        with rio.open(raster_file) as src:
            land_cover = src.read(1)
            land_cover[land_cover<0] = np.nan
            land_cover[(land_cover>14) & (land_cover<24)] = 15
            land_cover[land_cover>=24] = 16
            
            unique_classes = np.unique(list(land_cover_colors.keys()))
            color_list = [land_cover_colors.get(cls, (0, 0, 0, 1)) for cls in unique_classes]
            cmap = mcolors.ListedColormap([color[:3] for color in color_list])
            
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.imshow(land_cover, cmap=cmap)
            ax.set_title(f"{selected_scenario} - {time_period}")
            ax.axis("off")
            
            st.pyplot(fig)
    else:
        st.error("Raster file not found for the selected scenario and time period.")

with transition_col:
    st.header("Transition Visualization")
    lc1 = st.selectbox("Select first land cover class:", list(land_cover_labels.values()), index=5)
    lc2 = st.selectbox("Select second land cover class:", list(land_cover_labels.values()),index=6)
    raster1 = st.selectbox("Select first raster:", list(raster_paths.keys()), index=0)
    raster2 = st.selectbox("Select second raster:", list(raster_paths.keys()), index=2)
    
    if raster1 == raster2 or lc1 == lc2:
        st.error("Please select different rasters and land cover classes for comparison.")
    else:
        transition, map_extent = transitions_calc(
            raster_paths[raster1], 
            raster_paths[raster2], 
            list(land_cover_labels.keys())[list(land_cover_labels.values()).index(lc1)], 
            list(land_cover_labels.keys())[list(land_cover_labels.values()).index(lc2)]
        )

        fig = transition_viz(transition, lc1, lc2, map_extent)
        st.pyplot(fig)
        st.write(f"Transition from {lc1} to {lc2} is shown in red, while transition from {lc2} to {lc1} is shown in blue.")
