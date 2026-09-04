import pandas as pd
import io
from typing import Union, Tuple, Optional

def load_file(file_or_path: Union[str, io.BytesIO, io.StringIO], filename: Optional[str] = None) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Safely load CSV or Excel dataset into Pandas DataFrame.
    Returns (df, error_message).
    """
    try:
        name = filename or (file_or_path if isinstance(file_or_path, str) else getattr(file_or_path, 'name', ''))
        name_lower = name.lower()

        if name_lower.endswith('.xlsx') or name_lower.endswith('.xls'):
            df = pd.read_excel(file_or_path, engine='openpyxl' if name_lower.endswith('.xlsx') else None)
            return df, None

        # CSV reading with encoding fallbacks
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        for enc in encodings:
            try:
                if isinstance(file_or_path, (io.BytesIO, io.StringIO)):
                    file_or_path.seek(0)
                df = pd.read_csv(file_or_path, encoding=enc)
                return df, None
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue

        return None, "Unable to decode CSV file. Please ensure it is saved in UTF-8 or standard CSV format."

    except Exception as e:
        return None, f"Failed to load file: {str(e)}"
