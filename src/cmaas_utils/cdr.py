import cdr_schemas.common
from cdr_schemas.area_extraction import AreaType
from cdr_schemas.feature_results import FeatureResults
from cdr_schemas.cdr_responses.legend_items import LegendItemResponse
from cdr_schemas.cdr_responses.area_extractions import AreaExtractionResponse

from typing import List

from .types import AreaBoundary, CMAAS_Map, Layout, Legend, MapUnit, MapUnitType, MapUnitSegmentation, Provenance

# region CDR Common
def exportMapToCDR(map_data: CMAAS_Map, cog_id:str='', system:str='UIUC', system_version:str='0.1') -> FeatureResults:
    """Exports CMAAS map object to a CDR feature results object."""
    cdr_result = FeatureResults(cog_id=cog_id, system=system, system_version=system_version)
    # Export Map Unit Data (Legend and Segmentation)
    for feature in map_data.legend.features:
        if feature.type == MapUnitType.POINT:
            cdr_result.point_feature_results.append(_build_CDR_point_feature(feature, map_data.legend.provenance))
    for feature in map_data.legend.features:
        if feature.type == MapUnitType.LINE:
            cdr_result.line_feature_results.append(_build_CDR_line_feature(feature, map_data.legend.provenance))
    for feature in map_data.legend.features:
        if feature.type == MapUnitType.POLYGON:
            cdr_result.polygon_feature_results.append(_build_CDR_poly_feature(feature, map_data.legend.provenance))
    return cdr_result

def _build_CDR_provenance(provenance: Provenance) -> cdr_schemas.common.ModelProvenance:
    return cdr_schemas.common.ModelProvenance(model=provenance.name, model_version=provenance.version)
# endregion CDR Common

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
    
    return PointFeatureCollection(features=[])

def _build_CDR_point(geometry: List[float]) -> Point:
    return Point(coordinates=geometry)

def _build_CDR_point_property(provenance: Provenance) -> PointProperties:
    return PointProperties(
        model=provenance.name,
        model_version=provenance.version)
# endregion Export CDR Point

# region Export CDR Line
from cdr_schemas.features.line_features import LineLegendAndFeaturesResult, LineFeatureCollection, LineFeature, Line, LineProperties
def _build_CDR_line_feature(feature: MapUnit, legend_provenance: Provenance) -> LineLegendAndFeaturesResult:
    if feature.segmentation is not None and feature.segmentation.geometry is not None:
        line_collection = _build_CDR_line_feature_collection(feature.segmentation)
    else:
        line_collection = None
    line_feature = LineLegendAndFeaturesResult(
        id="None",
        legend_provenance=_build_CDR_provenance(legend_provenance),
        name=feature.label if feature.label is not None else "",
        abbreviation=feature.abbreviation if feature.abbreviation is not None else "",
        description=feature.description if feature.description is not None else "",
        # legend_contour=feature.label_bbox if feature.label_bbox is not None else [],
        legend_bbox=[*feature.label_bbox[0], *feature.label_bbox[1]] if feature.label_bbox is not None else [],
        line_features=line_collection)
    return line_feature

def _build_CDR_line_feature_collection(segmentation: MapUnitSegmentation) -> LineFeatureCollection:
    line_features = []
    for line in segmentation.geometry:
        line_features.append(
            LineFeature(
                id='None',
                geometry=_build_CDR_line(line),
                properties=_build_CDR_line_property(segmentation.provenance)
            )
        )
    
    return LineFeatureCollection(features=line_features)

def _build_CDR_line(geometry: List[List[float]]) -> Line:
    return Line(coordinates=geometry)

def _build_CDR_line_property(provenance: Provenance) -> LineProperties:
    return LineProperties(
        model=provenance.name,
        model_version=provenance.version)

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

# region Convert CDR to CMAAS
def convert_cdr_feature_results_to_cmaas_map(cdr_results: FeatureResults) -> CMAAS_Map:
    """
    Convert a CDR feature results object to a CMAAS map object. Preseves the provenance, cog_id, legend and layout information. No segmentation or metadata is preserved.
    
    Args:
        cdr_results (FeatureResults): A CDR feature results object.
        
    Returns:
        CMAAS_Map: A CMAAS map object.
    """
    map_data = CMAAS_Map(name=cdr_results.cog_id, cog_id=cdr_results.cog_id)
    # Legend 
    legend = Legend(provenance=Provenance(name=cdr_results.system, version=cdr_results.system_version))
    for point_feature in cdr_results.point_feature_results:
        map_unit = MapUnit(type=MapUnitType.POINT)
        map_unit.label = point_feature.name
        map_unit.abbreviation = point_feature.abbreviation
        map_unit.description = point_feature.description
        map_unit.label_bbox = [point_feature.legend_bbox[0:2], point_feature.legend_bbox[2:4]]
        legend.features.append(map_unit)
    for line_feature in cdr_results.line_feature_results:
        map_unit = MapUnit(type=MapUnitType.LINE)
        map_unit.label = line_feature.name
        map_unit.abbreviation = line_feature.abbreviation
        map_unit.description = line_feature.description
        map_unit.label_bbox = [line_feature.legend_bbox[0:2], line_feature.legend_bbox[2:4]]
        legend.features.append(map_unit)
    for poly_feature in cdr_results.polygon_feature_results:
        map_unit = MapUnit(type=MapUnitType.POLYGON)
        map_unit.label = poly_feature.label
        map_unit.abbreviation = poly_feature.abbreviation
        map_unit.description = poly_feature.description
        map_unit.color = poly_feature.color
        map_unit.pattern = poly_feature.pattern
        map_unit.label_bbox = [poly_feature.legend_bbox[0:2], poly_feature.legend_bbox[2:4]]
        legend.features.append(map_unit)
    map_data.legend = legend
    # Layout
    layout = Layout(provenance=Provenance(name=cdr_results.system, version=cdr_results.system_version))
    for ae in cdr_results.cog_area_extractions:
        if ae.category == AreaType.Map_Area:
            if len(layout.map) > 0:
                if ae.confidence > layout.map[0].confidence:
                    layout.map = [AreaBoundary(geometry=ae.px_geojson.coordinates, confidence=ae.confidence)]
            else:
                layout.map = [AreaBoundary(geometry=ae.px_geojson.coordinates, confidence=ae.confidence)]
        if ae.category == AreaType.Polygon_Legend_Area:
            layout.polygon_legend.append(AreaBoundary(geometry=ae.px_geojson.coordinates, confidence=ae.confidence))
        if ae.category == AreaType.Line_Point_Legend_Area:
            layout.line_legend.append(AreaBoundary(geometry=ae.px_geojson.coordinates, confidence=ae.confidence))
            layout.point_legend.append(AreaBoundary(geometry=ae.px_geojson.coordinates, confidence=ae.confidence))
        if ae.category == AreaType.Point_Legend_Area:
            layout.point_legend.append(AreaBoundary(geometry=ae.px_geojson.coordinates, confidence=ae.confidence))
        if ae.category == AreaType.CrossSection:
            layout.cross_section.append(AreaBoundary(geometry=ae.px_geojson.coordinates, confidence=ae.confidence))
        if ae.category == AreaType.Correlation_Diagram:
            layout.correlation_diagram.append(AreaBoundary(geometry=ae.px_geojson.coordinates, confidence=ae.confidence))
    map_data.layout = layout
    return map_data

def convert_cdr_legend_items_to_legend(cdr_legend:List[LegendItemResponse]) -> Legend:
    """
    Convert a list of cdr_schema LegendItemResponse to a cmaas_utils Legend object.
    
    Args:
        cdr_legend (List[LegendItemResponse]): A list of cdr_schema LegendItemResponse objects.
        
    Returns:
        Legend: A cmaas_utils Legend object.
    """
    if len(cdr_legend) == 0:
        return None
    legend = Legend(provenance=Provenance(name=cdr_legend[0].system, version=cdr_legend[0].system_version))    
    for item in cdr_legend:
        map_unit = MapUnit(type=MapUnitType.from_str(item.category.lower()))
        map_unit.label = item.label
        map_unit.abbreviation = item.abbreviation
        map_unit.description = item.description
        map_unit.color = item.color
        map_unit.pattern = item.pattern
        map_unit.label_bbox = [item.px_bbox[0:2],item.px_bbox[2:4]] if len(item.px_bbox) > 0 else []
        legend.features.append(map_unit)
    return legend

def convert_cdr_area_extraction_to_layout(cdr_area_extraction:List[AreaExtractionResponse]) -> Layout:
    """
    Convert a list of cdr_schema AreaExtractionResponse to a cmaas_utils Layout object.

    Args:
        cdr_area_extraction (List[AreaExtractionResponse]): A list of cdr_schema AreaExtractionResponse objects.

    Returns:
        Layout: A cmaas_utils Layout object.
    """
    if len(cdr_area_extraction) == 0:
        return None
    layout = Layout(provenance=Provenance(name=cdr_area_extraction[0].system, version=cdr_area_extraction[0].system_version))
    for area in cdr_area_extraction:
        # Map area is selected by the highest confidence
        if area.category == 'map_area':
            if len(layout.map) == 0:
                layout.map = [AreaBoundary(geometry=area.px_geojson.coordinates, confidence=area.confidence)]
            else:
                cur_confidence = 0
                for map_area in layout.map:
                    if map_area.confidence is not None:
                        cur_confidence = max(cur_confidence, map_area.confidence)
                if area.confidence > cur_confidence:
                    layout.map = [AreaBoundary(geometry=area.px_geojson.coordinates, confidence=area.confidence)]
        # All other areas are concatanated to the layout
        if area.category == 'line_point_legend_area':
            layout.line_legend.append(AreaBoundary(geometry=area.px_geojson.coordinates, confidence=area.confidence))
            layout.point_legend.append(AreaBoundary(geometry=area.px_geojson.coordinates, confidence=area.confidence))
        if area.category == 'polygon_legend_area':
            layout.polygon_legend.append(AreaBoundary(geometry=area.px_geojson.coordinates, confidence=area.confidence))
        if area.category == 'cross_section':
            layout.cross_section.append(AreaBoundary(geometry=area.px_geojson.coordinates, confidence=area.confidence))
        if area.category == 'correlation_diagram':
            layout.correlation_diagram.append(AreaBoundary(geometry=area.px_geojson.coordinates, confidence=area.confidence))
    return layout
# endregion Convert CDR to CMAAS