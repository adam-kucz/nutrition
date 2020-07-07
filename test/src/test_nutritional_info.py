from pathlib import Path

import base
import nutritional_info


class TestReadout(base.AdvancedTestCase):
    def test_read_basic(self):
        filepath = \
            Path(__file__).parent / "data" / "nutritional-info-test-1.csv"
        filecontent = (
            "potato,tomato,vegetable\n"
            "sugar,carbohydrate,starch\n"
            "salt\n"
            "\n"
            "water,h2o,H2O\n")
        filepath.write(filecontent)
        result = nutritional_info.read_names(filepath)
        expected = {
            'potato': 'potato',
            'tomato': 'potato',
            'vegetable': 'potato',
            'sugar': 'sugar',
            'carbohydrate': 'sugar',
            'starch': 'sugar',
            'salt': 'salt',
            'water': 'water',
            'h2o': 'water',
            'H2O': 'water'}
        self.assertSameElements(result.items(), expected.items())
