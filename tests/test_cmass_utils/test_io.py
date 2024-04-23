import pytest
import os
import copy
import numpy as np
from pathlib import Path
from rasterio.crs import CRS
from rasterio.transform import Affine

from tests.data import mock_data
from src.cmaas_utils.types import CMAAS_Map, GeoReference, Legend, MapUnit, MapUnitType, Layout
import src.cmaas_utils.io as io

def exec_loadLegendJson(filepath:Path, expected:Legend):
    result = io.loadLegendJson(filepath)
    assert result == expected

    # Poly Data Filter
    expected_poly = copy.deepcopy(expected)
    [expected_poly.features.remove(f) for f in expected.features if f.type != MapUnitType.POLYGON]
    result = io.loadLegendJson(filepath, type_filter=[MapUnitType.POLYGON])
    assert result == expected_poly

    # Line Data Filter
    expected_line = copy.deepcopy(expected)
    [expected_line.features.remove(f) for f in expected.features if f.type != MapUnitType.LINE]
    result = io.loadLegendJson(filepath, type_filter=[MapUnitType.LINE])
    assert result == expected_line

    # Point Data Filter
    expected_point = copy.deepcopy(expected)
    [expected_point.features.remove(f) for f in expected.features if f.type != MapUnitType.POINT]
    result = io.loadLegendJson(filepath, type_filter=[MapUnitType.POINT])
    assert result == expected_point

    # Not Unknown Data
    expected_known = copy.deepcopy(expected)
    [expected_known.features.remove(f) for f in expected.features if f.type == MapUnitType.UNKNOWN]
    result = io.loadLegendJson(filepath, type_filter=[MapUnitType.POINT, MapUnitType.LINE, MapUnitType.POLYGON])
    assert result == expected_known

def exec_loadUSGSLegendJson(filepath:Path, expected:Legend):
    # Full Data
    result = io._loadUSGSLegendJson(filepath)
    assert result == expected

    # Poly Data Filter
    expected_poly = copy.deepcopy(expected)
    [expected_poly.features.remove(f) for f in expected.features if f.type != MapUnitType.POLYGON]
    result = io._loadUSGSLegendJson(filepath, type_filter=[MapUnitType.POLYGON])
    assert result == expected_poly

    # Line Data Filter
    expected_line = copy.deepcopy(expected)
    [expected_line.features.remove(f) for f in expected.features if f.type != MapUnitType.LINE]
    result = io._loadUSGSLegendJson(filepath, type_filter=[MapUnitType.LINE])
    assert result == expected_line

    # Point Data Filter
    expected_point = copy.deepcopy(expected)
    [expected_point.features.remove(f) for f in expected.features if f.type != MapUnitType.POINT]
    result = io._loadUSGSLegendJson(filepath, type_filter=[MapUnitType.POINT])
    assert result == expected_point

    # Not Unknown Data
    expected_known = copy.deepcopy(expected)
    [expected_known.features.remove(f) for f in expected.features if f.type == MapUnitType.UNKNOWN]
    result = io._loadUSGSLegendJson(filepath, type_filter=[MapUnitType.POINT, MapUnitType.LINE, MapUnitType.POLYGON])
    assert result == expected_known

class Test_USGSLegendData:
    usgs_legend_dir = 'tests/data/legends'

    # mock_usgs_data.json
    def test_load_mock_legend(self):
        testfile = os.path.join(self.usgs_legend_dir, 'mock_usgs_data.json')
        expected = mock_data.get_mock_usgs_legend()
        exec_loadUSGSLegendJson(testfile, expected)
        exec_loadLegendJson(testfile, expected)
        
    # 46_Coosa_2015_11 74.json # v5.0.1
    def test_load_coosa_legend(self):
        testfile = os.path.join(self.usgs_legend_dir,'46_Coosa_2015_11 74.json')
        expected = mock_data.get_46_coosa_2015_11_75_legend()
        exec_loadUSGSLegendJson(testfile, expected)
        exec_loadLegendJson(testfile, expected)

    # JosCtyOR.json # v5.0.2 # Good test for check if stuff works with only one type 
    def test_load_josCtyOR_legend(self):
        test_file = os.path.join(self.usgs_legend_dir,'JosCtyOR.json')
        expected = mock_data.get_josCtyOR_legend()
        exec_loadUSGSLegendJson(test_file, expected)
        exec_loadLegendJson(test_file, expected)

    # rectify2_LawrenceHoffmann.json # v5.0.2
    def test_load_rectify2_legend(self):
        testfile = os.path.join(self.usgs_legend_dir,'rectify2_LawrenceHoffmann.json')
        expected = mock_data.get_rectify2_LawrenceHoffmann_map().legend
        exec_loadUSGSLegendJson(testfile, expected)
        exec_loadLegendJson(testfile, expected)

    # TODO ParallelLoadLegends Test

def exec_loadLayoutJson(filepath:Path, expected:Layout):
    result = io.loadLayoutJson(filepath)
    assert result == expected

def exec_loadUnchartedLayoutv1Json(filepath:Path, expected:Layout):
    result = io._loadUnchartedLayoutv1Json(filepath)
    assert result == expected

def exec_loadUnchartedLayoutv2Json(filepath:Path, expected:Layout):
    result = io._loadUnchartedLayoutv2Json(filepath)
    assert result == expected

class Test_LayoutData:
    layout_dir = 'tests/data/layouts'

    # mock_layout_v1.json
    def test_load_mock_layout_v1(self):
        testfile = os.path.join(self.layout_dir, 'mock_layout_v1.json')
        expected = mock_data.get_mock_uncharted_layout()
        exec_loadUnchartedLayoutv1Json(testfile, expected)
        exec_loadLayoutJson(testfile, expected)

    # mock_layout_v2.json
    def test_load_mock_layout_v2(self):
        testfile = os.path.join(self.layout_dir, 'mock_layout_v2.json')
        expected = mock_data.get_mock_uncharted_layout()
        expected.provenance.version = '0.2'
        exec_loadUnchartedLayoutv2Json(testfile, expected)
        exec_loadLayoutJson(testfile, expected)

    def test_load_rectify2_layout(self):
        testfile = os.path.join(self.layout_dir, 'rectify2_LawrenceHoffmann.json')
        expected = mock_data.get_rectify2_LawrenceHoffmann_map().layout
        exec_loadUnchartedLayoutv1Json(testfile, expected)
        exec_loadLayoutJson(testfile, expected)

    # TODO ParallelLoadLayouts Test

def exec_loadGeoTiff(filepath:Path, expected:tuple):
    # Just checking if the shape is correct.
    image, crs, transform = io.loadGeoTiff(filepath)
    assert image.shape == expected
    assert type(crs) == CRS
    assert type(transform) == Affine

class Test_GeoTiffData:
    geotiff_dir = 'tests/data/images'

    # Rectify2_LawrenceHoffmann.tif # 3 channel map
    def test_load_rectify2(self):
        filepath = os.path.join(self.geotiff_dir, 'rectify2_LawrenceHoffmann.tif')
        expected = (3, 3791, 5476)
        exec_loadGeoTiff(filepath, expected)

    # DMEA2328_OldLeydenMine_CO.tif # single channel map # This map also doesn't have a crs or transform
    def test_load_OldLeydenMine(self):
        filepath = os.path.join(self.geotiff_dir, 'DMEA2328_OldLeydenMine_CO.tif')
        expected = (1, 11897, 8344)
        image, _, _ = io.loadGeoTiff(filepath)
        assert image.shape == expected

    # AZ_PrescottNF.tif # Largest map
    def test_load_AZ_PrescottNF(self):
        filepath = os.path.join(self.geotiff_dir, 'AZ_PrescottNF.tif')
        expected = (3, 15450, 22800)
        exec_loadGeoTiff(filepath, expected)

def exec_loadCMASSMap(image_path:Path, expected:CMAAS_Map, legend_path:Path=None, layout_path:Path=None, georef_path:Path=None, metadata_path:Path=None):
    map_data = io.loadCMAASMapFromFiles(image_path, legend_path, layout_path, georef_path, metadata_path)
    assert map_data == expected

def exec_loadCMASSMapMule(json_path:Path, expected:CMAAS_Map, image_path:Path=None):
    map_data = io.loadCMAASMap(json_path, image_path=image_path)
    assert map_data == expected

class Test_MapData:
    image_dir = 'tests/data/images'
    legend_dir = 'tests/data/legends'
    layout_dir = 'tests/data/layouts'
    georef_dir = 'tests/data/georefs'
    metadata_dir = 'tests/data/metadata'
    mule_dir = 'tests/data/mule'

    # Individual file load
    def test_load_mock_map(self):
        expected = CMAAS_Map(name='mock_map_data')
        expected.image = np.zeros((3,100,100), dtype=np.uint8)
        expected.legend = mock_data.get_mock_usgs_legend()
        expected.layout = mock_data.get_mock_uncharted_layout()
        exec_loadCMASSMap(os.path.join(self.image_dir, 'mock_map_data.tif'), expected, os.path.join(self.legend_dir, 'mock_usgs_data.json'), os.path.join(self.layout_dir, 'mock_layout_v1.json'))

    # Rectify2_LawrenceHoffmann
    def test_load_rectify2(self):
        expected = mock_data.get_rectify2_LawrenceHoffmann_map()
        exec_loadCMASSMap(os.path.join(self.image_dir, 'rectify2_LawrenceHoffmann.tif'), expected, legend_path=os.path.join(self.legend_dir, 'rectify2_LawrenceHoffmann.json'), layout_path=os.path.join(self.layout_dir, 'rectify2_LawrenceHoffmann.json'))

    def test_save_geopackage_pixel(self):
        from src.cmaas_utils.types import Provenance
        map_data = CMAAS_Map(name='VA_Stanardsville')
        map_data.legend = io.loadLegendJson('tests/data/legends/VA_Stanardsville.json')
        map_data.poly_segmentation_mask = io.loadGeoTiff('tests/data/segmentations/VA_Stanardsville_poly_segmentation.tif')[0]
        
        map_data.generate_poly_geometry(Provenance(name='test', version='0.1'))
        io.saveGeoPackage('tests/data/tmp.gpkg', map_data, coord_type='pixel')
        assert True

    def test_save_geopackage_georeferenced(self):
        from src.cmaas_utils.types import Provenance
        map_data = io.loadCMAASMapFromFiles('tests/data/images/VA_Stanardsville.tif', legend_path='tests/data/legends/VA_Stanardsville.json')
        map_data.poly_segmentation_mask = io.loadGeoTiff('tests/data/segmentations/VA_Stanardsville_poly_segmentation.tif')[0]
        
        map_data.generate_poly_geometry(Provenance(name='test', version='0.1'))
        io.saveGeoPackage('tests/data/tmp.gpkg', map_data, coord_type='georeferenced')
        assert True
    # Mule file load
    # def test_load_mock_mule(self):
    #     expected = mock_data.get_mock_map()
    #     exec_loadCMASSMapMule(os.path.join(self.mule_dir, 'mock_mule_data.json'), expected, image_path=os.path.join(self.image_dir, 'mock_map_data.tif'))

# def print_2d_array(prefix, arr):
#     outstr = '['
#     for row in arr:
#         outstr += '['
#         for i in row:
#             outstr += f'{i},'
#         outstr = outstr[:-1] + '],'
#     outstr = outstr[:-1] + ']'
#     print(f'{prefix} = np.array({outstr})')

# def print_layout_data(layout):
#     print_2d_array('layout.map', layout.map) if layout.map is not None else None
#     print_2d_array('layout.correlation_diagram', layout.correlation_diagram) if layout.correlation_diagram is not None else None
#     print_2d_array('layout.cross_section', layout.cross_section) if layout.cross_section is not None else None
#     print_2d_array('layout.point_legend', layout.point_legend) if layout.point_legend is not None else None
#     print_2d_array('layout.line_legend', layout.line_legend) if layout.line_legend is not None else None
#     print_2d_array('layout.polygon_legend', layout.polygon_legend) if layout.polygon_legend is not None else None
    