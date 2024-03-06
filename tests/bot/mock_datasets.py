from aiogram import types
from aiogram_tests.types.dataset import MESSAGE_WITH_DOCUMENT, DatasetItem
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent / 'data'

DOCUMENT = DatasetItem(
    {
        "file_name": str(DATA_PATH / 'raw/test/0a89730f-c271-4429-8351-fdfb2daf6b81'),
        "mime_type": "video/quicktime",
        "file_id": "BQADAgADpgADy_JxS66XQTBRHFleAg",
        "file_unique_id": "file_unique_id",
        "file_size": 21331,
    },
    model=types.Document,
)

MESSAGE_WITH_DOCUMENT.data['document'] = DOCUMENT
