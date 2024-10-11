import os
import json
import rasterio
import multiprocessing
import numpy as np
import geopandas as gpd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from .types import AreaBoundary, CMAAS_Map, Layout, Legend, GeoReference, MapUnit, MapUnitType, Provenance
from rasterio.crs import CRS

from cdr_schemas.map_results import MapResults
from cdr_schemas.feature_results import FeatureResults
from pydantic.tools import parse_obj_as
from shapely.affinity import affine_transform

#region Legend
def loadLegendJson(filepath:Path, type_filter:MapUnitType=MapUnitType.ALL()) -> Legend:
    with open(filepath, 'r') as fh:
        json_data = json.load(fh)
    if json_data['version'] in ['5.0.1', '5.0.2']:
        legend = _loadLegacyUSGSLegendJson(filepath, type_filter)
    else:
        legend = parse_obj_as(Legend, json_data)
    return legend

def _loadLegacyUSGSLegendJson(filepath:Path, type_filter:MapUnitType=MapUnitType.ALL()) -> Legend:
    with open(filepath, 'r') as fh:
        json_data = json.load(fh)
    legend = Legend(provenance=Provenance(name='USGS', version='5.0.1'))
    for m in json_data['shapes']:
        # Filter out unwanted map unit types
        unit_type = MapUnitType.from_str(m['label'].split('_')[-1])
        if unit_type not in type_filter:
            continue
        # Remove type encoding from label
        unit_label = m['label']
        unit_label = ' '.join(unit_label.split('_'))
        if unit_type != MapUnitType.UNKNOWN:
            unit_label = ' '.join(unit_label.split(' ')[:-1])
        unit_aliases = None
        if 'aliases' in m:
            unit_aliases = []
            for unit_alias in m['aliases']:
                unit_alias = ' '.join(unit_alias.split('_'))
                if unit_type != MapUnitType.UNKNOWN:
                    unit_alias = ' '.join(unit_alias.split(' ')[:-1])
                unit_aliases.append(unit_alias)
        legend.features.append(MapUnit(label=unit_label, type=unit_type, aliases=unit_aliases, label_bbox=np.array(m['points']).astype(int)))
    return legend

def parallelLoadLegends(filepaths, type_filter:MapUnitType=MapUnitType.ALL(), threads:int=32):
    with ThreadPoolExecutor(max_workers=threads) as executor:
        legends = {}
        for filepath in filepaths:
            map_name = os.path.basename(os.path.splitext(filepath)[0])
            legends[map_name] = executor.submit(loadLegendJson, filepath, type_filter).result()
    return legends
# endregion Legend

# region Layout
def loadLayoutJson(filepath:Path) -> Layout:
    with open(filepath, 'r') as fh:
        layout_version = 1
        try:
            for line in fh:
                json_data = json.loads(line)
                if json_data['name'] == 'segmentation':
                    layout_version = 2
                break
        except:
            layout_version = 1
            pass
        if layout_version == 1:
            layout = _loadLegacyUnchartedLayoutv1Json(filepath)
        elif layout_version == 2:
            layout = _loadLegacyUnchartedLayoutv2Json(filepath)
        else:
            layout = parse_obj_as(Layout, json_data)
    return layout

def _loadLegacyUnchartedLayoutv1Json(filepath:Path) -> Layout:
    layout = Layout(provenance=Provenance(name='Uncharted', version='0.1'))
    with open(filepath, 'r') as fh:
        json_data = json.load(fh)

    for section in json_data:
        bounds = AreaBoundary(geometry=[section['bounds']], confidence=section['confidence'])
        if section['name'] == 'map':
            layout.map.append(bounds)
        elif section['name'] == 'correlation_diagram':
            layout.correlation_diagram.append(bounds)
        elif section['name'] == 'cross_section':
            layout.cross_section.append(bounds)
        elif section['name'] == 'legend_points_lines':
            layout.point_legend.append(bounds)
            layout.line_legend.append(bounds)
        elif section['name'] == 'legend_points':
            layout.point_legend.append(bounds)
        elif section['name'] == 'legend_lines':
            layout.line_legend.append(bounds)
        elif section['name'] == 'legend_polygons':
            layout.polygon_legend.append(bounds)
    return layout

def _loadLegacyUnchartedLayoutv2Json(filepath:Path) -> Layout:
    layout = Layout(provenance=Provenance(name='Uncharted', version='0.2'))
    with open(filepath, 'r') as fh:
        for line in fh:
            json_data = json.loads(line)
            section_name = json_data['model']['field']
            bounds = AreaBoundary(geometry=[json_data['bounds']], confidence=json_data['confidence'])
            if section_name == 'map':
                layout.map.append(bounds)
            elif section_name == 'correlation_diagram':
                layout.correlation_diagram.append(bounds)
            elif section_name == 'cross_section':
                layout.cross_section.append(bounds)
            elif section_name == 'legend_points_lines':
                layout.point_legend.append(bounds)
                layout.line_legend.append(bounds)
            elif section_name == 'legend_points':
                layout.point_legend.append(bounds)
            elif section_name == 'legend_lines':
                layout.line_legend.append(bounds)
            elif section_name == 'legend_polygons':
                layout.polygon_legend.append(bounds)
    return layout

def parallelLoadLayouts(filepaths, threads:int=32):
    with ThreadPoolExecutor(max_workers=threads) as executor:
        layouts = {}
        for filepath in filepaths:
            map_name = os.path.basename(os.path.splitext(filepath)[0])
            layouts[map_name] = executor.submit(loadLayoutJson, filepath).result()
    return layouts
# endregion Layout

# region GeoTiff
def loadGeoTiff(filepath:Path):
    """Load a GeoTiff file. Image is in CHW format. Raises exception if image is not loaded properly. Returns a tuple of the image, crs and transform """
    with rasterio.open(filepath) as fh:
        image = fh.read()
        crs = fh.crs
        transform = fh.transform
    if image is None:
        msg = f'Unknown issue caused "{filepath}" to fail while loading'
        raise Exception(msg)
    
    return image, crs, transform

def saveGeoTiff(filename, image, crs=None, transform=None):
    image = np.array(image[...], ndmin=3)
    with rasterio.open(filename, 'w', driver='GTiff', compress='lzw', height=image.shape[1], width=image.shape[2],
                       count=image.shape[0], dtype=image.dtype, crs=crs, transform=transform) as fh:
        fh.write(image)

def parallelLoadGeoTiffs(filepaths, processes=multiprocessing.cpu_count()): # -> list[tuple(image, crs, transfrom)]:
    """Load a list of filenames in parallel with N processes. Returns a list of images"""
    p=multiprocessing.Pool(processes=processes)
    with multiprocessing.Pool(processes) as p:
        images = p.map(loadGeoTiff, filepaths)

    return images
# endregion GeoTiff

# region CMAAS Map IO
def loadCMAASMapFromFiles(image_path:Path, legend_path:Path=None, layout_path:Path=None, georef_path:Path=None, metadata_path:Path=None) -> CMAAS_Map:
    """Loads a CMAAS Map from its individual file components. Returns a CMAAS_Map object."""
    map_name = os.path.basename(os.path.splitext(image_path)[0])

    # Start Threads
    with ThreadPoolExecutor() as executor:
        img_future = executor.submit(loadGeoTiff, image_path)
        if legend_path is not None:
            lgd_future = executor.submit(loadLegendJson, legend_path)
        if layout_path is not None:
            lay_future = executor.submit(loadLayoutJson, layout_path)
        
        image, crs, transform = img_future.result()
        if legend_path is not None:
            legend = lgd_future.result()
        if layout_path is not None:
            layout = lay_future.result()
        georef = GeoReference(provenance=Provenance(name='GeoTIFF'), crs=crs, transform=transform)
    
    map_data = CMAAS_Map(name=map_name, image=image, georef=georef)
    if legend_path is not None:
        map_data.legend = legend
    if layout_path is not None:
        map_data.layout = layout

    return map_data

def saveGeoPackage(filepath: Path, map_data: CMAAS_Map, coord_type:str='pixel'):
    # Create a GeoDataFrame to store all features
    gdf = gpd.GeoDataFrame()
    
    # Get the crs
    if map_data.georef and map_data.georef.crs:
        crs = map_data.georef.crs
    else:
        crs = CRS.from_epsg(4326)

    # Process each feature in the legend
    for feature in map_data.legend.features:
        if feature.segmentation and feature.segmentation.geometry:
            geometries = feature.segmentation.geometry
            
            # Apply transform
            if map_data.georef and map_data.georef.transform and coord_type == 'georef':
                transform = map_data.georef.transform
                affine_params = [transform.a, transform.b, transform.d, transform.e, transform.xoff, transform.yoff]
                geometries = [affine_transform(geom, affine_params) for geom in geometries]
            
            # Create a GeoDataFrame for this feature    
            gdf = gpd.GeoDataFrame(geometry=geometries, crs=crs)

            # Save to GeoPackage
            gdf.to_file(filepath, layer=feature.label, driver="GPKG")
    
# Deprecating
# def parallelLoadCMASSMapFromFiles(map_files, legend_path=None, layout_path=None, processes : int=multiprocessing.cpu_count()):
#     """Load a list of maps in parallel with N processes. Returns a list of CMASS_Map objects"""
#     # Build argument list
#     map_args = []
#     for file in map_files:
#         map_name = os.path.basename(os.path.splitext(file)[0])
#         lgd_file = None
#         if legend_path is not None:
#             lgd_file = os.path.join(legend_path, f'{map_name}.json')
#             if not os.path.exists(lgd_file):
#                 lgd_file = None
#         lay_file = None
#         if layout_path is not None:
#             lay_file = os.path.join(layout_path, f'{map_name}.json')
#             if not os.path.exists(lay_file):
#                 lay_file = None
#         map_args.append((file, lgd_file, lay_file))

#     # Load all files in parallel
#     with multiprocessing.Pool(processes) as p:
#         results = p.starmap(loadCMAASMapFromFiles, map_args)

#     return results
# endregion CMAAS Map IO

# region CDR IO
def loadCDRMapResults(filepath:Path) -> MapResults:
    """Load a CDR Map Result from a json file. Returns a MapResults object."""
    with open(filepath, 'r') as fh:
        json_data = json.load(fh)
    return parse_obj_as(MapResults, json_data)
    
def loadCDRFeatureResults(filepath:Path) -> FeatureResults:
    """Load a CDR Feature Result from a json file. Returns a FeatureResults object."""
    with open(filepath, 'r') as fh:
        json_data = json.load(fh)
    return parse_obj_as(FeatureResults, json_data)

def saveCDRFeatureResults(filepath, feature_result: FeatureResults):
    """Save a CDR Feature Result to a json file."""
    # Save CDR schema
    with open(filepath, 'w') as fh:
        fh.write(feature_result.model_dump_json())
# endregion CDR IO