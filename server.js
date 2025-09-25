// server.js (ESM - "type":"module" in package.json)
import express from "express";
import nodejieba from "nodejieba";
import kuromoji from "kuromoji";
import { franc } from "franc";
import langs from "langs";
import { loadModule } from "cld3-asm";

const app = express();
app.use(express.json());

let cldFactory;
let cldIdent;
let jaTokenizer;

// helper loaders
async function initCLD3() {
  cldFactory = await loadModule(); // load wasm
  cldIdent = cldFactory.create(); // default params
  console.log("CLD3 loaded.");
}

function buildKuromoji() {
  return new Promise((resolve, reject) => {
    kuromoji
      .builder({ dicPath: "node_modules/kuromoji/dict" })
      .build((err, tokenizer) => {
        if (err) return reject(err);
        jaTokenizer = tokenizer;
        console.log("Kuromoji loaded.");
        resolve();
      });
  });
}

// Unicode script checks (Node 18 supports \p{Script=...})
const hasHiragana = (text) => /\p{Script=Hiragana}/u.test(text);
const hasKatakana = (text) => /\p{Script=Katakana}/u.test(text);
const hasHangul = (text) => /\p{Script=Hangul}/u.test(text);
const hasHan = (text) => /\p{Script=Han}/u.test(text);

// map possibly 3-letter codes -> 2-letter
function toIso2(code) {
  if (!code) return "und";
  // clean BCP47 like 'zh-CN' -> 'zh'
  const base = code.split("-")[0].toLowerCase();
  if (base.length === 2) return base;
  // try map 3->1 via langs
  const obj = langs.where("3", base);
  if (obj && obj["1"]) return obj["1"];
  return "und";
}

async function detectLang(text, hint) {
  if (!text || !text.trim()) return { lang: "und", method: "empty" };

  // 1) quick script heuristics
  if (hasHiragana(text) || hasKatakana(text))
    return { lang: "ja", method: "script" };
  if (hasHangul(text)) return { lang: "ko", method: "script" };

  // 2) if mostly Han characters (CJK) prefer CLD3
  const isCJK = hasHan(text);

  // 3) Try CLD3 (good for short text)
  try {
    if (cldIdent) {
      const r = cldIdent.findLanguage(text);
      if (r && r.language) {
        const prob = r.probability ?? 0;
        const lang2 = toIso2(r.language);
        // accept when high confidence or CJK case where CLD3 is reliable
        if (prob >= 0.7)
          return { lang: lang2, method: "cld3", confidence: prob };
      }
    }
  } catch (e) {
    console.warn("CLD3 error:", e.message || e);
  }

  // 4) fallback to franc (but require longer input)
  try {
    const francOpts = { minLength: 3 };
    const lang3 = franc(text, francOpts); // may return 'und'
    const lang2 = toIso2(lang3);
    if (lang2 !== "und") return { lang: lang2, method: "franc" };
  } catch (e) {
    console.warn("franc error:", e.message || e);
  }

  // 5) final fallback: if has Han but CLD3 failed, assume 'zh' (or und)
  if (isCJK) return { lang: "zh", method: "heuristic" };

  return { lang: "und", method: "none" };
}

async function start() {
  await initCLD3();
  await buildKuromoji();

  app.post("/segment", async (req, res) => {
    const { text, hint } = req.body;
    if (!text) return res.status(400).json({ error: "Missing text" });

    const det = await detectLang(text, hint);
    const lang = det.lang;

    try {
      let words = [];
      if (lang === "zh") {
        words = nodejieba.cut(text);
      } else if (lang === "ja") {
        if (!jaTokenizer)
          return res
            .status(503)
            .json({ error: "Japanese tokenizer not ready" });
        words = jaTokenizer.tokenize(text).map((t) => t.surface_form);
      } else {
        const segmenter = new Intl.Segmenter(lang === "und" ? "und" : lang, {
          granularity: "word",
        });
        words = [...segmenter.segment(text)].map((s) => s.segment);
      }

      res.json({ detected: det, words });
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: err.message });
    }
  });

  app.listen(3000, () => console.log("Server listening on :3000"));
}

start().catch((err) => {
  console.error(err);
  process.exit(1);
});
