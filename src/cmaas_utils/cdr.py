# region CDR Schema
import cdr_schemas.common
from cdr_schemas.map_results import MapResults
from cdr_schemas.feature_results import FeatureResults
from typing import List

from .types import CMAAS_Map, MapUnit, MapUnitType, MapUnitSegmentation, Provenance, GeoReference

# region CDR Common
def importMapFromCDR(cdr_results: MapResults, map_image=None) -> CMAAS_Map:
    """Imports a CDR map results object to a CMAAS map object."""
    
    map_data = CMAAS_Map(name=cdr_results.cog_id, cog_id=cdr_results.cog_id)
    map_data.image = map_image
    # Georeferencing
    if len(cdr_results.georef_results) > 0:
        # Just using the first Georef result as idk how to determine which one is the best
        map_data.georef = _build_geo_ref_from_CDR(cdr_results.georef_results[0])

    # Legend
    

    # Layout
    
    
def _build_geo_ref_from_CDR() -> GeoReference:
    # TODO: Implement geoeref loading
    return None

def exportMapToCDR(map_data: CMAAS_Map, cog_id:str='', system:str='UIUC', system_version:str='0.1') -> FeatureResults:
    """Exports CMAAS map object to a CDR feature results object."""
    point_segmentations = []
    for feature in map_data.legend.features:
        if feature.type == MapUnitType.POINT:
            point_segmentations.append(_build_CDR_point_feature(feature, map_data.legend.provenance))
    polygon_segmentations = []
    for feature in map_data.legend.features:
        if feature.type == MapUnitType.POLYGON:
            polygon_segmentations.append(_build_CDR_poly_feature(feature, map_data.legend.provenance))
    return FeatureResults(cog_id=cog_id, system=system, system_version=system_version, point_feature_results=point_segmentations, polygon_feature_results=polygon_segmentations)

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
        name=feature.label if feature.label is not None else "",
        abbreviation=feature.abbreviation if feature.abbreviation is not None else "",
        description=feature.description if feature.description is not None else "",
        legend_contour=feature.bounding_box if feature.bounding_box is not None else [],
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
        label=feature.label if feature.label is not None else "",
        abbreviation=feature.abbreviation if feature.abbreviation is not None else "",
        description=feature.description if feature.description is not None else "",
        legend_contour=feature.bounding_box if feature.bounding_box is not None else [],
        color=feature.color if feature.color is not None else "",
        pattern=feature.pattern if feature.pattern is not None else "",
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
