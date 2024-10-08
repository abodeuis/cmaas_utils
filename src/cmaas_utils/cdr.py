# region CDR Schema
import numpy as np
import cdr_schemas.common
from cdr_schemas.area_extraction import AreaType
from cdr_schemas.map_results import MapResults
from cdr_schemas.feature_results import FeatureResults
from typing import List

from .types import CMAAS_Map, Layout, MapUnit, MapUnitType, MapUnitSegmentation, Provenance, GeoReference

# region CDR Common
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

def importCDRFeatureResults(cdr_results: FeatureResults) -> CMAAS_Map:
    """Imports a CDR feature results object to a CMAAS map object."""
    # Only importing area_extraction currently
    map_data = CMAAS_Map(name=cdr_results.cog_id, cog_id=cdr_results.cog_id)
    # Layout
    map_data.layout = Layout(provenance=Provenance(name=cdr_results.system, version=cdr_results.system_version))
    for ae in cdr_results.cog_area_extractions:
        if ae.category == AreaType.Map_Area:
            map_data.layout.map = np.array(ae.coordinates).astype(int)
        if ae.category == AreaType.Polygon_Legend_Area:
            map_data.layout.polygon_legend = np.array(ae.coordinates).astype(int)
        if ae.category == AreaType.Line_Point_Legend_Area:
            map_data.layout.line_legend = np.array(ae.coordinates).astype(int)
            map_data.layout.point_legend = np.array(ae.coordinates).astype(int)
        if ae.category == AreaType.Point_Legend_Area:
            map_data.layout.point_legend = np.array(ae.coordinates).astype(int)
        if ae.category == AreaType.CrossSection:
            map_data.layout.cross_section = np.array(ae.coordinates).astype(int)
        if ae.category == AreaType.Correlation_Diagram:
            map_data.layout.correlation_diagram = np.array(ae.coordinates).astype(int)
    return map_data
# endregion Import CDR data

# region Export CDR Point
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
        # legend_contour=feature.label_bbox if feature.label_bbox is not None else [],
        legend_bbox=[*feature.label_bbox[0], *feature.label_bbox[1]] if feature.label_bbox is not None else [],
        point_features=point_collection)
    return point_feature

def _build_CDR_point_feature_collection(segmentation: MapUnitSegmentation) -> PointFeatureCollection:
    # TODO : Just disabling this as we don't expect to be exporting point feature geometry to the CDR, and i would have to fix it to work with the new shapely format
    # point_features = []
    # for point in segmentation.geometry:
    #     for coord in point:
    #         point_features.append(
    #             PointFeature(
    #                 id='None',
    #                 geometry=_build_CDR_point(coord),
    #                 properties=_build_CDR_point_property(segmentation.provenance)
    #             )
    #         )
    
    return PointFeatureCollection(features=point_features)

def _build_CDR_point(geometry: List[float]) -> Point:
    return Point(coordinates=geometry)

def _build_CDR_point_property(provenance: Provenance) -> PointProperties:
    return PointProperties(
        model=provenance.name,
        model_version=provenance.version)
# endregion Export CDR Point

# region Export CDR Polygon
from cdr_schemas.features.polygon_features import PolygonLegendAndFeaturesResult, PolygonFeatureCollection, PolygonFeature, Polygon, PolygonProperties
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
        # legend_contour=feature.label_bbox if feature.label_bbox is not None else [],
        legend_bbox=[*feature.label_bbox[0], *feature.label_bbox[1]] if feature.label_bbox is not None else [],
        color=feature.color if feature.color is not None else "",
        pattern=feature.pattern if feature.pattern is not None else "",
        polygon_features=poly_collection,
        map_unit=[])
    return poly_feature

def _build_CDR_poly_feature_collection(segmentation: MapUnitSegmentation) -> PolygonFeatureCollection:
    poly_features = []
    for polygon in segmentation.geometry:
        # Change Shapely geometries to CDR Format
        poly_geometry = []
        poly_geometry.append([[*point] for point in polygon.exterior.coords])
        for interior in polygon.interiors:
            poly_geometry.append([[*point] for point in interior.coords])
        poly_features.append(
            PolygonFeature(
                id='None',
                geometry=_build_CDR_polygon(poly_geometry), 
                properties=_build_CDR_polygon_property(segmentation.provenance)
            )
        )
    
    return PolygonFeatureCollection(features=poly_features)

def _build_CDR_polygon(geometry: List[List[List[float]]]) -> Polygon:
    return Polygon(coordinates=geometry)

def _build_CDR_polygon_property(provenance: Provenance) -> PolygonProperties:
    return PolygonProperties(model=provenance.name, model_version=provenance.version)  
# endregion Export CDR Polygon
