from tests.data import mock_data
import src.cmaas_utils.cdr as cdr
from tests.utilities import init_test_log
import json
from cdr_schemas.cdr_responses.legend_items import LegendItemResponse
from cdr_schemas.cdr_responses.area_extractions import AreaExtractionResponse
from cdr_schemas.feature_results import FeatureResults

# Leaving the full tests out for this since the cdr object is about to change anyway. 
class Test_CDRSchema:
    def test_export_mock_map_to_cdr(self):
        log = init_test_log("Test_CDRSchema/test_export_mock_map_to_cdr")
        map_data = mock_data.get_mock_map()
        cdr_schema = cdr.exportMapToCDR(map_data, cog_id='1234', system='Unit testing', system_version='42')
        
        assert cdr_schema.cog_id == '1234'
        assert cdr_schema.system == 'Unit testing'
        assert cdr_schema.system_version == '42'
        assert len(cdr_schema.point_feature_results) == 1
        assert len(cdr_schema.line_feature_results) == 1
        assert len(cdr_schema.polygon_feature_results) == 1
        assert len(cdr_schema.cog_area_extractions) == 0
        

class Test_ConvertCDRToCMAAS:
    def test_convert_CDR_feature_results_to_cmass_map(self):
        log = init_test_log("Test_ConvertCDRToCMAAS/test_convert_CDR_feature_results_to_cmass_map")
        # Load sample data
        with open("tests/data/cdr/sample_cdr_feature_results.json") as fh:
            feature_results = FeatureResults.parse_raw(fh.read())
        # Convert to cmaas
        cmass_map = cdr.convert_cdr_feature_results_to_cmaas_map(feature_results)
        log.info (f"Converted Map : {cmass_map}")
        # Check data was converted correctly
        # assert cmass_map.provenance.name == 'uncharted-points'

    def test_convert_CDR_area_extraction_to_layout(self):
        log = init_test_log("Test_ConvertCDRToCMAAS/test_convert_CDR_area_extraction_to_layout")
        # Load smaple data
        with open("tests/data/cdr/sample_cdr_area_extraction.json") as fh:
            json_data = json.load(fh)
        cdr_area_extractions = []
        for item in json_data:
            cdr_area_extractions.append(AreaExtractionResponse.model_validate(item))
        # Convert to cmaas
        cmass_layout = cdr.convert_cdr_area_extraction_to_layout(cdr_area_extractions)
        log.info (f"Converted Layout : {cmass_layout}")
        # Check data was converted correctly
        assert cmass_layout.provenance.name == 'uncharted-area'

    def test_convert_CDR_legend_items_to_legend(self):
        log = init_test_log("Test_ConvertCDRToCMAAS/test_convert_CDR_legend_items_to_legend")
        # Load sample data
        with open("tests/data/cdr/sample_cdr_legend_items.json") as fh:
            json_data = json.load(fh)
        cdr_legend = []
        for item in json_data:
            cdr_legend.append(LegendItemResponse.model_validate(item))
        # Convert to cmaas
        cmass_legend = cdr.convert_cdr_legend_items_to_legend(cdr_legend)
        log.info (f"Converted Legend : {cmass_legend}")
        # Check data was converted correctly
        assert cmass_legend.provenance.name == 'uncharted-points'
        assert len(cmass_legend.features) == 104
        log.info("Test passed successfully")
        
    # def test_export_rectify2_to_cdr(self):
    #     map_data = mock_data.get_rectify2_LawrenceHoffmann_map()
    #     cdr_schema = cdr.exportMapToCDR(map_data)
    #     # expected = mock_data.get_rectify2_LawrenceHoffmann_feature_results()
    #     # assert(cdr_schema == expected)
    #     assert True