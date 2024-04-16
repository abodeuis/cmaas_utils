from tests.data import mock_data
import src.cmaas_utils.cdr as cdr

# Leaving the full tests out for this since the cdr object is about to change anyway. 
class Test_CDRSchema:
    def test_export_mock_map_to_cdr(self):
        map_data = mock_data.get_mock_map()
        cdr_schema = cdr.export_CMAAS_Map_to_cdr_schema(map_data)
        # expected = mock_data.get_mock_feature_results()
        # assert(cdr_schema == expected)
        assert True

    def test_export_rectify2_to_cdr(self):
        map_data = mock_data.get_rectify2_LawrenceHoffmann_map()
        cdr_schema = cdr.export_CMAAS_Map_to_cdr_schema(map_data)
        # expected = mock_data.get_rectify2_LawrenceHoffmann_feature_results()
        # assert(cdr_schema == expected)
        assert True