import numpy as np
from enum import Enum
from typing import List, Optional
from shapely.geometry import shape
from pydantic import BaseModel, Field

import rasterio
from rasterio.crs import CRS
from rasterio.features import shapes, sieve 
# from rasterio.control import GroundControlPoint
# from rasterio.transform import from_gcps


DEBUG_MODE = False # Turns on debuging why two objects are not equal

class MapUnitType(Enum):
    POINT = 1
    LINE = 2
    POLYGON = 3
    UNKNOWN = 4
    def ALL():
        return [MapUnitType.POINT, MapUnitType.LINE, MapUnitType.POLYGON, MapUnitType.UNKNOWN]
    def ALL_KNOWN():
        return [MapUnitType.POINT, MapUnitType.LINE, MapUnitType.POLYGON]

    def from_str(feature_type:str):
        if feature_type.lower() in ['pt','point']:
            return MapUnitType.POINT
        elif feature_type.lower() in ['line']:
            return MapUnitType.LINE
        elif feature_type.lower() in ['poly','polygon']:
            return MapUnitType.POLYGON
        else:
            return MapUnitType.UNKNOWN
        
    def to_str(self):
        if self == MapUnitType.POINT:
            return 'pt'
        elif self == MapUnitType.LINE:
            return 'line'
        elif self == MapUnitType.POLYGON:
            return 'poly'
        else:
            return 'unknown'

    def __str__(self) -> str:
        return self.to_str()
    
    def __repr__(self) -> str:
        repr_str = 'MapUnitType.'
        if self == MapUnitType.POINT:
            repr_str += 'POINT'
        elif self == MapUnitType.LINE:
            repr_str += 'LINE'
        elif self == MapUnitType.POLYGON:
            repr_str += 'POLYGON'
        else:
            repr_str += 'Unknown'
        return repr_str
    
class Provenance(BaseModel):
    name : str = Field(    
        description='The name of the model used to generate the data')
    version : Optional[str] = Field(
        default=None,
        description='The version of the model used to generate the data')
    
    # def __eq__(self, __value: object) -> bool:
    #     if self is None or __value is None:
    #         if self is None and __value is None:
    #             return True
    #         else:
    #             return False
    #     if self.name != __value.name:
    #         if DEBUG_MODE:
    #             print(f'Name Mismatch: {self.name} != {__value.name}')
    #         return False
    #     if self.version != __value.version:
    #         if DEBUG_MODE:
    #             print(f'Version Mismatch: {self.version} != {__value.version}')
    #         return False
    #     return True

class MapUnitSegmentation(BaseModel):
    provenance : Provenance = Field(
        description='Information about the source the segmentation orginated from')
    mask : Optional[np.ndarray] = Field(
        default=None,
        description='A binary mask of the map unit')
    geometry : Optional[List[List[List[float]]]] = Field(
        default=None,
        description='The vector geometry of the map unit')
    
    class Config:
        arbitrary_types_allowed = True

class MapUnit(BaseModel):
    """
    The information describing a map unit along with it's segmentation if present.
    """
    type : MapUnitType = Field(
        description='The type of the map unit')
    label : Optional[str] = Field(
        default=None,
        description='The label of the map unit in the legend')
    abbreviation : Optional[str] = Field(
        default=None,
        description='The abbreviation of the map unit in the legend')
    description : Optional[str] = Field(
        default=None,
        description='The description of the map unit in the legend')
    aliases : Optional[List[str]] = Field(
        default=None,
        description='Any know aliases of the of the map unit\'s name.')
    color : Optional[str] = Field(
        default=None,
        description='The color of the map unit in the legend')
    pattern : Optional[str] = Field(
        default=None,
        description='The pattern of the map unit in the legend')
    overlay : Optional[bool] = Field(
        default=False,
        description='Wheather or not the map unit can be overlayed on other map units')
    bounding_box : Optional[List[List[float]]] = Field(
        default=None,
        description="""The more precise polygon bounding box of the map units label. Format is expected to be [x,y]
                    coordinate pairs where the top left is the origin (0,0).""")
    segmentation : Optional[MapUnitSegmentation] = Field(
        default=None,
        description='The segmentation of the map unit')
    
    # def to_dict(self):
    #     return {
    #         'type' : self.type,
    #         'label' : self.label,
    #         'abbreviation' : self.abbreviation,
    #         'description' : self.description,
    #         'color' : self.color,
    #         'pattern' : self.pattern,
    #         'overlay' : self.overlay,
    #         'bounding_box' : self.bounding_box
    #     }
    
    # def __eq__(self, __value: object) -> bool:
    #     # Check if either self or __value is None
    #     if self is None or __value is None:
    #         if self is None and __value is None:
    #             return True
    #         else:
    #             return False
    #     # Check individual fields match
    #     if self.type != __value.type:
    #         if DEBUG_MODE:
    #             print(f'Type Mismatch: {self.type} != {__value.type}')
    #         return False
    #     if self.label != __value.label:
    #         if DEBUG_MODE:
    #             print(f'Label Mismatch: {self.label} != {__value.label}')
    #         return False
    #     if self.abbreviation != __value.abbreviation:
    #         if DEBUG_MODE:
    #             print(f'Abbreviation Mismatch: {self.abbreviation} != {__value.abbreviation}')
    #         return False
    #     if self.description != __value.description:
    #         if DEBUG_MODE:
    #             print(f'Description Mismatch: {self.description} != {__value.description}')
    #         return False
    #     if self.color != __value.color:
    #         if DEBUG_MODE:
    #             print(f'Color Mismatch: {self.color} != {__value.color}')
    #         return False
    #     if self.pattern != __value.pattern:
    #         if DEBUG_MODE:
    #             print(f'Pattern Mismatch: {self.pattern} != {__value.pattern}')
    #         return False
    #     if self.overlay != __value.overlay:
    #         if DEBUG_MODE:
    #             print(f'Overlay Mismatch: {self.overlay} != {__value.overlay}')
    #         return False
    #     # if isinstance(self.bounding_box, (np.ndarray, np.generic)) or isinstance(__value.bounding_box, (np.ndarray, np.generic)):
    #     #     if (self.bounding_box != __value.bounding_box).any():
    #     #         if DEBUG_MODE:
    #     #             print(f'Bounding Box Mismatch: {self.bounding_box} != {__value.bounding_box}')
    #     #         return False
    #     else:
    #         if self.bounding_box != __value.bounding_box:
    #             if DEBUG_MODE:
    #                 print(f'Bounding Box Mismatch: {self.bounding_box} != {__value.bounding_box}')
    #             return False
    #     return True

    def __str__(self) -> str:
        out_str = 'MapUnit{\'' + self.label + '\'}'
        return out_str

    def __repr__(self) -> str:
        repr_str = 'MapUnit{'
        repr_str += f'type : \'{self.type}\', '
        repr_str += f'label : \'{self.label}\', '
        repr_str += f'abbreviation : \'{self.abbreviation}\', '
        repr_str += f'description : \'{self.description}\', '
        repr_str += f'aliases : {self.aliases}, '
        repr_str += f'color : \'{self.color}\', '
        repr_str += f'pattern : \'{self.pattern}\', '
        repr_str += f'overlay : {self.overlay}, '
        repr_str += f'bounding_box : {self.bounding_box}'
        return repr_str

class Legend(BaseModel):
    """
    A collection of map units that make up the legend of a map.
    """
    provenance : Provenance = Field(
        description='Information about the source the Legend orginated from')
    features : List[MapUnit] = Field(
        default=[],
        description='The map units that make up the legend')
    

    def to_dict(self):
        feature_dict = {}
        for map_unit in self.features:
            feature_dict[map_unit.label] = map_unit.to_dict()
        return {
            'features' : feature_dict,
            'provenance' : self.provenance
        }
    
    def map_unit_distr(self):
        dist = {}
        for feature in self.features:
            if feature.type in dist:
                dist[feature.type].append(feature.label)
            else:
                dist[feature.type] = [feature.label]
        return dist

    def __len__(self):
        return len(self.features)
    
    def __eq__(self, __value: object) -> bool:
        if self is None or __value is None:
            if self is None and __value is None:
                return True
            else:
                return False
        # if self.provenance != __value.provenance:
        #     if DEBUG_MODE:
        #         print(f'Provenance Mismatch: {self.provenance} != {__value.provenance}')
        #     return False
        for u1 in self.features:
            matched = False
            for u2 in __value.features:
                if DEBUG_MODE:
                    print(f'Comparing {u1} and {u2}')
                if u1 == u2:
                    if DEBUG_MODE:
                        print(f'Feature match: {u1} == {u2}')
                    matched = True
                    break
            if not matched:
                if DEBUG_MODE:
                    print(f'Feature Mismatch: {u1} != {u2}')
                return False
        return True

    def __str__(self) -> str:
        out_str = 'Legend{Provenance : ' + f'{self.provenance}, {len(self.features)} Features : {self.features}' + '}'
        return out_str
    
    def __repr__(self) -> str:
        repr_str = 'Legend{Provenance : ' + f'{self.provenance}, {len(self.features)} Features : {self.features}' + '}'
        return repr_str

class Layout(BaseModel):
    """
    The area segmentations for a map
    """
    provenance : Provenance = Field(
        description='Information about the source the Layout orginated from')
    map : Optional[List[List[List[float]]]] = Field(
        default=None,
        description='The map segmentation')
    point_legend : Optional[List[List[List[float]]]] = Field(
        default=None,
        description='The point map unit segmentation')
    line_legend : Optional[List[List[List[float]]]] = Field(
        default=None,
        description='The line map unit segmentation')
    polygon_legend : Optional[List[List[List[float]]]] = Field(
        default=None,
        description='The polygon map unit segmentation')
    correlation_diagram : Optional[List[List[List[float]]]] = Field(
        default=None,
        description='The correlation diagram')
    cross_section : Optional[List[List[List[float]]]] = Field(
        default=None,
        description='The cross section')
    
    class Config:
        arbitrary_types_allowed = True

    def __str__(self) -> str:
        out_str = 'Layout{'
        out_str += f'map : {self.map}, '
        out_str += f'correlation_diagram : {self.correlation_diagram}, '
        out_str += f'cross_section : {self.cross_section}, '
        out_str += f'point_legend : {self.point_legend}, '
        out_str += f'line_legend : {self.line_legend}, '
        out_str += f'polygon_legend : {self.polygon_legend}, '
        out_str += f'provenance : {self.provenance}'
        out_str += '}'
        return out_str
    
    def __repr__(self) -> str:
        out_str = 'Layout{'
        out_str += f'map : {self.map}, '
        out_str += f'correlation_diagram : {self.correlation_diagram}, '
        out_str += f'cross_section : {self.cross_section}, '
        out_str += f'point_legend : {self.point_legend}, '
        out_str += f'line_legend : {self.line_legend}, '
        out_str += f'polygon_legend : {self.polygon_legend}, '
        out_str += f'provenance : {self.provenance}'
        out_str += '}'
        return out_str

    def __eq__(self, __value: object) -> bool:
        if self is None or __value is None:
            if self is None and __value is None:
                return True
            else:
                return False
        # if self.provenance != __value.provenance:
        #     if DEBUG_MODE:
        #         print(f'Provenance Mismatch: {self.provenance} != {__value.provenance}')
        #     return False
        if isinstance(self.map, (np.ndarray, np.generic)) and isinstance(__value.map, (np.ndarray, np.generic)):
            if (self.map != __value.map).any():
                if DEBUG_MODE:
                    print(f'Map Mismatch: {self.map} != {__value.map}')
                return False
        else:
            if self.map != __value.map:
                if DEBUG_MODE:
                    print(f'Map Mismatch: {self.map} != {__value.map}')
                return False
        if isinstance(self.correlation_diagram, (np.ndarray, np.generic)) or isinstance(__value.correlation_diagram, (np.ndarray, np.generic)):
            if (self.correlation_diagram != __value.correlation_diagram).any():
                if DEBUG_MODE:
                    print(f'Correlation Diagram Mismatch: {self.correlation_diagram} != {__value.correlation_diagram}')
                return False
        else:
            if self.correlation_diagram != __value.correlation_diagram:
                if DEBUG_MODE:
                    print(f'Correlation Diagram Mismatch: {self.correlation_diagram} != {__value.correlation_diagram}')
                return False
        if isinstance(self.cross_section, (np.ndarray, np.generic)) or isinstance(__value.cross_section, (np.ndarray, np.generic)):
            if (self.cross_section != __value.cross_section).any():
                if DEBUG_MODE:
                    print(f'Cross Section Mismatch: {self.cross_section} != {__value.cross_section}')
                return False
        else:
            if self.cross_section != __value.cross_section:
                if DEBUG_MODE:
                    print(f'Cross Section Mismatch: {self.cross_section} != {__value.cross_section}')
                return False
        if isinstance(self.point_legend, (np.ndarray, np.generic)) or isinstance(__value.point_legend, (np.ndarray, np.generic)):
            if (self.point_legend != __value.point_legend).any():
                if DEBUG_MODE:
                    print(f'Point Legend Mismatch: {self.point_legend} != {__value.point_legend}')
                return False
        else:
            if self.point_legend != __value.point_legend:
                if DEBUG_MODE:
                    print(f'Point Legend Mismatch: {self.point_legend} != {__value.point_legend}')
                return False
        if isinstance(self.line_legend, (np.ndarray, np.generic)) or isinstance(__value.line_legend, (np.ndarray, np.generic)):
            if (self.line_legend != __value.line_legend).any():
                if DEBUG_MODE:
                    print(f'Line Legend Mismatch: {self.line_legend} != {__value.line_legend}')
                return False
        else:
            if self.line_legend != __value.line_legend:
                if DEBUG_MODE:
                    print(f'Line Legend Mismatch: {self.line_legend} != {__value.line_legend}')
                return False
        if isinstance(self.polygon_legend, (np.ndarray, np.generic)) or isinstance(__value.polygon_legend, (np.ndarray, np.generic)):
            if (self.polygon_legend != __value.polygon_legend).any():
                if DEBUG_MODE:
                    print(f'Polygon Legend Mismatch: {self.polygon_legend} != {__value.polygon_legend}')
                return False
        else:
            if self.polygon_legend != __value.polygon_legend:
                if DEBUG_MODE:
                    print(f'Polygon Legend Mismatch: {self.polygon_legend} != {__value.polygon_legend}')
                return False
        
        return True
    
    def to_dict(self):
        return {
            'provenance' : self.provenance,
            'map' : self.map,
            'point_legend' : self.point_legend,
            'line_legend' : self.line_legend,
            'polygon_legend' : self.polygon_legend,
            'correlation_diagram' : self.correlation_diagram,
            'cross_section' : self.cross_section,
        }

class GeoReference(BaseModel):
    """
    Georeferencing information for a map.
    """
    provenance : Provenance = Field(
        description='Information about the source the GeoReference orginated from')
    crs : Optional[CRS] = Field(
        default=None,
        description="""The EPSG number for the crs. Should be in the format "EPSG:####" or an equivelent that can be
                    read by rasterio.CRS.from_string()""")
    transform : Optional[rasterio.transform.Affine] = Field(
        default=None,
        description='The affine transformation matrix for the map')
    
    class Config:
        arbitrary_types_allowed = True
    # gcps : Optional[List[GroundControlPoint]] = Field(
    #     default=None,
    #     description='List of ground control points that can be used to create the transform and crs')



    def __eq__(self, __value: object) -> bool:
        if self is None or __value is None:
            if self is None and __value is None:
                return True
            else:
                return False
            
        if self.crs is not None and self.transform is not None and __value.crs is not None and __value.transform is not None:
            if self.crs != __value.crs:
                if DEBUG_MODE:
                    print(f'CRS Mismatch: {self.crs} != {__value.crs}')
                return False
            if self.transform != __value.transform:
                if DEBUG_MODE:
                    print(f'Transform Mismatch: {self.transform} != {__value.transform}')
                return False

        return True

class TextUnit(BaseModel):
    """
    A single unit of text extracted from a map.
    """
    label : str = Field(
        description='The text contained in the unit')
    geometry : List[List[float]] = Field(
        description='The geometry of the text unit')
    confidence : Optional[float] = Field(
        default=None,
        description='The confidence of the OCR model')
    

class OCRText(BaseModel):
    """
    The OCR text extracted from a map.
    """
    provenance : Provenance = Field(
        description='Information about the source the OCR text orginated from')
    features : List[TextUnit] = Field(
        default=[],
        description='The individual text units in the map')
        
class CMAAS_MapMetadata(BaseModel):
    """
    Metadata for a map.
    """
    provenance : Provenance = Field(
        description='Information about the source the Metadata orginated from')
    title : Optional[str] = Field(
        default=None,
        description='The title of the map')
    authors : Optional[List[str]] = Field(
        default=None,
        description='The authors of the map')
    publisher : Optional[str] = Field(
        default=None,
        description='The publisher of the map')
    source_url : Optional[str] = Field(
        default=None,
        description='The source url of the map')
    year : Optional[int] = Field(
        default=None,
        description='The year the map was published')
    scale : Optional[str] = Field(
        default=None,
        description='The scale of the map. E.g. 1:24,000')
    map_color : Optional[str] = Field(
        default=None,
        description='The color type of the map. Possible values are full color, monocolor, greyscale.')
    map_shape : Optional[str] = Field(
        default=None,
        description='The shape of the map area. Possible values are rectangle or non-rectangle.')
    physiographic_region : Optional[str] = Field( # Would be helpful if theres a link to a resource that can display the possible values for this
        default=None,
        description='The physiographic region of the map')
    
    # Cut Fields
    # url : str # What is the diff between url and source url.
    # organization : str # Is this signifgantly difference then publisher?

    def to_dict(self):
        return {
            'provenance' : self.provenance,
            'title' : self.title,
            'authors' : self.authors,
            'year' : self.year,
            'publisher' : self.publisher,
            'organization' : self.organization,
            'source_url' : self.source_url,
            'url' : self.url,
            'scale' : self.scale,
            'map_shape' : self.map_shape,
            'map_color' : self.map_color,
            'physiographic_region' : self.physiographic_region,
            
        }
    
    def __str__(self) -> str:
        out_str = 'CMASS_MapMetadata{'
        out_str += f'provenance : \'{self.provenance}\', '
        out_str += f'title : \'{self.title}\', '
        out_str += f'authors : {self.authors}, '
        out_str += f'publisher : \'{self.publisher}\', '
        out_str += f'url : \'{self.url}\', '
        out_str += f'source_url : \'{self.source_url}\', '
        out_str += f'year : {self.year}, '
        out_str += f'organization : \'{self.organization}\', '
        out_str += f'scale : \'{self.scale}\', '
        out_str += f'map_color : \'{self.map_color}\', '
        out_str += f'map_shape : \'{self.map_shape}\', '
        out_str += f'physiographic_region : \'{self.physiographic_region}\''
        out_str += '}'
        return out_str
    
    def __repr__(self) -> str:
        repr_str = 'CMASS_MapMetadata{'
        repr_str += f'provenance : \'{self.provenance}\', '
        repr_str += f'title : \'{self.title}\', '
        repr_str += f'authors : {self.authors}, '
        repr_str += f'publisher : \'{self.publisher}\', '
        repr_str += f'url : \'{self.url}\', '
        repr_str += f'source_url : \'{self.source_url}\', '
        repr_str += f'year : {self.year}, '
        repr_str += f'organization : \'{self.organization}\', '
        repr_str += f'scale : \'{self.scale}\', '
        repr_str += f'map_color : \'{self.map_color}\', '
        repr_str += f'map_shape : \'{self.map_shape}\', '
        repr_str += f'physiographic_region : \'{self.physiographic_region}\''
        repr_str += '}'
        return repr_str

    # def __eq__(self, __value: object) -> bool:
    #     if self is None or __value is None:
    #         if self is None and __value is None:
    #             return True
    #         else:
    #             return False
            
    #     if self.provenance != __value.provenance:
    #         if DEBUG_MODE:
    #             print(f'Provenance Mismatch: {self.provenance} != {__value.provenance}')
    #         return False
    #     if self.title != __value.title:
    #         if DEBUG_MODE:
    #             print(f'Title Mismatch: {self.title} != {__value.title}')
    #         return False
    #     if self.authors != __value.authors:
    #         if DEBUG_MODE:
    #             print(f'Authors Mismatch: {self.authors} != {__value.authors}')
    #         return False
    #     if self.publisher != __value.publisher:
    #         if DEBUG_MODE:
    #             print(f'Publisher Mismatch: {self.publisher} != {__value.publisher}')
    #         return False
    #     if self.url != __value.url:
    #         if DEBUG_MODE:
    #             print(f'URL Mismatch: {self.url} != {__value.url}')
    #         return False
    #     if self.source_url != __value.source_url:
    #         if DEBUG_MODE:
    #             print(f'Source URL Mismatch: {self.source_url} != {__value.source_url}')
    #         return False
    #     if self.year != __value.year:
    #         if DEBUG_MODE:
    #             print(f'Year Mismatch: {self.year} != {__value.year}')
    #         return False
    #     if self.organization != __value.organization:
    #         if DEBUG_MODE:
    #             print(f'Organization Mismatch: {self.organization} != {__value.organization}')
    #         return False
    #     if self.scale != __value.scale:
    #         if DEBUG_MODE:
    #             print(f'Scale Mismatch: {self.scale} != {__value.scale}')
    #         return False
    #     if self.map_color != __value.map_color:
    #         if DEBUG_MODE:
    #             print(f'Map Color Mismatch: {self.map_color} != {__value.map_color}')
    #         return False
    #     if self.map_shape != __value.map_shape:
    #         if DEBUG_MODE:
    #             print(f'Map Shape Mismatch: {self.map_shape} != {__value.map_shape}')
    #         return False
    #     if self.physiographic_region != __value.physiographic_region:
    #         if DEBUG_MODE:
    #             print(f'Physiographic Region Mismatch: {self.physiographic_region} != {__value.physiographic_region}')
    #         return False
    #     return True

class CMAAS_Map(BaseModel):
    """
    Contains all of the CMAAS data for a map.
    """
    name : str = Field(
        description='The name of the map. Defaults to the filename that the image was loaded from')
    cog_id : Optional[str] = Field(
        default=None,
        description='The CDR provided cog_id of the map')
    image : Optional[np.ndarray] = Field(
        default=None,
        description='The map image')
    metadata : Optional[CMAAS_MapMetadata] = Field(
        default=None,
        description='The metadata for the map')
    layout : Optional[Layout] = Field(
        default=None,
        description='The area segmentation data for the map')
    legend : Optional[Legend] = Field(
        default=None,
        description='The legend data for the map')
    georef : Optional[GeoReference] = Field(
        default=None,
        description='The georeferencing information for the map')
    ocrtext : Optional[OCRText] = Field(
        default=None,
        description='The OCR text extracted from the map')

    # Segmentation masks
    point_segmentation_mask : Optional[np.ndarray] = Field(
        default=None,
        description="""The point map unit segmentation mask. This is a single image with the value of each pixel being
                    the map unit index in the legend.features""")
    poly_segmentation_mask : Optional[np.ndarray] = Field(
        default=None,
        description="""The polygon map unit segmentation mask. This is a single image with the value of each pixel
                    being the map units index in the legend.features""")

    def generate_poly_geometry(self, mask_provenance:Provenance, noise_threshold=10):
        legend_index = 1
        for feature in self.legend.features:
            if feature.type != MapUnitType.POLYGON:
                continue
            # Get mask of feature
            feature_mask = np.zeros_like(self.poly_segmentation_mask, dtype=np.uint8)
            feature_mask[self.poly_segmentation_mask == legend_index] = 1
            # Remove "noise" from mask by removing pixel groups smaller then the threshold
            sieve_img = sieve(feature_mask, noise_threshold, connectivity=4)
            # Convert mask to vector shapes
            shape_gen = shapes(sieve_img, connectivity=4)
            # Only use Filled pixels (1s) for shapes 
            geometries = [shape(geometry) for geometry, value in shape_gen if value == 1]
            # Change Shapely geometries to List(List(List(float)))
            poly_geometry = [[[*point] for point in geometry.exterior.coords] for geometry in geometries]
            if feature.segmentation is None:
                feature.segmentation = MapUnitSegmentation(provenance=mask_provenance, geometry=poly_geometry)
            else:
                feature.segmentation.geometry = poly_geometry
            legend_index += 1

    def generate_point_geometry(self, mask_provenance:Provenance):
        legend_index = 1
        for feature in self.legend.features:
            if feature.type != MapUnitType.POINT:
                continue
            # Get mask of feature
            feature_mask = np.zeros_like(self.point_segmentation_mask, dtype=np.uint8)
            feature_mask[self.point_segmentation_mask == legend_index] = 1
            # Get points from mask
            point_geometry = np.transpose(feature_mask.nonzero())
            # Convert geometry to List(List(List(float)))
            point_geometry = [[point] for point in point_geometry]
            if feature.segmentation is None:
                feature.segmentation = MapUnitSegmentation(provenance=mask_provenance, geometry=point_geometry)
            else:
                feature.segmentation.geometry = point_geometry
            legend_index += 1


    class Config:
        arbitrary_types_allowed = True
    
    def __eq__(self, __value: object) -> bool:
        if self is None or __value is None:
            if self is None and __value is None:
                return True
            else:
                return False

        if self.name != __value.name:
            if DEBUG_MODE:
                print(f'Name Mismatch: {self.name} != {__value.name}')
            return False
        if self.image is None or __value.image is None:
            if not (self.image is None and __value.image is None):
                return False
        if self.image.shape != __value.image.shape:
            if DEBUG_MODE:
                print(f'Shape Mismatch: {self.image.shape} != {__value.image.shape}')
            return False
        # if self.georef != __value.georef:
        #     if DEBUG_MODE:
        #         print(f'GeoReference Mismatch: {self.georef} != {__value.georef}')
        #     return False
        if self.legend != __value.legend:
            if DEBUG_MODE:
                print(f'Legend Mismatch: {self.legend} != {__value.legend}')
            return False
        if self.layout != __value.layout:
            if DEBUG_MODE:
                print(f'Layout Mismatch: {self.layout} != {__value.layout}')
            return False
        if self.metadata != __value.metadata:
            if DEBUG_MODE:
                print(f'Metadata Mismatch: {self.metadata} != {__value.metadata}')
            return False
        return True

    def __str__(self) -> str:
        out_str = 'CMASS_Map{'
        out_str += f'name : \'{self.name}\', '
        if self.image is not None:
            out_str += f'image : {self.image.shape}, '
        else:
            out_str += f'image : {self.image}, '
        out_str += f'georef : {self.georef}, '
        out_str += f'legend : {self.legend}, '
        out_str += f'layout : {self.layout}, '
        out_str += f'metadata : {self.metadata}'
        out_str += '}'
        return out_str

    def __repr__(self) -> str:
        repr_str = 'CMASS_Map{'
        repr_str += f'name : \'{self.name}\', '
        if self.image is not None:
            repr_str += f'image : {self.image.shape}, '
        else:
            repr_str += f'image : {self.image}, '
        repr_str += f'georef : {self.georef}, '
        repr_str += f'legend : {self.legend}, '
        repr_str += f'layout : {self.layout}, '
        repr_str += f'metadata : {self.metadata}'
        repr_str += '}'
        return repr_str
    
    def to_dict(self):
        return {
            'version' : '0.1',
            'map_name' : self.name,
            'metadata' : self.metadata.to_dict() if self.metadata is not None else None,
            'layout' : self.layout.to_dict() if self.layout is not None else None,
            'legend' : self.legend.to_dict() if self.legend is not None else None,
            'georef' : [g.to_dict() for g in self.georef] if self.georef is not None else None,
            'ocrtext' : self.ocrtext.to_dict() if self.ocrtext is not None else None
        }

