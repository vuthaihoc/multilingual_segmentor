# Text Segmentation API

API phân đoạn (tokenize) văn bản theo ngôn ngữ, hỗ trợ tiếng:

- Tiếng Việt (via `underthesea`)
- Tiếng Trung (via `jieba`)
- Tiếng Nhật (via `fugashi`)
- Tiếng Hàn (via `KoNLPy`)
- Các ngôn ngữ khác (via `nltk`)

API hỗ trợ:

- Phân đoạn 1 đoạn text (`/segment`)
- Phân đoạn theo câu (`/paragraph/segment`)
- Phân đoạn bulk nhiều đoạn text cùng lúc (`/bulk/segment`)

---

## 1️⃣ Cài đặt

```bash
# Clone repo
git clone <repo-url>
cd <repo-folder>

# Tạo virtualenv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Cài dependencies
pip install fastapi uvicorn langid pycountry jieba fugashi konlpy nltk underthesea
```

> Lưu ý: `konlpy` yêu cầu Java JDK.
> `fugashi` yêu cầu `mecab` cài sẵn trên hệ thống.

---

## 2️⃣ Chạy server

```bash
uvicorn main:app --reload
```

Server sẽ chạy ở `http://127.0.0.1:8000`

---

## 3️⃣ Endpoints

### `/segment`

- Phân đoạn 1 đoạn text
- **Method:** POST
- **Body:**

```json
{
  "text": "văn bản cần phân đoạn",
  "language_code": "zh",    # tuỳ chọn, nếu bỏ trống sẽ tự detect
  "force_nltk": false       # tuỳ chọn, ép dùng nltk
}
```

- **Response:**

```json
{
  "language_code": "zh",
  "force_nltk": false,
  "tokens": ["突然间", "，", "一切", "都", "崩塌", "了"]
}
```

---

### `/paragraph/segment`

- Tách câu và phân đoạn theo câu
- **Method:** POST
- **Body:** giống `/segment`
- **Response:**

```json
{
  "language_code": "vi",
  "force_nltk": false,
  "sentences": [
    {
      "sentence": "Hôm nay trời đẹp.",
      "tokens": ["Hôm", "nay", "trời", "đẹp", "."]
    },
    {
      "sentence": "Chúng ta đi công viên nhé?",
      "tokens": ["Chúng", "ta", "đi", "công", "viên", "nhé", "?"]
    }
  ]
}
```

---

### `/bulk/segment`

- Phân đoạn nhiều đoạn text cùng lúc
- **Method:** POST
- **Body:**

```json
{
  "items": [
    { "text": "Xin chào, tôi là ChatGPT." },
    { "text": "突然间，一切都崩塌了" },
    { "text": "こんにちは、元気ですか？" },
    { "text": "오늘 날씨가 좋네요" }
  ]
}
```

- **Response:**

```json
{
  "results": [
    {
      "language_code": "vi",
      "force_nltk": false,
      "tokens": ["Xin", "chào", ",", "tôi", "là", "ChatGPT", "."],
      "text": "Xin chào, tôi là ChatGPT."
    },
    {
      "language_code": "zh",
      "force_nltk": false,
      "tokens": ["突然间", "，", "一切", "都", "崩塌", "了"],
      "text": "突然间，一切都崩塌了"
    },
    {
      "language_code": "ja",
      "force_nltk": false,
      "tokens": ["こんにちは", "元気", "です", "か", "？"],
      "text": "こんにちは、元気ですか？"
    },
    {
      "language_code": "ko",
      "force_nltk": false,
      "tokens": ["오늘", "날씨", "가", "좋네요"],
      "text": "오늘 날씨가 좋네요"
    }
  ]
}
```

---

## 4️⃣ Ví dụ curl

### 4.1 Tiếng Trung

```bash
curl -X POST "http://127.0.0.1:8000/bulk/segment" \
-H "Content-Type: application/json" \
-d '{
  "items": [{"text": "突然间，一切都崩塌了"}]
}'
```

### 4.2 Tiếng Nhật

```bash
curl -X POST "http://127.0.0.1:8000/bulk/segment" \
-H "Content-Type: application/json" \
-d '{
  "items": [{"text": "今日はとても良い天気です"}]
}'
```

### 4.3 Tiếng Hàn

```bash
curl -X POST "http://127.0.0.1:8000/bulk/segment" \
-H "Content-Type: application/json" \
-d '{
  "items": [{"text": "오늘 날씨가 좋네요"}]
}'
```
