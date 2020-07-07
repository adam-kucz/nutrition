from pathlib import Path

import test.src.base as base
import src.nutritional_info as info


class TestReadout(base.AdvancedTestCase):
    def test_read_basic(self):
        filepath = \
            Path(__file__).parent.parent / "data" / "nutritional-info-test-1.csv"
        filecontent = (
            "potato,tomato,vegetable\n"
            "sugar,carbohydrate,starch\n"
            "salt\n"
            "\n"
            "water,h2o,H2O\n")
        filepath.write_text(filecontent)
        result = info.read_names(filepath)
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
