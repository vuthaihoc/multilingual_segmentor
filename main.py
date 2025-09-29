from fastapi import FastAPI
from pydantic import BaseModel
import langid
import pycountry
import jieba
from fugashi import GenericTagger
from konlpy.tag import Okt
import nltk
from underthesea import sent_tokenize as vi_sent_tokenize, word_tokenize as vi_word_tokenize

nltk.download("punkt", quiet=True)

app = FastAPI()

# init tokenizer
ja_tagger = GenericTagger()
ko_tagger = Okt()

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

def segment_text_by_lang(text: str, lang_code: str, force_nltk: bool):
    if force_nltk:
        return nltk.word_tokenize(text)
    if lang_code == "zh":
        return list(jieba.cut(text))
    elif lang_code == "ja":
        return [word.surface for word in ja_tagger(text)]
    elif lang_code == "ko":
        return ko_tagger.morphs(text)
    elif lang_code == "vi":
        return vi_word_tokenize(text)
    else:
        return nltk.word_tokenize(text)

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
        "tokens": tokens
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
        "sentences": segmented_sentences
    }
