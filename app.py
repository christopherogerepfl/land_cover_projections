import streamlit as st
import rasterio as rio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import contextily as ctx

import numpy as np

def adapt_raster(old_raster):
    """
    Adapt an old raster to the new classification system.
    :param old_raster: 2D numpy array representing the old raster.
    :return: 2D numpy array with updated class codes.
    """
    # Define the mapping from old class codes to new class codes
    class_mapping = {
        1: 1,  # Industry
        2: 2,  # Building
        3: 15, # Transportation
        4: 3,  # Special urban
        5: 4,  # Urban green
        6: 5,  # Horticulture
        7: 6,  # Arable
        8: 7,  # Grassland
        9: 8,  # Alpine grassland
        10: 9, # Forest
        11: 10, # Brush
        12: 11, # Trees
        13: 16, # Water (standing)
        14: 16, # Water (flowing)
        15: 12, # Unproductive vegetation
        16: 13, # Bare land
        17: 14  # Glacier
    }
    
    # Vectorized mapping of old raster values to new raster values
    vectorized_map = np.vectorize(lambda x: class_mapping.get(x, x))
    new_raster = vectorized_map(old_raster)
    
    return new_raster


def transitions_calc(raster1_path, raster2_path, lc_sources, lc_target):
    """Function to outline the transition from multiple land cover classes to a target class"""

    # Read raster data
    with rio.open(raster1_path) as src:
        raster1 = src.read(1)
        map_extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]

    with rio.open(raster2_path) as src:
        raster2 = src.read(1)

    # Adapt raster values if needed
    def preprocess_raster(raster, raster_path):
        if 'RCP' in raster_path:
            raster[(raster > 14) & (raster < 24)] = 15
            raster[raster >= 24] = 16
        else:
            raster = adapt_raster(raster)
        return raster

    raster1 = preprocess_raster(raster1, raster1_path)
    raster2 = preprocess_raster(raster2, raster2_path)

    # Ensure rasters have the same shape
    min_rows = min(raster1.shape[0], raster2.shape[0])
    min_cols = min(raster1.shape[1], raster2.shape[1])
    raster1 = raster1[-min_rows:, -min_cols:]
    raster2 = raster2[-min_rows:, -min_cols:]

    # Initialize transition map
    transition = np.zeros_like(raster1, dtype=int)

    # Mark transitions from any source class to the target class
    for lc in lc_sources:
        transition[(raster1 == lc) & (raster2 == lc_target)] = 1

    crs = src.crs  # Get coordinate reference system

    return transition, map_extent, crs

def transition_viz(transition, lc_sources, lc_target, map_extent, crs):
    """Function to visualize the transitions"""

    fig, ax = plt.subplots(figsize=(10, 8))
    transition = transition.astype(float)  # Convert to float first
    transition[transition == 0] = np.nan  # Now assign NaN safely

    img = ax.imshow(transition, cmap='coolwarm', extent=map_extent, zorder=2)
    ctx.add_basemap(ax, crs=crs, attribution=False, zorder=1, alpha=0.5)

    ax.set_title(f"Transition from {', '.join(lc_sources)} to {lc_target}")
    ax.axis('off')
    plt.tight_layout()

    return fig

# Define available scenarios and time periods
scenarios = ["RCP45", "RCP85"]
time_periods = ["1979_1985", "1992_1997", "2004_2009", "2013_2018", "2020_2045", "2045_2074", "2070_2099"]

# Mapping between scenarios and raster paths
raster_paths = {
    "1979_1985": "clipped_raster/1979_1985_clipped.tif",
    "1992_1997": "clipped_raster/1992_1997_clipped.tif",
    "2004_2009": "clipped_raster/2004_2009_clipped.tif",
    "2013_2018": "clipped_raster/2013_2018_clipped.tif",
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
    time_period = st.radio("Select Time Period:",time_periods)
    selected_scenario = None
    raster_key = f"{time_period}"


    if int(time_period.split('_')[0]) > 2018: 
        selected_scenario = st.radio("Select Climate Scenario:", scenarios)
        raster_key += f"_{selected_scenario}"


    if raster_key in raster_paths:
        raster_file = raster_paths[raster_key]
        with rio.open(raster_file) as src:
            land_cover = src.read(1)
            if selected_scenario is not None:
                land_cover[land_cover<=0] = np.nan
                land_cover[(land_cover>14) & (land_cover<24)] = 15
                land_cover[land_cover>=24] = 16
            else:
                land_cover = adapt_raster(land_cover)
                land_cover[land_cover==0] = np.nan  

            
            unique_classes = np.unique(list(land_cover_colors.keys()))
            color_list = [land_cover_colors.get(cls, (0, 0, 0, 1)) for cls in unique_classes]
           # Define colormap and normalization
            cmap = mcolors.ListedColormap([color[:3] for color in color_list])  # Remove alpha
            norm = mcolors.BoundaryNorm(unique_classes.tolist() + [max(unique_classes) + 1], cmap.N)

            # Create figure and plot raster
            fig, ax = plt.subplots(figsize=(10, 8))
            img = ax.imshow(land_cover, cmap=cmap, norm=norm, extent=[src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top], zorder=2, alpha=0.7)
            ctx.add_basemap(ax, crs='epsg:2056', attribution=1, zorder=1)
            #scale = ctx.add_scale(ax, at_location=(0.5, 0.05), length=10000, units='m')

            ax.set_title(f"{selected_scenario} - {time_period}")

            #add distance scale
            ax.axis("off")

            # Create a colorbar legend
            ax_legend = fig.add_axes([0.1, 0.1, 0.8, 0.05])  # Position for legend
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])  # Dummy array for colorbar

            cb = plt.colorbar(sm, cax=ax_legend, orientation='horizontal')
            cb.set_ticks(unique_classes+0.5)
            cb.ax.set_xticklabels([land_cover_labels.get(cls, "") for cls in unique_classes], rotation=360-60)

            # Adjust legend appearance
            cb.ax.tick_params(labelsize=8)
            cb.ax.set_title("Land Cover Classes", fontsize=10)
            
            st.pyplot(fig)
    else:
        st.error("Raster file not found for the selected scenario and time period.")

with transition_col:
    # Streamlit UI
    st.header("Multi-Class Transition Visualization")

    
    # Allow multiple selections for source land cover classes
    lc_sources = st.multiselect(
        "Select source land cover class(es):",
        list(land_cover_labels.values()),
        default=[list(land_cover_labels.values())[0]]
    )
    
    lc_target = st.selectbox("Select target land cover class:", list(land_cover_labels.values()))
    
    raster1 = st.selectbox("Select first raster:", list(raster_paths.keys()), index=0)
    raster2 = st.selectbox("Select second raster:", list(raster_paths.keys()), index=1)

    if not lc_sources or raster1 == raster2:
        st.error("Please select at least one source class and ensure different raster selections.")
    else:
        # Convert selected labels to land cover class IDs
        lc_source_ids = [list(land_cover_labels.keys())[list(land_cover_labels.values()).index(lc)] for lc in lc_sources]
        print(lc_source_ids)
        lc_target_id = list(land_cover_labels.keys())[list(land_cover_labels.values()).index(lc_target)]
        print(lc_target_id)

        # Compute transition map
        transition, map_extent, crs = transitions_calc(
            raster_paths[raster1], raster_paths[raster2], lc_source_ids, lc_target_id
        )

        # Generate visualization
        fig = transition_viz(transition, lc_sources, lc_target, map_extent, crs)
        st.pyplot(fig)

        # Explanation text
        st.write(f"Areas transitioning from **{', '.join(lc_sources)}** to **{lc_target}** are highlighted.")