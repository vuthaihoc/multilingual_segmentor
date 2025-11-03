# FastAPI Text Segmentation & Transliteration API

API này cung cấp các endpoint để:

- Tách từ (tokenize) cho nhiều ngôn ngữ: **Tiếng Trung, Nhật, Hàn, Việt, và các ngôn ngữ khác**
- Tách câu và tokenize từng câu
- **Transliteration** cho CJK (Chinese / Japanese / Korean) tương ứng với mỗi token
- Hỗ trợ **bulk processing** cho nhiều đoạn text cùng lúc

---

## 📦 Yêu cầu

- Python ≥ 3.10
- FastAPI
- langid
- nltk
- jieba
- fugashi
- konlpy
- underthesea
- pypinyin
- pykakasi
- hgtk

---

### `requirements.txt` ví dụ

```
fastapi
uvicorn
langid
nltk
jieba
fugashi
konlpy
underthesea
pypinyin==0.55.0
pykakasi==2.3.0
hgtk==0.2.1
```

---

## 🚀 Cài đặt & chạy server

```bash
pip install -r requirements.txt

# chạy server
uvicorn main:app --reload
```

Mặc định API sẽ chạy tại `http://127.0.0.1:8000`.

---

## 📌 Endpoints

### 1. `/segment` — tokenize 1 đoạn text

**Request JSON:**

```json
{
  "text": "突然间，一切都崩塌了",
  "language_code": "zh",
  "force_nltk": false
}
```

**Response JSON:**

```json
{
  "language_code": "zh",
  "force_nltk": false,
  "tokens": [
    { "token": "突然间", "transliteration": "turanjian" },
    { "token": "，", "transliteration": "，" },
    { "token": "一切", "transliteration": "yiqie" },
    { "token": "都", "transliteration": "dou" },
    { "token": "崩塌", "transliteration": "bengta" },
    { "token": "了", "transliteration": "le" }
  ]
}
```

---

### 2. `/paragraph/segment` — tách câu + tokenize từng câu

**Request JSON:**

```json
{
  "text": "Xin chào. Tôi là ChatGPT.",
  "language_code": "vi"
}
```

**Response JSON:**

```json
{
  "language_code": "vi",
  "force_nltk": false,
  "sentences": [
    {
      "sentence": "Xin chào.",
      "tokens": [
        { "token": "Xin", "transliteration": "Xin" },
        { "token": "chào", "transliteration": "chào" },
        { "token": ".", "transliteration": "." }
      ]
    },
    {
      "sentence": "Tôi là ChatGPT.",
      "tokens": [
        { "token": "Tôi", "transliteration": "Tôi" },
        { "token": "là", "transliteration": "là" },
        { "token": "ChatGPT", "transliteration": "ChatGPT" },
        { "token": ".", "transliteration": "." }
      ]
    }
  ]
}
```

---

### 3. `/bulk/segment` — tokenize nhiều đoạn text cùng lúc

**Request JSON:**

```json
{
  "items": [
    { "text": "突然间，一切都崩塌了" },
    { "text": "こんにちは、元気ですか？" },
    { "text": "안녕하세요" }
  ]
}
```

**Response JSON:**

```json
{
  "results": [
    {
      "language_code": "zh",
      "force_nltk": false,
      "tokens": [
        { "token": "突然间", "transliteration": "turanjian" },
        { "token": "，", "transliteration": "，" },
        { "token": "一切", "transliteration": "yiqie" },
        { "token": "都", "transliteration": "dou" },
        { "token": "崩塌", "transliteration": "bengta" },
        { "token": "了", "transliteration": "le" }
      ]
    },
    {
      "language_code": "ja",
      "force_nltk": false,
      "tokens": [
        { "token": "こんにちは", "transliteration": "konnichiwa" },
        { "token": "、", "transliteration": "、" },
        { "token": "元気", "transliteration": "genki" },
        { "token": "です", "transliteration": "desu" },
        { "token": "か", "transliteration": "ka" },
        { "token": "？", "transliteration": "？" }
      ]
    },
    {
      "language_code": "ko",
      "force_nltk": false,
      "tokens": [{ "token": "안녕하세요", "transliteration": "annyeonghaseyo" }]
    }
  ]
}
```

---

### 4. Ví dụ `curl` sử dụng inline JSON

```bash
curl -X POST "http://127.0.0.1:8000/bulk/segment" \
     -H "Content-Type: application/json" \
     -d '{
           "items": [
             {"text": "突然间，一切都崩塌了"},
             {"text": "こんにちは、元気ですか？"},
             {"text": "안녕하세요"}
           ]
         }'
```
