import express from "express";
import nodejieba from "nodejieba";
import kuromoji from "kuromoji";
import { franc } from "franc";
import iso6393to1 from "iso-639-3-to-1";
import langs from "langs";

const app = express();
app.use(express.json());

let jaTokenizer;

// khởi tạo tokenizer cho Nhật
kuromoji
  .builder({ dicPath: "node_modules/kuromoji/dict" })
  .build((err, tokenizer) => {
    if (err) {
      console.error("Error initializing kuromoji:", err);
      process.exit(1);
    }
    jaTokenizer = tokenizer;
    console.log("Kuromoji tokenizer loaded.");
  });

// bảng country mặc định (có thể mở rộng)
const defaultCountries = {
  zh: "CN",
  ja: "JP",
  ko: "KR",
  en: "US",
  vi: "VN",
  fr: "FR",
  pt: "BR",
};

function detectLang(text) {
  const iso3 = franc(text, { minLength: 2 }); // eg: "cmn", "jpn", "eng"
  if (iso3 === "und") return { language: "und", country: null };

  // convert ISO639-3 → ISO639-1
  const iso1 = iso6393to1(iso3) || iso3;

  // check hợp lệ (langs lib)
  const langData = langs.where("1", iso1);
  if (!langData) return { language: iso1, country: null };

  const country = defaultCountries[iso1] || null;

  return { language: iso1, country };
}

app.post("/segment", (req, res) => {
  const { text } = req.body;
  if (!text) return res.status(400).json({ error: "Missing text" });

  const { language, country } = detectLang(text);
  let words = [];

  try {
    if (language === "zh") {
      words = nodejieba.cut(text);
    } else if (language === "ja") {
      if (!jaTokenizer)
        return res.status(503).json({ error: "Japanese tokenizer not ready" });
      words = jaTokenizer.tokenize(text).map((t) => t.surface_form);
    } else {
      const segmenter = new Intl.Segmenter(language || "und", {
        granularity: "word",
      });
      words = [...segmenter.segment(text)].map((seg) => seg.segment);
    }

    res.json({ language, country, words });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});

app.listen(3000, () => {
  console.log("API server running at http://localhost:3000");
});
