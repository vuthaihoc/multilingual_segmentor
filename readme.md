# Text Segmentation API

API này cung cấp các endpoint để tách câu và từ (tokenization) cho nhiều ngôn ngữ: tiếng Việt, tiếng Trung, tiếng Nhật, tiếng Hàn và tiếng Anh.  

---

## 📦 Yêu cầu

- Python 3.9+
- Thư viện:

```text
fastapi>=0.95.0
uvicorn>=0.22.0
langid>=1.1.6
jieba>=0.42.1
fugashi>=1.2.1
unidic-lite>=1.0.8
konlpy>=0.6.0
nltk>=3.8.1
pycountry>=22.3.5
underthesea>=1.3.4
````

Cài đặt tất cả thư viện:

```bash
pip install -r requirements.txt
```

---

## 🚀 Khởi chạy server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ chạy trên: `http://localhost:8000`

---

## 📝 Input Model

Cả 2 API đều sử dụng cùng định dạng input JSON:

```json
{
  "text": "Đoạn văn hoặc câu cần tách từ.",
  "language_code": "vi",    // tùy chọn, override detect
  "force_nltk": false        // tùy chọn, nếu true luôn dùng NLTK tokenizer
}
```

* `text`: đoạn văn hoặc câu muốn segment.
* `language_code`: mã ngôn ngữ 2 ký tự ISO-639-1 (nếu không truyền, hệ thống sẽ detect tự động).
* `force_nltk`: nếu `true`, sẽ dùng NLTK tokenizer cho tất cả ngôn ngữ.

---

## 📌 API Endpoints

### 1. `/segment`

Tách **một câu hoặc một đoạn ngắn** thành tokens (từ).

* **Method:** POST
* **URL:** `/segment`
* **Request Example:**

```json
{
  "text": "Xin chào thế giới!",
  "language_code": "vi",
  "force_nltk": false
}
```

* **Response Example:**

```json
{
  "language_code": "vi",
  "force_nltk": false,
  "tokens": ["Xin", "chào", "thế", "giới", "!"]
}
```

---

### 2. `/paragraph/segment`

Tách **một đoạn văn dài** thành câu, sau đó tách từ từng câu.

* **Method:** POST
* **URL:** `/paragraph/segment`
* **Request Example:**

```json
{
  "text": "Xin chào! Tôi tên là ChatGPT. Rất vui được gặp bạn.",
  "language_code": "vi",
  "force_nltk": false
}
```

* **Response Example:**

```json
{
  "language_code": "vi",
  "force_nltk": false,
  "sentences": [
    {
      "sentence": "Xin chào!",
      "tokens": ["Xin", "chào", "!"]
    },
    {
      "sentence": "Tôi tên là ChatGPT.",
      "tokens": ["Tôi", "tên", "là", "ChatGPT", "."]
    },
    {
      "sentence": "Rất vui được gặp bạn.",
      "tokens": ["Rất", "vui", "được", "gặp", "bạn", "."]
    }
  ]
}
```

---

## 🔧 Lưu ý

* Hỗ trợ các ngôn ngữ:

  * Tiếng Việt (`vi`) → `underthesea`
  * Tiếng Trung (`zh`) → `jieba`
  * Tiếng Nhật (`ja`) → `fugashi`
  * Tiếng Hàn (`ko`) → `konlpy.Okt`
  * Tiếng Anh và các ngôn ngữ khác → `nltk`

* `language_code` mặc định được detect bằng `langid.py`.

* `force_nltk=True` sẽ bỏ qua detect và tokenizers riêng theo ngôn ngữ, luôn dùng NLTK.

---

## ⚡ Test nhanh với `curl`

```bash
curl -X POST "http://localhost:8000/segment" \
-H "Content-Type: application/json" \
-d '{"text":"Xin chào thế giới!","language_code":"vi"}'

curl -X POST "http://localhost:8000/paragraph/segment" \
-H "Content-Type: application/json" \
-d '{"text":"Xin chào! Tôi tên là ChatGPT.","language_code":"vi"}'
```

---

## 📚 Tài liệu

* [FastAPI](https://fastapi.tiangolo.com/)
* [NLTK](https://www.nltk.org/)
* [Underthesea](https://github.com/underthesea/underthesea)
* [jieba](https://github.com/fxsjy/jieba)
* [Fugashi](https://pypi.org/project/fugashi/)
* [Konlpy](https://konlpy.org/en/latest/)
* [langid.py](https://github.com/saffsd/langid.py)

```

---