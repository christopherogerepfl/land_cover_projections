import streamlit as st
import geopandas as gpd
import rasterio as rio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import matplotlib.patches as mpatches
import contextily as ctx
import pandas as pd
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
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
rcp_ssp_scenarios = ["SSP1-RCP2.6", "SSP2-RCP4.5", "SSP3-RPC7.0", "SSP4-RCP3.4", "SSP4-RCP6.0", "SSP5-RCP3.4", "SSP5-RCP8.5"]

historical_time_periods = ["1979_1985", "1992_1997", "2004_2009", "2013_2018"]
rcp_future_time_periods = ["2020_2045", "2045_2074", "2070_2099"]
ssp_future_time_periods = ["2020", "2030", "2040", "2050", "2060", "2070", "2080", "2090", "2100"]
rcpssp_future_time_periods = ["2020", "2025", "2030","2035", "2040", "2045", "2050", "2055","2060","2065",
                               "2070", "2075","2080", "2085","2090", "2095","2100"]

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

raster_paths_rcpssp = {f"{time_period}_{scenario}": f"clipped_raster/clipped_{scenario}_gISA_{time_period}_1km.tif"
                for time_period in rcpssp_future_time_periods for scenario in rcp_ssp_scenarios}

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
            (1, 1, 1, 0),  # Light blue for 1 (RGB for lightblue)
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

    
    # Add legend
    red_patch = mpatches.Patch(color='red', label='Urban')
    ax.legend(handles=[red_patch], loc='lower left', frameon=True)

    return fig

def display_raster_rcpssp(raster_file, selected_scenario=None, time_period=None):
    print(raster_file)
    with rio.open(raster_file) as src:
        land_cover = src.read(1)
        crs = src.crs
        bounds = src.bounds

    # Create a colormap from transparent -> yellow -> orange -> red
    colors = [
        (1, 1, 1, 0),        # 0: Fully transparent
        (1, 1, 0, 1),        # ~33: Yellow
        (1, 0.65, 0, 1),     # ~66: Orange
        (1, 0, 0, 1),        # 100: Red
    ]
    
    cmap = LinearSegmentedColormap.from_list("custom_colormap", colors, N=256)

    # Normalize between 0 and 100
    norm = plt.Normalize(vmin=0, vmax=100)

    fig, ax = plt.subplots(figsize=(10, 8))
    img = ax.imshow(
        land_cover,
        cmap=cmap,
        norm=norm,
        extent=[bounds.left, bounds.right, bounds.bottom, bounds.top],
        zorder=2
    )
    
    ctx.add_basemap(ax, crs=crs, attribution=1, zorder=1)

    title = time_period
    if selected_scenario:
        title = f"{selected_scenario} - {time_period}"
    ax.set_title(title)
    ax.axis("off")

    cbar = fig.colorbar(img, ax=ax, orientation='horizontal', fraction=0.046, pad=0.04)
    cbar.set_label('Percentage of impervious surface area')
    cbar.set_ticks([0, 25, 50, 75, 100])
    cbar.set_ticklabels(['0%', '25%', '50%', '75%', '100%'])


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

def show_transition_analysis_ssp(scenario_type, available_rasters):
    """Function to show urban transition analysis interface (1 = non-urban, 2 = urban)"""
    st.subheader(f"{scenario_type} Urban Transition Analysis")

    # Filter raster options (historical + scenario)
    filtered_rasters = []
    filtered_rasters.extend([r for r in available_rasters if r in raster_paths.keys()])

    # Raster selections
    raster1 = st.selectbox("Select earlier raster:", filtered_rasters, index=0)
    raster2 = st.selectbox("Select later raster:", filtered_rasters, index=1)

    if raster1 == raster2:
        st.error("Please select two different rasters.")
    else:
        # Load both rasters
        with rio.open(raster_paths[raster1]) as src1:
            data1 = src1.read(1)
            bounds = src1.bounds
            crs = src1.crs

        with rio.open(raster_paths[raster2]) as src2:
            data2 = src2.read(1)

        # Identify transitions
        new_urban = np.logical_and(data1 != 2 , data2 == 2)
        old_urban = np.logical_and(data1 == 2, data2 == 2)
        # Optionally: lost urban → other
        # lost_urban = np.logical_and(data1 == 2, data2 == 1)

        # Create a display map
        transition_map = np.zeros_like(data1)
        transition_map[old_urban] = 1
        transition_map[new_urban] = 2
        # transition_map[lost_urban] = 3  # Optional

        # Colormap: 0 = transparent, 1 = old urban (red), 2 = new urban (orange)
        cmap = ListedColormap([
            (1, 1, 1, 0),        # 0: Transparent
            (1, 0, 0, 1),        # 1: Old urban - Red
            (1, 0.5, 0, 1),      # 2: New urban - Orange
        ])

        fig, ax = plt.subplots(figsize=(10, 8))
        img = ax.imshow(
            transition_map,
            cmap=cmap,
            extent=[bounds.left, bounds.right, bounds.bottom, bounds.top],
            zorder=2
        )
        ctx.add_basemap(ax, crs=crs, attribution=1, zorder=1)
        ax.set_title(f"Urban Transition: {raster1} → {raster2}")
        ax.axis("off")

        # Legend
        red_patch = mpatches.Patch(color='red', label='Stable urban')
        orange_patch = mpatches.Patch(color='orange', label='New urban')
        ax.legend(handles=[red_patch, orange_patch], loc='lower left', frameon=True)

        st.pyplot(fig)
        st.write(f"**New urban areas** (orange) are where land changed from non-urban to urban between {raster1} and {raster2}.")
        st.write("**Stable urban areas** (red) remained urban in both time periods.")

def show_transition_analysis_rcpssp(scenario_type, available_rasters):
    """Visualize urban transition based on urban percentage rasters (0-100%)"""
    st.subheader(f"{scenario_type} Urban % Transition Analysis")

    # Raster options (historical + scenario)
    filtered_rasters = []
    filtered_rasters.extend([r for r in available_rasters if r in raster_paths_rcpssp.keys()])

    # Raster selections
    raster1 = st.selectbox("Select earlier raster:", filtered_rasters, index=0, key=',kdo,fze')
    raster2 = st.selectbox("Select later raster:", filtered_rasters, index=1, key=',ocdzni')

    if raster1 == raster2:
        st.error("Please select two different rasters.")
    else:
        # Load raster data
        with rio.open(raster_paths_rcpssp[raster1]) as src1:
            data1 = src1.read(1).astype(float)
            bounds = src1.bounds
            crs = src1.crs

        with rio.open(raster_paths_rcpssp[raster2]) as src2:
            data2 = src2.read(1).astype(float)

        # Calculate change in urban %
        delta = data2 - data1  # positive = urban increase

        # Visualization setup
        # We'll use a diverging colormap: blue (decrease), white (no change), red (increase)
        cmap = LinearSegmentedColormap.from_list("urban_change", [
            (0, 1, 1, 0),     # White - no change
            (1, 1, 0, 1),        # ~33: Yellow
            (1, 0.65, 0, 1),     # ~66: Orange
            (1, 0, 0, 1)      # Red 
        ])

        # Center at 0, clip changes to avoid outlier stretch
        max_abs_change = np.nanpercentile(np.abs(delta), 99)
        norm = plt.Normalize(vmin=0, vmax=max_abs_change)

        fig, ax = plt.subplots(figsize=(10, 8))
        img = ax.imshow(delta, cmap=cmap, norm=norm,
                        extent=[bounds.left, bounds.right, bounds.bottom, bounds.top],
                        zorder=2)
        ctx.add_basemap(ax, crs=crs, attribution=1, zorder=1)
        ax.set_title(f"Urban % Change: {raster1} → {raster2}")
        ax.axis("off")

        # Colorbar
        cbar = fig.colorbar(img, ax=ax, orientation='horizontal', fraction=0.046, pad=0.04)
        cbar.set_label('Change in impervious surface area (%)')
        cbar.set_ticks([0, max_abs_change])
        cbar.set_ticklabels(["0%", f"+{int(max_abs_change)}%"])

        st.pyplot(fig)
        st.write(f"**Red areas** show increased urbanization between {raster1} and {raster2}.")
        st.write("**Blue areas** show decreased urbanization. **White areas** stayed about the same.")

def plot_viz_survey(geodf, col_name):
    fig, ax = plt.subplots(1, 2, figsize=(15, 6))
    fig.subplots_adjust(right=0.85)
    cmap = 'viridis'
    norm = Normalize(vmin=0, vmax=0.6)  # 0 to 1 because values are in fraction
    geodf_1 = geodf[geodf['canton'].isin(['Gros-de-Vaud', 'Lausanne','Lavaux-Oron','Morges', 'Ouest lausannois'])]
    geodf_1.plot(column = col_name, ax = ax[0], cmap=cmap, norm=norm, alpha=0.7)

    geodf_1.apply(lambda x: ax[0].annotate(text=x[col_name], xy=x.geometry.centroid.coords[0], ha='center', color = "black"), axis=1)
    ctx.add_basemap(ax = ax[0], crs='epsg:2056', attribution=1)
    ax[0].set_axis_off()
    ax[0].set_title('Absolute percentage preference in infrastructure - Lausanne and neighbors')

    geodf.set_index('canton')[col_name].plot(kind='bar',ax=ax[1])
    for p in ax[1].patches:
        ax[1].annotate(f"{p.get_height():.2f}",
                       (p.get_x() + p.get_width() / 2., p.get_height()),
                       ha='center', va='center',
                       xytext=(0, 10),
                       textcoords='offset points')
        

    plt.xticks(rotation=45)
    ax[1].yaxis.set_visible(False)
    ax[1].set_title("Absolute percentage preference in infrastructure - Vaud")
    return fig

from mpl_toolkits.axes_grid1 import make_axes_locatable

def plot_preferred_infra(geodf, col_names):
    # Create a new GeoDataFrame for the preferred infrastructure
    preferred_gdf = geodf.copy()
    preferred_gdf['preferred_infra'] = geodf[col_names].idxmax(axis=1)
    preferred_gdf['preferred_percentage'] = geodf[col_names].max(axis=1)

    fig, ax = plt.subplots(1, 1, figsize=(5, 5))
    cmap = 'viridis'
    norm = Normalize(vmin=0, vmax=0.6)  # 0 to 1 because values are in fraction
    geodf_1 = preferred_gdf[preferred_gdf['canton'].isin(['Gros-de-Vaud', 'Lausanne', 'Lavaux-Oron', 'Morges', 'Ouest lausannois'])]
    plot = geodf_1.plot(column='preferred_percentage', cmap=cmap, norm=norm, alpha=0.7, ax=ax)
    geodf_1.apply(lambda x: ax.annotate(text=f"{x['preferred_infra']} ({x['preferred_percentage']:.2f})",
                                        xy=x.geometry.centroid.coords[0], ha='center', color="black", fontsize=5), axis=1)

    ctx.add_basemap(ax=ax, crs='epsg:2056', attribution=1)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.1)
    plt.colorbar(plot.get_children()[0], cax=cax)

    ax.set_axis_off()
    ax.set_title('Preferred infrastructure - Lausanne and neighbors', fontsize=8)
    return fig

# Streamlit UI  
st.set_page_config(layout="wide")
st.title("Land Cover Scenario Viewer")

# Main tab selection - RCP vs SSP
tab_rcp, tab_ssp, tab_rcp_ssp, tab_survey = st.tabs(["RCP Scenarios", "SSP (shared spatio-temporal pathways) Scenarios", "RCP-SSP Scenarios", "Survey results"])

# RCP Tab
with tab_rcp:
    # Create subtabs for scenario viewing and transition analysis
    # add text and link for the paper
    st.markdown("https://www.nature.com/articles/s41597-024-03055-z")
    
    rcp_view_tab, rcp_transition_tab = st.tabs(["View Scenarios", "Transition Analysis"])
    with rcp_view_tab:
        st.header("RCP Climate Scenarios")
        col1, col2 = st.columns(2)
        with col1:
            rcp_time_period = st.radio("Select Time Period:", historical_time_periods+rcp_future_time_periods)
        with col2:
            rcp_scenario = st.radio("Select RCP Scenario:", rcp_scenarios)
        if int(rcp_time_period.split('_')[-1]) < 2020:
            raster_key = f"{rcp_time_period}"
            rcp_scenario=None
        else:
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
    st.markdown("https://www.nature.com/articles/s41467-020-14386-x")
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
    
    with ssp_transition_tab:
        # Create a list of all SSP raster keys
        ssp_rasters = [f"{scenario}_{period}" for period in ssp_future_time_periods for scenario in ssp_scenarios]
        show_transition_analysis_ssp("SSP", ssp_rasters)

with tab_rcp_ssp:
        # Create subtabs for scenario viewing and transition analysis
    st.markdown("https://essd.copernicus.org/articles/15/3623/2023/#section5")

    ssp_view_tab, ssp_transition_tab = st.tabs(["View Scenarios", "Transition Analysis"])
    with ssp_view_tab:
        
        st.header("SSP-RCP Climate Scenarios")
        col1_rcpssp, col2_rcpssp,  = st.columns(2)
        with col1_rcpssp:
            rcpssp_time_period = st.radio("Select Time Period:", rcpssp_future_time_periods)
        with col2_rcpssp:
            rcpssp_scenario= st.radio("Select SSP-RCP Scenario:", rcp_ssp_scenarios)
        raster_key = f'{rcpssp_time_period}_{rcpssp_scenario}'
        if raster_key in raster_paths_rcpssp:
            fig = display_raster_rcpssp(raster_paths_rcpssp[raster_key], selected_scenario=rcpssp_scenario, time_period=rcpssp_time_period)
            st.pyplot(fig)
        else:
            st.error(f"Raster file {raster_paths_rcpssp[raster_key]} not found for the selected scenario and time period.")
    with ssp_transition_tab:
        # Create a list of all SSP raster keys
        rcpssp_rasters = [f"{period}_{scenario}" for period in rcpssp_future_time_periods for scenario in rcp_ssp_scenarios]
        show_transition_analysis_rcpssp("SSP", rcpssp_rasters)

with tab_survey:
    infra_file = pd.read_csv('survey/infrastructures.csv')
    percentages = infra_file.drop(columns=['Total Canton Vaud']).set_index('Region').T.reset_index(names=['canton'])
    #percentages = percentages[percentages['canton'].isin(['Gros-de-Vaud', 'Lausanne','Lavaux-Oron','Morges', 'Ouest lausannois'])]
    cols = percentages.drop(columns=['canton']).columns
    for col in cols:
        percentages[col] = round(percentages[col] / 100, 3)  # convert to 0–1 scale

    print(percentages.max())

    # Normalize canton names
    #percentages.loc[percentages["canton"] == 'Ouest Lausannois', "canton"] = "Ouest lausannois"

    admin_borders = gpd.read_file('survey/MN95_CAD_TPR_LAD_MO_DISTRICT.shp')

    # --- Merge geodata with percentages ---
    merged = pd.merge(admin_borders, percentages, left_on='NOM_MIN', right_on='canton', how='right')
    merged = gpd.GeoDataFrame(merged)


with tab_survey:
    infra_file = pd.read_csv('survey/infrastructures.csv')
    percentages = infra_file.drop(columns=['Total Canton Vaud']).set_index('Region').T.reset_index(names=['canton'])
    cols = percentages.drop(columns=['canton']).columns
    for col in cols:
        percentages[col] = round(percentages[col] / 100, 3)  # convert to 0–1 scale

    admin_borders = gpd.read_file('survey/MN95_CAD_TPR_LAD_MO_DISTRICT.shp')

    # --- Merge geodata with percentages ---
    merged = pd.merge(admin_borders, percentages, left_on='NOM_MIN', right_on='canton', how='right')
    merged = gpd.GeoDataFrame(merged)

    # Sub-tab for selecting multiple infrastructures
    sub_tab_single, sub_tab_multiple = st.tabs(["Single Infrastructure", "Multiple Infrastructures"])
    with sub_tab_single:
        selected_col = 'Parc de panneaux solaires'
        selected_col = st.selectbox(label='Type of infrastructure', options = percentages.drop(columns=["canton"]).columns)
        print(merged[selected_col])
        fig = plot_viz_survey(merged, selected_col)
        st.pyplot(fig)
    with sub_tab_multiple:
        selected_cols = st.multiselect(label='Types of infrastructure', options=percentages.drop(columns=["canton"]).columns)

        if selected_cols:
            fig = plot_preferred_infra(merged, selected_cols)
            st.pyplot(fig)
        else:
            st.write("Please select at least one infrastructure.")
