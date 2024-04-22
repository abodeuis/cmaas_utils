import numpy as np
from src.cmaas_utils.types import CMAAS_Map, CMAAS_MapMetadata, GeoReference, Layout, Legend, MapUnit, MapUnitSegmentation, MapUnitType, Provenance, TextUnit, OCRText
from rasterio.crs import CRS
import src.cmaas_utils.io as io

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
            mask=np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]),
            geometry=[[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]
        )

        # Check the attributes of the map unit segmentation
        assert map_unit_segmentation.provenance == prov
        assert np.array_equal(map_unit_segmentation.mask, np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]))
        assert map_unit_segmentation.geometry == [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]

class Test_MapUnit():
    def test_map_unit_creation(self):
        # Create a map unit object
        map_unit = MapUnit(
            type=MapUnitType.POLYGON,
            label='Water',
            abbreviation='W',
            description='Map unit representing water bodies',
            color='blue',
            pattern='solid',
            overlay=False,
            bounding_box=[[0, 0], [10, 10]]
        )

        # Check the attributes of the map unit
        assert map_unit.type == MapUnitType.POLYGON
        assert map_unit.label == 'Water'
        assert map_unit.abbreviation == 'W'
        assert map_unit.description == 'Map unit representing water bodies'
        assert map_unit.color == 'blue'
        assert map_unit.pattern == 'solid'
        assert map_unit.overlay == False
        assert map_unit.bounding_box == [[0, 0], [10, 10]]
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
            bounding_box=[[0, 0], [10, 10]]
        )

        # Create a legend object
        legend = Legend(provenance=prov, features=[map_unit])

        # Check the attributes of the legend
        assert legend.provenance == prov
        assert legend.features == [map_unit]

class Test_Layout():
    def test_layout_creation(self):
        # Create a provenance object
        prov = Provenance(name='test', version='0.1')

        # Create a layout object
        layout = Layout(
            provenance=prov,
            map=np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]),
            point_legend=np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]),
            line_legend=np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]),
            polygon_legend=np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]),
            correlation_diagram=np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]),
            cross_section=np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]])
        )

        # Check the attributes of the layout
        assert layout.provenance == prov
        assert np.array_equal(layout.map, np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]))
        assert np.array_equal(layout.point_legend, np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]))
        assert np.array_equal(layout.line_legend, np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]))
        assert np.array_equal(layout.polygon_legend, np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]))
        assert np.array_equal(layout.correlation_diagram, np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]))
        assert np.array_equal(layout.cross_section, np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]))

class Test_GeoReference():
    def test_georeference_creation(self):
        # Create a provenance object
        prov = Provenance(name='test', version='0.1')

        # Create a georeference object
        georef = GeoReference(provenance=prov, crs=CRS.from_string('EPSG:4326'))

        # Check the attributes of the georeference
        assert georef.provenance == prov
        assert georef.crs == CRS.from_epsg(4326)

class Test_TextUnit:
    def test_text_unit_creation(self):
        # Create a text unit object
        text_unit = TextUnit(
            label='Sample Text',
            geometry=[[0, 0], [0, 1], [1, 1], [1, 0]],
            confidence=0.9
        )

        # Check the attributes of the text unit
        assert text_unit.label == 'Sample Text'
        assert text_unit.geometry == [[0, 0], [0, 1], [1, 1], [1, 0]]
        assert text_unit.confidence == 0.9

class Test_OCRText:
    def test_ocr_text_creation(self):
        # Create a text unit object
        text_unit = TextUnit(
            label='Sample Text',
            geometry=[[0, 0], [0, 1], [1, 1], [1, 0]],
            confidence=0.9
        )

        # Create an OCR text object
        ocr_text = OCRText(
            provenance=Provenance(name='test', version='0.1'),
            features=[text_unit]
        )

        # Check the attributes of the OCR text
        assert ocr_text.provenance.name == 'test'
        assert ocr_text.provenance.version == '0.1'
        assert ocr_text.features == [text_unit]

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

    def test_poly_geometry_generation(self):
        map_data = CMAAS_Map(name='VA_Stanardsville')
        map_data.legend = io.loadLegendJson('tests/data/legends/VA_Stanardsville.json')
        map_data.poly_segmentation_mask = io.loadGeoTiff('tests/data/segmentations/VA_Stanardsville_poly_segmentation.tif')[0]
        
        map_data.generate_poly_geometry(Provenance(name='test', version='0.1'))
        # Just testing that the function executes without error
        assert True

    # def test_point_geometry_generation(self):
    #     # map_data = CMAAS_Map(name='VA_Stanardsville')
    #     # map_data.legend = io.loadLegendJson('tests/data/legends/VA_Stanardsville.json')
    #     # map_data.point_segmentation_mask = io.loadGeoTiff('tests/data/segmentations/VA_Stanardsville_point_segmentation.tif')[0]
        
    #     map_data.generate_point_geometry(Provenance(name='test', version='0.1'))
    #     # Just testing that the function executes without error
    #     assert True

