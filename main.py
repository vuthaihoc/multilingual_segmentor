from fastapi import FastAPI
from pydantic import BaseModel
import langid
import pycountry
import jieba
from fugashi import GenericTagger
from konlpy.tag import Okt
import nltk
from underthesea import sent_tokenize as vi_sent_tokenize, word_tokenize as vi_word_tokenize

from pypinyin import lazy_pinyin
import pykakasi
import hgtk

nltk.download("punkt", quiet=True)

app = FastAPI()

# init tokenizer
ja_tagger = GenericTagger()
ko_tagger = Okt()

# khởi tạo transliteration cho JA
kks = pykakasi.kakasi()

class TextInput(BaseModel):
    text: str
    language_code: str | None = None
    force_nltk: bool = False

def to_iso639_1(lang_code: str) -> str:
    try:
        lang = pycountry.languages.get(alpha_2=lang_code)
        if lang:
            return lang.alpha_2
        lang = pycountry.languages.get(alpha_3=lang_code)
        if lang:
            return lang.alpha_2
    except:
        pass
    return lang_code[:2]

def transliterate_token(token: str, lang_code: str) -> str:
    if lang_code == "zh":
        # pypinyin trả list, nối lại thành string cho token
        return "".join(lazy_pinyin(token))
    elif lang_code == "ja":
        result = ja_kakasi.convert(token)
        # lấy phần romaji của token
        return "".join([r['hepburn'] for r in result])
    elif lang_code == "ko":
        try:
            return hgtk.text.transliterate(token)
        except hgtk.exception.NotHangulException:
            return token
    else:
        return token  # các ngôn ngữ khác giữ nguyên


def segment_text_by_lang(text: str, lang_code: str, force_nltk: bool):
    if force_nltk:
        tokens = nltk.word_tokenize(text)
    elif lang_code == "zh":
        tokens = list(jieba.cut(text))
    elif lang_code == "ja":
        tokens = [word.surface for word in ja_tagger(text)]
    elif lang_code == "ko":
        tokens = ko_tagger.morphs(text)
    elif lang_code == "vi":
        tokens = vi_word_tokenize(text)
    else:
        tokens = nltk.word_tokenize(text)
    
    # thêm transliteration
    token_objs = []
    for tok in tokens:
        token_objs.append({
            "token": tok,
            "transliteration": transliterate_token(tok, lang_code)
        })
    return token_objs

@app.post("/segment")
async def segment_text(input: TextInput):
    text = input.text
    force_nltk = input.force_nltk
    lang_code = input.language_code

    if not lang_code:
        try:
            detected_code, confidence = langid.classify(text)
            lang_code = to_iso639_1(detected_code)
        except:
            lang_code = "und"

    tokens = segment_text_by_lang(text, lang_code, force_nltk)

    return {
        "language_code": lang_code,
        "force_nltk": force_nltk,
        "tokens": tokens,
        "text": text
    }

@app.post("/paragraph/segment")
async def paragraph_segment(input: TextInput):
    text = input.text
    force_nltk = input.force_nltk
    lang_code = input.language_code

    if not lang_code:
        try:
            detected_code, confidence = langid.classify(text)
            lang_code = to_iso639_1(detected_code)
        except:
            lang_code = "und"

    # tách câu
    if lang_code == "vi":
        sentences = vi_sent_tokenize(text)
    else:
        sentences = nltk.sent_tokenize(text)

    segmented_sentences = []

    for sentence in sentences:
        tokens = segment_text_by_lang(sentence, lang_code, force_nltk)
        segmented_sentences.append({
            "sentence": sentence,
            "tokens": tokens
        })

    return {
        "language_code": lang_code,
        "force_nltk": force_nltk,
        "sentences": segmented_sentences,
        "text": text
    }

# ------------------------
# 3️⃣ /bulk/segment (NEW)
# ------------------------
class BulkTextInput(BaseModel):
    items: list[TextInput]

@app.post("/bulk/segment")
async def bulk_segment(input: BulkTextInput):
    results = []
    for item in input.items:
        text = item.text
        force_nltk = item.force_nltk
        lang_code = item.language_code

        if not lang_code:
            try:
                detected_code, confidence = langid.classify(text)
                lang_code = to_iso639_1(detected_code)
            except:
                lang_code = "und"

        tokens = segment_text_by_lang(text, lang_code, force_nltk)
        results.append({
            "language_code": lang_code,
            "force_nltk": force_nltk,
            "tokens": tokens,
            "text": text
        })

    return {"results": results}