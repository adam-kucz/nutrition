A: InfoItem
B1: InfoItem [thiamin, thiamine]
B2: InfoItem [riboflavin]
B3: InfoItem [niacin]
B5: InfoItem [pantothenic_acid]
B6: InfoItem
H: InfoItem [biotin, vitamin_b7, vitamin_b8]
B9: InfoItem [folate]
B12: InfoItem
C: InfoItem
D2: InfoItem
D3: InfoItem
E: InfoItem
K1: InfoItem
K2: InfoItem
CHOLINE: InfoItem


class Macronutrient:
    fat: InfoItem
    saturated: InfoItem
    monounsaturated: InfoItem
    polyunsaturated: InfoItem
    carbohydrate: InfoItem
    sugar: InfoItem
    fibre: InfoItem
    protein: InfoItem
    salt: InfoItem
    omega_3: InfoItem
    omega_3_ala: InfoItem
    omega_6: InfoItem


class Minerals:
    postassium: InfoItem
    chloride: InfoItem
    calcium: InfoItem
    phosphorus: InfoItem
    magnesium: InfoItem
    iron: InfoItem
    zinc: InfoItem
    copper: InfoItem
    manganese: InfoItem
    selenium: InfoItem
    chromium: InfoItem
    molybdenum: InfoItem
    sodium: InfoItem
    iodine: InfoItem


class NutrientInfo:
    def __init__(self):
        energy: GeneralItem(EnergyUnit)
        cholesterol: InfoItem
        MCT: InfoItem
        trans_fat: InfoItem
        # lycopene: InfoItem -- no effect
        # lutein: InfoItem -- no effect
        # zeaxanthin: InfoItem -- unproven effects
