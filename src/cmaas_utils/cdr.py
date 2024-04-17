# region CDR Schema
import cdr_schemas.common
from cdr_schemas.feature_results import FeatureResults
from typing import List

from .types import CMAAS_Map, MapUnit, MapUnitType, MapUnitSegmentation, Provenance

# region CDR Common
def export_CMAAS_Map_to_cdr_schema(map_data: CMAAS_Map, cog_id:str='', system:str='UIUC', system_version:str='0.1'):
    point_segmentations = []
    for feature in map_data.legend.features:
        if feature.type == MapUnitType.POINT:
            point_segmentations.append(_build_CDR_point_feature(feature, map_data.legend.provenance))
    polygon_segmentations = []
    for feature in map_data.legend.features:
        if feature.type == MapUnitType.POLYGON:
            polygon_segmentations.append(_build_CDR_poly_feature(feature, map_data.legend.provenance))
    return FeatureResults(cog_id=cog_id, system=system, system_version=system_version, point_feature_results=point_segmentations, polygon_feature_results=polygon_segmentations)

def saveCDRFeatureResults(filepath, feature_result: FeatureResults):
    # Save CDR schema
    with open(filepath, 'w') as fh:
        fh.write(feature_result.model_dump_json())

def _build_CDR_provenance(provenance: Provenance) -> cdr_schemas.common.ModelProvenance:
    return cdr_schemas.common.ModelProvenance(model=provenance.name, model_version=provenance.version)
# endregion CDR Common

# region CDR Point
from cdr_schemas.features.point_features import PointLegendAndFeaturesResult, PointFeatureCollection, PointFeature,  Point, PointProperties
def _build_CDR_point_feature(feature: MapUnit, legend_provenance: Provenance) -> PointLegendAndFeaturesResult:
    if feature.segmentation is not None and feature.segmentation.geometry is not None:
        point_collection = _build_CDR_point_feature_collection(feature.segmentation)
    else:
        point_collection = None
    point_feature = PointLegendAndFeaturesResult(
        id="None",
        legend_provenance=_build_CDR_provenance(legend_provenance),
        name=feature.label,
        abbreviation=feature.abbreviation,
        description=feature.description,
        legend_contour=feature.bounding_box,
        point_features=point_collection)
    return point_feature

def _build_CDR_point_feature_collection(segmentation: MapUnitSegmentation) -> PointFeatureCollection:
    point_features = []
    for point in segmentation.geometry:
        for coord in point:
            point_features.append(PointFeature(
                id='None',
                geometry=_build_CDR_point(coord),
                properties=_build_CDR_point_property(segmentation.provenance)
            ))
    
    return PointFeatureCollection(features=point_features)

def _build_CDR_point(geometry: List[float]) -> Point:
    return Point(coordinates=geometry)

def _build_CDR_point_property(provenance: Provenance) -> PointProperties:
    return PointProperties(
        model=provenance.name,
        model_version=provenance.version)
# endregion CDR Point

# region CDR Polygon
from cdr_schemas.features.polygon_features import PolygonLegendAndFeaturesResult, PolygonFeatureCollection, PolygonFeature, Polygon, PolygonProperty
def _build_CDR_poly_feature(feature: MapUnit, legend_provenance: Provenance) -> PolygonLegendAndFeaturesResult:
    if feature.segmentation is not None and feature.segmentation.geometry is not None:
        poly_collection = _build_CDR_poly_feature_collection(feature.segmentation)
    else:
        poly_collection = None
    poly_feature = PolygonLegendAndFeaturesResult(
        id="None",
        legend_provenance=_build_CDR_provenance(legend_provenance),
        label=feature.label,
        abbreviation=feature.abbreviation,
        description=feature.description,
        legend_contour=feature.bounding_box,
        color=feature.color,
        pattern=feature.pattern,
        polygon_features=poly_collection)
    return poly_feature

def _build_CDR_poly_feature_collection(segmentation: MapUnitSegmentation) -> PolygonFeatureCollection:
    poly_features = []
    for poly in segmentation.geometry:
        poly_features.append(PolygonFeature(
            id='None', 
            geometry=_build_CDR_polygon(poly), 
            properties=_build_CDR_polygon_property(segmentation.provenance)
        ))
    
    return PolygonFeatureCollection(features=poly_features)

def _build_CDR_polygon(geometry: List[List[float]]) -> Polygon:
    return Polygon(coordinates=[geometry])

def _build_CDR_polygon_property(provenance: Provenance) -> PolygonProperty:
    return PolygonProperty(model=provenance.name, model_version=provenance.version)  
# endregion CDR Polygon

# region CDR Schema
from rasterio.features import shapes, sieve 
from shapely.geometry import shape
import numpy as np
# def _build_CDR_polygon(image, id, noise_threshold=10):
#     # Get mask of feature
#     feature_mask = np.zeros_like(image, dtype=np.uint8)
#     feature_mask[image == id] = 1
#     # Remove "noise" from mask by removing pixel groups smaller then the threshold
#     #sieve_img = sieve(feature_mask, noise_threshold, connectivity=4)
#     # Convert mask to vector shapes
#     shape_gen = shapes(feature_mask, connectivity=4)
#     # Only use Filled pixels (1s) for shapes 
#     geometries = [shape(geometry) for geometry, value in shape_gen if value == 1]
#     # Change Shapely geometryies to List(List(List(float)))

#     cdr_geometries = [[[*point] for point in geometry.exterior.coords] for geometry in geometries]
#     tmp = cdr_schemas.features.polygon_features.Polygon(coordinates=cdr_geometries)
#     return tmp

# endregion CDR Schema