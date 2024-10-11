import numpy as np
from src.cmaas_utils.types import AreaBoundary, CMAAS_Map, CMAAS_MapMetadata, GeoReference, Layout, Legend, MapUnit, MapUnitSegmentation, MapUnitType, Provenance
import src.cmaas_utils.io as io
from shapely.geometry import Polygon

class Test_Provenance():
    def test_provenance_creation(self):
        prov = Provenance(name='test', version='0.1')
        assert prov.name == 'test'
        assert prov.version == '0.1'

class Test_MapUnitSegmentation():
    def test_map_unit_segmentation_creation(self):
        # Create a provenance object
        prov = Provenance(name='test', version='0.1')

        # Create a map unit segmentation object
        map_unit_segmentation = MapUnitSegmentation(
            provenance=prov,
            confidence=0.95,
            mask=np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]),
            geometry=[Polygon([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])]
        )

        # Check the attributes of the map unit segmentation
        assert map_unit_segmentation.provenance == prov
        assert map_unit_segmentation.confidence == 0.95
        assert np.array_equal(map_unit_segmentation.mask, np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]))

class Test_MapUnit():
    def test_map_unit_creation(self):
        # Create a map unit object
        map_unit = MapUnit(
            type=MapUnitType.POLYGON,
            label='Water',
            label_confidence=0.95,
            label_bbox=[[0, 0], [5, 6]],
            description='Map unit representing water bodies',
            description_confidence=0.90,
            description_bbox=[[1, 2], [3, 4]],
            abbreviation='W',
            aliases=['H2O'],
            color='blue',
            pattern='solid',
            overlay=False
        )

        # Check the attributes of the map unit
        assert map_unit.type == MapUnitType.POLYGON
        assert map_unit.label == 'Water'
        assert map_unit.abbreviation == 'W'
        assert map_unit.description == 'Map unit representing water bodies'
        assert map_unit.color == 'blue'
        assert map_unit.pattern == 'solid'
        assert map_unit.overlay == False
        assert map_unit.label_bbox == [[0, 0], [5, 6]]
        assert map_unit.segmentation == None

class Test_Legend():
    def test_legend_creation(self):
        # Create a provenance object
        prov = Provenance(name='test', version='0.1')

        # Create a map unit object
        map_unit = MapUnit(
            type=MapUnitType.POLYGON,
            label='Water',
            abbreviation='W',
            description='Map unit representing water bodies',
            color='blue',
            pattern='solid',
            overlay=False,
            label_bbox=[[0, 0], [10, 10]]
        )

        # Create a legend object
        legend = Legend(provenance=prov, features=[map_unit])

        # Check the attributes of the legend
        assert legend.provenance == prov
        assert legend.features == [map_unit]

class Test_AreaBoundary():
    def test_area_boundary_creation(self):
        # Create an area boundary object
        area_boundary = AreaBoundary(geometry=[[[1, 0, 1], [0, 1, 0], [1, 0, 1]]], confidence=0.95)

        # Check the attributes of the area boundary
        assert area_boundary.geometry == [[[1, 0, 1], [0, 1, 0], [1, 0, 1]]]
        assert area_boundary.confidence == 0.95

class Test_Layout():
    def test_layout_creation(self):
        # Create a provenance object
        prov = Provenance(name='test', version='0.1')

        maparea = [AreaBoundary(geometry=[[[1, 0, 1], [0, 1, 0], [1, 0, 1]]])]
        point_legend = [AreaBoundary(geometry=[[[1, 0, 1], [0, 1, 0], [1, 0, 1]]])]
        line_legend = [AreaBoundary(geometry=[[[1, 0, 1], [0, 1, 0], [1, 0, 1]]])]
        polygon_legend = [AreaBoundary(geometry=[[[1, 0, 1], [0, 1, 0], [1, 0, 1]]])]
        correlation_diagram = [AreaBoundary(geometry=[[[1, 0, 1], [0, 1, 0], [1, 0, 1]]])]
        cross_section = [AreaBoundary(geometry=[[[1, 0, 1], [0, 1, 0], [1, 0, 1]]])]

        # Create a layout object
        layout = Layout(
            provenance=prov,
            map=maparea,
            point_legend=point_legend,
            line_legend=line_legend,
            polygon_legend=polygon_legend,
            correlation_diagram=correlation_diagram,
            cross_section=cross_section
        )

        # Check the attributes of the layout
        assert layout.provenance == prov
        assert layout.map == maparea
        assert layout.point_legend == point_legend
        assert layout.line_legend == line_legend
        assert layout.polygon_legend == polygon_legend
        assert layout.correlation_diagram == correlation_diagram
        assert layout.cross_section == cross_section

class Test_GeoReference():
    def test_georeference_creation(self):
        # Create a provenance object
        prov = Provenance(name='test', version='0.1')

        # Create a georeference object
        georef = GeoReference(provenance=prov)

        # Check the attributes of the georeference
        assert georef.provenance == prov

class Test_CMAAS_MapMetadata:
    def test_cmaas_map_metadata_creation(self):
        # Create a CMAAS map metadata object
        metadata = CMAAS_MapMetadata(
            provenance=Provenance(name='test', version='0.1'),
            title='Sample Map',
            authors=['Author 1', 'Author 2'],
            publisher='Publisher',
            source_url='https://example.com',
            year=2022,
            scale='1:24,000',
            map_color='full color',
            map_shape='rectangle',
            physiographic_region='Region'
        )

        # Check the attributes of the CMAAS map metadata
        assert metadata.provenance.name == 'test'
        assert metadata.provenance.version == '0.1'
        assert metadata.title == 'Sample Map'
        assert metadata.authors == ['Author 1', 'Author 2']
        assert metadata.publisher == 'Publisher'
        assert metadata.source_url == 'https://example.com'
        assert metadata.year == 2022
        assert metadata.scale == '1:24,000'
        assert metadata.map_color == 'full color'
        assert metadata.map_shape == 'rectangle'
        assert metadata.physiographic_region == 'Region'

class Test_CMAAS_Map:
    def test_cmaas_map_creation(self):
        # Create a provenance object
        provenance = Provenance(name='test', version='0.1')
        
        # Create a CMAAS map metadata object
        metadata = CMAAS_MapMetadata(
            provenance=provenance,
            title='Sample Map',
            authors=['Author 1', 'Author 2'],
            publisher='Publisher',
            source_url='https://example.com',
            year=2022,
            scale='1:24,000',
            map_color='full color',
            map_shape='rectangle',
            physiographic_region='Region'
        )
        
        # Create a layout object
        layout = Layout(provenance=provenance)
        
        # Create a CMAAS map object
        cmaas_map = CMAAS_Map(
            name='Sample Map',
            cog_id='12345',
            image=None,
            metadata=metadata,
            layout=layout
        )
        
        # Check the attributes of the CMAAS map
        assert cmaas_map.name == 'Sample Map'
        assert cmaas_map.cog_id == '12345'
        assert cmaas_map.image is None
        assert cmaas_map.metadata == metadata
        assert cmaas_map.layout == layout

    # def test_poly_geometry_generation(self):
    #     map_data = CMAAS_Map(name='VA_Stanardsville')
    #     map_data.legend = io.loadLegendJson('tests/data/legends/VA_Stanardsville.json')
    #     map_data.poly_segmentation_mask = io.loadGeoTiff('tests/data/segmentations/VA_Stanardsville_poly_segmentation.tif')[0]
        
    #     map_data.generate_poly_geometry(Provenance(name='test', version='0.1'))
    #     # Just testing that the function executes without error
    #     assert True

    # def test_point_geometry_generation(self):
    #     # map_data = CMAAS_Map(name='VA_Stanardsville')
    #     # map_data.legend = io.loadLegendJson('tests/data/legends/VA_Stanardsville.json')
    #     # map_data.point_segmentation_mask = io.loadGeoTiff('tests/data/segmentations/VA_Stanardsville_point_segmentation.tif')[0]
        
    #     map_data.generate_point_geometry(Provenance(name='test', version='0.1'))
    #     # Just testing that the function executes without error
    #     assert True

