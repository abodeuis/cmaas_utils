import rasterio
import numpy as np
from enum import Enum
from typing import List, Optional, Union
from shapely.geometry import Polygon
from pydantic import BaseModel, Field
from rasterio.crs import CRS

class Provenance(BaseModel):
    name : str = Field(    
        description='The name of the model used to generate the data')
    version : Optional[str] = Field(
        default=None,
        description='The version of the model used to generate the data')

# region MapUnit
class MapUnitType(Enum):
    """
    The type of map unit.
    """
    POINT = 0
    LINE = 1
    POLYGON = 2
    UNKNOWN = 3
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
            return 'point'
        elif self == MapUnitType.LINE:
            return 'line'
        elif self == MapUnitType.POLYGON:
            return 'polygon'
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
            repr_str += 'UNKNOWN'
        return repr_str

class MapUnitSegmentation(BaseModel):
    """
    The information describing the occurances of the map unit in the map.
    """
    provenance : Provenance = Field(
        description='Information about the source the segmentation orginated from')
    confidence : Optional[float] = Field(
        default=None,
        description='The confidence of the segmentation')
    mask : Optional[np.ndarray] = Field(
        default=None,
        description='A binary mask of the map unit')
    geometry : Optional[List[Polygon]] = Field(
        default=None,
        description='The vector geometry of the map unit')
    
    class Config:
        arbitrary_types_allowed = True

class MapUnit(BaseModel):
    """
    A unit which contains the information a feature from the Legend.
    """
    type : MapUnitType = Field(
        description='The type of the map unit')
    label : Optional[str] = Field(
        default=None,
        description='The label of the map unit in the legend')
    label_confidence : Optional[float] = Field(
        default=None,
        description='The predicted confidence of the label')
    label_bbox : Optional[List[List[float]]] = Field(
        default=None,
        description="""The more precise polygon bounding box of the map units label. Format is expected to be [x,y]
                    coordinate pairs where the top left is the origin (0,0).""")
    
    description : Optional[str] = Field(
        default=None,
        description='The description of the map unit in the legend')
    description_confidence : Optional[float] = Field(
        default=None,
        description='The predicted confidence of the description')
    description_bbox : Optional[List[List[float]]] = Field(
        default=None,
        description="""The more precise polygon bounding box of the map units description. Format is expected to be [x,y]
                    coordinate pairs where the top left is the origin (0,0).""")
    
    abbreviation : Optional[str] = Field(
        default=None,
        description='The abbreviation of the map unit in the legend')
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
    
    segmentation : Optional[MapUnitSegmentation] = Field(
        default=None,
        description='The segmentation of the map unit')

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
        repr_str += f'bounding_box : {self.label_bbox}'
        return repr_str
# endregion MapUnit

# region Legend
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
    
    def __eq__(self, __value) -> bool:
        if self is None or __value is None:
            if self is None and __value is None:
                return True
            else:
                return False
        if self.provenance != __value.provenance:
            return False
        for u1 in self.features:
            matched = False
            for u2 in __value.features:
                if u1 == u2:
                    matched = True
                    break
            if not matched:
                return False
        return True

    def __len__(self):
        return len(self.features)

    def __str__(self) -> str:
        out_str = 'Legend{Provenance : ' + f'{self.provenance}, {len(self.features)} Features : {self.features}' + '}'
        return out_str
    
    def __repr__(self) -> str:
        repr_str = 'Legend{Provenance : ' + f'{self.provenance}, {len(self.features)} Features : {self.features}' + '}'
        return repr_str
# endregion Legend

# region Layout
class AreaBoundary(BaseModel):
    """
    A polygon area defining a specific region of the map.
    """
    geometry : List[List[List[Union[int, float]]]] = Field(
        description="""The coordinates of the areas boundry. Format is expected
                    to be [x,y] coordinate pairs where the top left is the
                    origin (0,0).""")
    confidence : Optional[float] = Field(
        default=None,
        description='The confidence of the area')

class Layout(BaseModel):
    """
    Information about where certain features of the map are in the image 
    """
    provenance : Provenance = Field(
        description='Information about the source the Layout orginated from')
    map : List[AreaBoundary] = Field(
        default=[],
        description='The map segmentation')
    point_legend : List[AreaBoundary] = Field(
        default=[],
        description='The point map unit segmentation')
    line_legend : List[AreaBoundary] = Field(
        default=[],
        description='The line map unit segmentation')
    polygon_legend : List[AreaBoundary] = Field(
        default=[],
        description='The polygon map unit segmentation')
    correlation_diagram : List[AreaBoundary] = Field(
        default=[],
        description='The correlation diagram')
    cross_section : List[AreaBoundary] = Field(
        default=[],
        description='The cross section')

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
# endregion Layout
# region GeoReference
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

# endregion GeoReference
# region Map Metadata
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
# endregion Map Metadata

# region CMAAS Map
class MapSegmentation(BaseModel):
    """
    A segmentation mask for a map. 
    """
    provenance : Provenance = Field(
        description='Information about the source the mask orginated from')
    type : MapUnitType = Field(
        description='The type of the map unit this mask is for')
    image : np.ndarray = Field(
        description="""The segmentation mask of the map. This is a single image with the value of each pixel being
                    the map unit index in the legend.features""")
    confidence : Optional[float] = Field(
        default=None,
        description='The confidence of the mask')
    
    class Config:
        arbitrary_types_allowed = True

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
    segmentations : List[MapSegmentation] = Field(
        default=[],
        description='The segmentation masks for the map')

    class Config:
        arbitrary_types_allowed = True

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
# endregion CMAAS Map
