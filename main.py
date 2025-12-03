from fastapi import FastAPI
from pydantic import BaseModel
import langid
import pycountry
import jieba
from fugashi import GenericTagger
from konlpy.tag import Okt
import nltk
from underthesea import sent_tokenize as vi_sent_tokenize, word_tokenize as vi_word_tokenize

from pypinyin import lazy_pinyin, Style
import pykakasi
from korean_romanizer.romanizer import Romanizer
import eng_to_ipa as ipa

nltk.download("punkt", quiet=True)

app = FastAPI()

# init tokenizer
ja_tagger = GenericTagger()
ko_tagger = Okt()

# khởi tạo transliteration cho JA
kks = pykakasi.kakasi()

style_map = {
    "TONE": Style.TONE,
    "NORMAL": Style.NORMAL,
    "TONE2": Style.TONE2
}


class TextInput(BaseModel):
    text: str
    language_code: str | None = None
    force_nltk: bool = False
    pinyin_style: str | None = None
    country_code: str | None = None  # US/UK

def get_ipa_espeak(word: str, country_code: str | None):
    return ipa.convert(word)

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


def transliterate_token(token: str, lang_code: str, pinyin_style: Style = Style.TONE,
                        country_code: str | None = None) -> str:
    if lang_code == "zh":
        return "".join(lazy_pinyin(token, style=pinyin_style))
    elif lang_code == "ja":
        result = kks.convert(token)
        return "".join([r['hepburn'] for r in result])
    elif lang_code == "ko":
        try:
            return Romanizer(token).romanize()
        except:
            return token
    elif lang_code == "en":  # NEW
        try:
            pronunciation = get_ipa_espeak(token, country_code)
            if pronunciation is None or pronunciation == token:
                return token
            return pronunciation
        except Exception:
            return token
    else:
        return token


def segment_text_by_lang(text: str, lang_code: str, force_nltk: bool, pinyin_style: Style = Style.TONE,
                         country_code: str | None = None):
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

    token_objs = []
    for tok in tokens:
        token_objs.append({
            "token": tok,
            "transliteration": transliterate_token(tok, lang_code, pinyin_style, country_code)
        })
    return token_objs


@app.post("/segment")
async def segment_text(req_input: TextInput):
    text = req_input.text
    force_nltk = req_input.force_nltk
    lang_code = req_input.language_code
    country_code = req_input.country_code

    if not lang_code:
        try:
            detected_code, confidence = langid.classify(text)
            lang_code = to_iso639_1(detected_code)
        except:
            lang_code = "und"

    pinyin_style = style_map.get(req_input.pinyin_style, Style.TONE)
    tokens = segment_text_by_lang(text, lang_code, force_nltk, pinyin_style)

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
    pinyin_style = style_map.get(input.pinyin_style, Style.TONE)

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
        tokens = segment_text_by_lang(sentence, lang_code, force_nltk, pinyin_style)
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
    language_code: str | None = None
    force_nltk: bool = False
    pinyin_style: str | None = None


@app.post("/bulk/segment")
async def bulk_segment(input: BulkTextInput):
    results = []
    for item in input.items:
        text = item.text
        force_nltk = item.force_nltk
        lang_code = item.language_code
        pinyin_style = style_map.get(input.pinyin_style, Style.TONE)

        if not lang_code:
            try:
                detected_code, confidence = langid.classify(text)
                lang_code = to_iso639_1(detected_code)
            except:
                lang_code = "und"

        tokens = segment_text_by_lang(text, lang_code, force_nltk, pinyin_style)
        results.append({
            "language_code": lang_code,
            "force_nltk": force_nltk,
            "tokens": tokens,
            "text": text
        })

    return {"results": results}
