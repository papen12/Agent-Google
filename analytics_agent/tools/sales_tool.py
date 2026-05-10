
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "sales_data.csv"

def get_business_data() -> str:
    """
     Extrae los datos existentes en un csv con datos de ventas de la empresa.
    """

    return CSV_PATH.read_text(encoding="utf-8")