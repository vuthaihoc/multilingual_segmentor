from fastapi import FastAPI
from pydantic import BaseModel
import langid
import pycountry
import jieba
from fugashi import GenericTagger
from konlpy.tag import Okt
import nltk

nltk.download("punkt", quiet=True)

app = FastAPI()

# init tokenizer
ja_tagger = GenericTagger()
ko_tagger = Okt()

# optional: set languages to limit detection
langid.set_languages(['en', 'vi', 'zh', 'ja', 'ko'])

class TextInput(BaseModel):
    text: str
    language_code: str | None = None  # override detected language
    force_nltk: bool = False

def to_iso639_1(lang_code: str) -> str:
    """
    Convert langid.py code to ISO-639-1 2-letter code
    """
    try:
        # pycountry có thể không tìm thấy code, fallback giữ nguyên
        lang = pycountry.languages.get(alpha_2=lang_code)
        if lang:
            return lang.alpha_2
        # thử alpha_3
        lang = pycountry.languages.get(alpha_3=lang_code)
        if lang:
            return lang.alpha_2
    except:
        pass
    return lang_code[:2]  # fallback lấy 2 ký tự đầu

@app.post("/segment")
async def segment_text(input: TextInput):
    text = input.text
    force_nltk = input.force_nltk
    lang_code = input.language_code

    # detect language nếu chưa truyền vào
    if not lang_code:
        try:
            detected_code, confidence = langid.classify(text)
            lang_code = to_iso639_1(detected_code)
        except:
            lang_code = "und"

    tokens = []

    if force_nltk:
        tokens = nltk.word_tokenize(text)
    else:
        if lang_code == "zh":
            tokens = list(jieba.cut(text))
        elif lang_code == "ja":
            tokens = [word.surface for word in ja_tagger(text)]
        elif lang_code == "ko":
            tokens = ko_tagger.morphs(text)
        else:
            tokens = nltk.word_tokenize(text)

    return {
        "language_code": lang_code,
        "force_nltk": force_nltk,
        "tokens": tokens
    }
