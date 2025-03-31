import streamlit as st
import rasterio as rio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap
import contextily as ctx

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
        if 'RCP' in raster_path or 'SSP' in raster_path:
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
rcp_scenarios = ["RCP45", "RCP85"]
ssp_scenarios = ["SSP1", "SSP2", "SSP3", "SSP4", "SSP5"]

historical_time_periods = ["1979_1985", "1992_1997", "2004_2009", "2013_2018"]
rcp_future_time_periods = ["2020_2045", "2045_2074", "2070_2099"]
ssp_future_time_periods = ["2020", "2030", "2040", "2050", "2060", "2070", "2080", "2090", "2100"]

# Mapping between scenarios and raster paths
raster_paths = {
    # Historical data
    "1979_1985": "clipped_raster/1979_1985_clipped.tif",
    "1992_1997": "clipped_raster/1992_1997_clipped.tif",
    "2004_2009": "clipped_raster/2004_2009_clipped.tif",
    "2013_2018": "clipped_raster/2013_2018_clipped.tif",
    
    # RCP scenarios
    "2020_2045_RCP45": "clipped_raster/2020_2045_RCP45_clipped.tif",
    "2020_2045_RCP85": "clipped_raster/2020_2045_RCP85_clipped.tif",
    "2045_2074_RCP45": "clipped_raster/2045_2074_RCP45_clipped.tif",
    "2045_2074_RCP85": "clipped_raster/2045_2074_RCP85_clipped.tif",
    "2070_2099_RCP45": "clipped_raster/2070_2099_RCP45_clipped.tif",
    "2070_2099_RCP85": "clipped_raster/2070_2099_RCP85_clipped.tif",
    
    # SSP scenarios
    "SSP1_2020": "clipped_raster/clipped_global_SSP1_2020.tif",
    "SSP1_2030": "clipped_raster/clipped_global_SSP1_2030.tif",
    "SSP1_2040": "clipped_raster/clipped_global_SSP1_2040.tif",
    "SSP1_2050": "clipped_raster/clipped_global_SSP1_2050.tif",
    "SSP1_2060": "clipped_raster/clipped_global_SSP1_2060.tif",
    "SSP1_2070": "clipped_raster/clipped_global_SSP1_2070.tif",
    "SSP1_2080": "clipped_raster/clipped_global_SSP1_2080.tif",
    "SSP1_2090": "clipped_raster/clipped_global_SSP1_2090.tif",
    "SSP1_2100": "clipped_raster/clipped_global_SSP1_2100.tif",

    "SSP2_2020": "clipped_raster/clipped_global_SSP2_2020.tif",
    "SSP2_2030": "clipped_raster/clipped_global_SSP2_2030.tif",
    "SSP2_2040": "clipped_raster/clipped_global_SSP2_2040.tif",
    "SSP2_2050": "clipped_raster/clipped_global_SSP2_2050.tif",
    "SSP2_2060": "clipped_raster/clipped_global_SSP2_2060.tif",
    "SSP2_2070": "clipped_raster/clipped_global_SSP2_2070.tif",
    "SSP2_2080": "clipped_raster/clipped_global_SSP2_2080.tif",
    "SSP2_2090": "clipped_raster/clipped_global_SSP2_2090.tif",
    "SSP2_2100": "clipped_raster/clipped_global_SSP2_2100.tif",

    "SSP3_2020": "clipped_raster/clipped_global_SSP3_2020.tif",
    "SSP3_2030": "clipped_raster/clipped_global_SSP3_2030.tif",
    "SSP3_2040": "clipped_raster/clipped_global_SSP3_2040.tif",
    "SSP3_2050": "clipped_raster/clipped_global_SSP3_2050.tif",
    "SSP3_2060": "clipped_raster/clipped_global_SSP3_2060.tif",
    "SSP3_2070": "clipped_raster/clipped_global_SSP3_2070.tif",
    "SSP3_2080": "clipped_raster/clipped_global_SSP3_2080.tif",
    "SSP3_2090": "clipped_raster/clipped_global_SSP3_2090.tif",
    "SSP3_2100": "clipped_raster/clipped_global_SSP3_2100.tif",

    "SSP4_2020": "clipped_raster/clipped_global_SSP4_2020.tif",
    "SSP4_2030": "clipped_raster/clipped_global_SSP4_2030.tif",
    "SSP4_2040": "clipped_raster/clipped_global_SSP4_2040.tif",
    "SSP4_2050": "clipped_raster/clipped_global_SSP4_2050.tif",
    "SSP4_2060": "clipped_raster/clipped_global_SSP4_2060.tif",
    "SSP4_2070": "clipped_raster/clipped_global_SSP4_2070.tif",
    "SSP4_2080": "clipped_raster/clipped_global_SSP4_2080.tif",
    "SSP4_2090": "clipped_raster/clipped_global_SSP4_2090.tif",
    "SSP4_2100": "clipped_raster/clipped_global_SSP4_2100.tif",

    "SSP5_2020": "clipped_raster/clipped_global_SSP5_2020.tif",
    "SSP5_2030": "clipped_raster/clipped_global_SSP5_2030.tif",
    "SSP5_2040": "clipped_raster/clipped_global_SSP5_2040.tif",
    "SSP5_2050": "clipped_raster/clipped_global_SSP5_2050.tif",
    "SSP5_2060": "clipped_raster/clipped_global_SSP5_2060.tif",
    "SSP5_2070": "clipped_raster/clipped_global_SSP5_2070.tif",
    "SSP5_2080": "clipped_raster/clipped_global_SSP5_2080.tif",
    "SSP5_2090": "clipped_raster/clipped_global_SSP5_2090.tif",
    "SSP5_2100": "clipped_raster/clipped_global_SSP5_2100.tif",
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

def display_raster_RCP(raster_file, selected_scenario=None, time_period=None):
    """Function to display a land cover raster"""
    with rio.open(raster_file) as src:
        land_cover = src.read(1)
        if selected_scenario is not None:
            land_cover[land_cover<=0] = np.nan
            land_cover[(land_cover>14) & (land_cover<24)] = 15
            land_cover[land_cover>=24] = 16
        else:
            land_cover = adapt_raster(land_cover)
            land_cover[land_cover==0] = np.nan  

        # Set up colors and visualization
        unique_classes = np.unique(list(land_cover_colors.keys()))
        color_list = [land_cover_colors.get(cls, (0, 0, 0, 1)) for cls in unique_classes]
        cmap = mcolors.ListedColormap([color[:3] for color in color_list])  # Remove alpha
        norm = mcolors.BoundaryNorm(unique_classes.tolist() + [max(unique_classes) + 1], cmap.N)

        # Create figure and plot raster
        fig, ax = plt.subplots(figsize=(10, 8))
        img = ax.imshow(land_cover, cmap=cmap, norm=norm, extent=[src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top], zorder=2, alpha=0.7)
        ctx.add_basemap(ax, crs='epsg:2056', attribution=1, zorder=1)

        # Set title
        title = time_period
        if selected_scenario:
            title = f"{selected_scenario} - {time_period}"
        ax.set_title(title)
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
        
        return fig
    
def display_raster_SSP(raster_file, selected_scenario=None, time_period=None):
    print(raster_file)
    with rio.open(raster_file) as src:
        land_cover = src.read(1)
        crs= src.crs

    # Define colors: transparent, light blue, red
    colors = [(1, 1, 1, 0),  # Transparent for other values
            (0.678, 0.847, 0.902, 1),  # Light blue for 1 (RGB for lightblue)
            (1, 0, 0, 1)]  # Red for 2 (RGB for red)

    # Create the custom colormap
    cmap = ListedColormap(colors)

    # Normalize to cover the range of values
    norm = plt.Normalize(vmin=0, vmax=2)


    fig, ax = plt.subplots(figsize=(10, 8))
    img = ax.imshow(land_cover, cmap=cmap, norm=norm, extent=[src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top], zorder=2, alpha=0.7)
    ctx.add_basemap(ax, crs=crs, attribution=1, zorder=1)

    title = time_period
    if selected_scenario:
        title = f"{selected_scenario} - {time_period}"
    ax.set_title(title)
    ax.axis("off")

    return fig

def show_transition_analysis(scenario_type, available_rasters):
    """Function to show transition analysis interface"""
    st.subheader(f"{scenario_type} Transition Analysis")
    
    # Allow multiple selections for source land cover classes
    lc_sources = st.multiselect(
        "Select source land cover class(es):",
        list(land_cover_labels.values()),
        default=[list(land_cover_labels.values())[0]]
    )
    
    lc_target = st.selectbox("Select target land cover class:", list(land_cover_labels.values()))
    
    # Filter raster options based on scenario type
    filtered_rasters = ["1979_1985", "1992_1997", "2004_2009", "2013_2018"]  # Always include historical
    filtered_rasters.extend([r for r in available_rasters if r in raster_paths.keys()])
    
    raster1 = st.selectbox("Select first raster:", filtered_rasters, index=0)
    raster2 = st.selectbox("Select second raster:", filtered_rasters, index=1)

    if not lc_sources or raster1 == raster2:
        st.error("Please select at least one source class and ensure different raster selections.")
    else:
        # Convert selected labels to land cover class IDs
        lc_source_ids = [list(land_cover_labels.keys())[list(land_cover_labels.values()).index(lc)] for lc in lc_sources]
        lc_target_id = list(land_cover_labels.keys())[list(land_cover_labels.values()).index(lc_target)]

        # Compute transition map
        transition, map_extent, crs = transitions_calc(
            raster_paths[raster1], raster_paths[raster2], lc_source_ids, lc_target_id
        )

        # Generate visualization
        fig = transition_viz(transition, lc_sources, lc_target, map_extent, crs)
        st.pyplot(fig)

        # Explanation text
        st.write(f"Areas transitioning from **{', '.join(lc_sources)}** to **{lc_target}** are highlighted.")

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Land Cover Scenario Viewer")

# Main tab selection - RCP vs SSP
tab_rcp, tab_ssp = st.tabs(["RCP Scenarios", "SSP Scenarios"])

# RCP Tab
with tab_rcp:
    # Create subtabs for scenario viewing and transition analysis
    rcp_view_tab, rcp_transition_tab = st.tabs(["View Scenarios", "Transition Analysis"])
    with rcp_view_tab:
        st.header("RCP Climate Scenarios")
        col1, col2 = st.columns(2)
        with col1:
            rcp_time_period = st.radio("Select Time Period:", historical_time_periods+rcp_future_time_periods)
        with col2:
            rcp_scenario = st.radio("Select RCP Scenario:", rcp_scenarios)
        
        raster_key = f"{rcp_time_period}_{rcp_scenario}"
        if raster_key in raster_paths:
            fig = display_raster_RCP(raster_paths[raster_key], selected_scenario=rcp_scenario, time_period=rcp_time_period)
            st.pyplot(fig)
        else:
            st.error("Raster file not found for the selected scenario and time period.")
    
    with rcp_transition_tab:
        # Create a list of all RCP raster keys
        rcp_rasters = [f"{period}_{scenario}" for period in rcp_future_time_periods for scenario in rcp_scenarios]
        show_transition_analysis("RCP", rcp_rasters)

# SSP Tab
with tab_ssp:
    # Create subtabs for scenario viewing and transition analysis
    ssp_view_tab, ssp_transition_tab = st.tabs(["View Scenarios", "Transition Analysis"])
    
    with ssp_view_tab:
        
        st.header("SSP Climate Scenarios")
        col1_ssp, col2_ssp = st.columns(2)
        with col1_ssp:
            ssp_time_period = st.radio("Select Time Period:", ssp_future_time_periods)
        with col2_ssp:
            ssp_scenario = st.radio("Select SSP Scenario:", ssp_scenarios)
        
        raster_key = f"{ssp_scenario}_{ssp_time_period}"
        if raster_key in raster_paths:
            fig = display_raster_SSP(raster_paths[raster_key], selected_scenario=ssp_scenario, time_period=ssp_time_period)
            st.pyplot(fig)
        else:
            st.error(f"Raster file {raster_paths[raster_key]} not found for the selected scenario and time period.")
    
"""    with ssp_transition_tab:
        # Create a list of all SSP raster keys
        ssp_rasters = [f"{period}_{scenario}" for period in ssp_future_time_periods for scenario in ssp_scenarios]
        show_transition_analysis("SSP", ssp_rasters)"""