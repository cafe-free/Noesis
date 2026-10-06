import asyncio
import logging
import urllib.parse
from dataclasses import dataclass, field
from typing import Any

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = "NoesisLanguageApp/1.0 (educational app; contact: support@noesis.local)"

# Topic to Japanese vocabulary seeds mapping for contextual lookup
TOPIC_VOCAB_SEEDS: dict[str, list[str]] = {
    "food": ["食べる", "飲む", "美味しい", "ご飯", "お茶", "水", "レストラン", "メニュー", "注文"],
    "dining": ["食べる", "飲む", "美味しい", "ご飯", "お茶", "水", "レストラン", "メニュー", "注文"],
    "restaurant": ["注文", "メニュー", "お会計", "テーブル", "美味しい", "店員", "水", "乾杯"],
    "coffee": ["コーヒー", "喫茶店", "カフェ", "砂糖", "ミルク", "注文", "お会計", "席"],
    "cafe": ["コーヒー", "喫茶店", "カフェ", "砂糖", "ミルク", "注文", "お会計", "席"],
    "travel": ["旅行", "駅", "電車", "切符", "どこ", "行く", "空港", "ホテル", "地下鉄"],
    "direction": ["駅", "右", "左", "前", "後ろ", "どこ", "道", "曲がる", "近い"],
    "everyday": ["毎日", "起きる", "寝る", "行く", "来る", "友達", "家", "仕事", "勉強"],
    "life": ["毎日", "起きる", "寝る", "行く", "来る", "友達", "家", "生活", "学校"],
    "habit": ["毎日", "朝", "夜", "時々", "散歩", "読書", "運動", "食べる"],
    "hobby": ["趣味", "映画", "読書", "音楽", "写真", "スポーツ", "散歩", "料理"],
    "shopping": ["買い物", "値段", "いくら", "高い", "安い", "店", "買う", "お金"],
    "price": ["いくら", "円", "高い", "安い", "値段", "お金", "会計", "割引"],
    "family": ["家族", "父", "母", "両親", "兄", "姉", "弟", "妹", "友達"],
    "friend": ["友達", "親友", "会う", "遊ぶ", "話す", "一緒", "約束", "楽しい"],
    "greeting": ["おはよう", "こんにちは", "こんばんは", "ありがとう", "さようなら", "初めまして"],
}

DEFAULT_SEEDS = ["日本語", "友達", "毎日", "今日", "話す", "食べる", "行く", "ありがとう"]


@dataclass
class JapaneseVocabEntry:
    word: str
    kanji: str
    reading: str
    romaji: str | None = None
    meanings: list[str] = field(default_factory=list)
    parts_of_speech: list[str] = field(default_factory=list)
    jlpt_level: str | None = None
    is_common: bool = True
    usage_examples: list[str] = field(default_factory=list)
    wiktionary_summary: str = ""
    source_urls: list[str] = field(default_factory=list)


class JapaneseVocabService:
    def __init__(self, timeout: float = 6.0):
        self.timeout = timeout
        self.headers = {"User-Agent": USER_AGENT}
        # In-memory LRU cache of fetched entries
        self._cache: dict[str, JapaneseVocabEntry] = {}

    async def fetch_jisho(self, word: str) -> dict[str, Any] | None:
        """
        Fetches structured dictionary data from Jisho API:
        https://jisho.org/api/v1/search/words?keyword=${encodeURIComponent(word)}
        """
        encoded_word = urllib.parse.quote(word)
        url = f"https://jisho.org/api/v1/search/words?keyword={encoded_word}"

        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                res = await client.get(url)
                if res.status_code != 200:
                    logger.warning(f"Jisho API returned status {res.status_code} for '{word}'")
                    return None

                data = res.json()
                items = data.get("data", [])
                if not items:
                    return None

                # Find best matching item
                best_item = items[0]
                for it in items:
                    for jp in it.get("japanese", []):
                        if jp.get("word") == word or jp.get("reading") == word:
                            best_item = it
                            break

                japanese_entries = best_item.get("japanese", [{}])
                primary_jp = japanese_entries[0] if japanese_entries else {}
                kanji = primary_jp.get("word") or word
                reading = primary_jp.get("reading") or ""

                # Senses and meanings
                meanings: list[str] = []
                parts_of_speech: list[str] = []
                for sense in best_item.get("senses", []):
                    for defn in sense.get("english_definitions", []):
                        if defn not in meanings:
                            meanings.append(defn)
                    for pos in sense.get("parts_of_speech", []):
                        if pos not in parts_of_speech:
                            parts_of_speech.append(pos)

                # JLPT level
                jlpt_list = best_item.get("jlpt", [])
                jlpt = jlpt_list[0].replace("jlpt-", "").upper() if jlpt_list else None

                return {
                    "word": word,
                    "kanji": kanji,
                    "reading": reading,
                    "meanings": meanings[:5],
                    "parts_of_speech": parts_of_speech[:4],
                    "jlpt_level": jlpt,
                    "is_common": bool(best_item.get("is_common", False)),
                    "jisho_url": f"https://jisho.org/search/{encoded_word}",
                }

        except Exception as e:
            logger.warning(f"Failed to fetch Jisho API for '{word}': {e}")
            return None

    async def fetch_wiktionary(self, word: str) -> dict[str, Any] | None:
        """
        Fetches and extracts Japanese etymology, readings, and definitions from English Wiktionary:
        https://en.wiktionary.org/api/rest_v1/page/html/${encodeURIComponent(word)}
        """
        encoded_word = urllib.parse.quote(word)
        url = f"https://en.wiktionary.org/api/rest_v1/page/html/{encoded_word}"

        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                res = await client.get(url)
                if res.status_code != 200:
                    logger.warning(f"Wiktionary API returned status {res.status_code} for '{word}'")
                    return None

                html = res.text
                soup = BeautifulSoup(html, "html.parser")

                # Find the Japanese language section
                ja_header = soup.find(id="Japanese") or soup.find(
                    lambda t: t.name in ("h2", "h3") and "Japanese" in t.get_text()
                )
                if not ja_header:
                    return None

                ja_section = ja_header.find_parent("section") or ja_header.parent
                if not ja_section:
                    return None

                # Clean non-content tags in section
                for tag in ja_section.find_all(["style", "script", "noscript"]):
                    tag.decompose()

                # Extract example sentences
                examples: list[str] = []
                for li in ja_section.find_all("li"):
                    txt = li.get_text(separator=" ", strip=True)
                    if "―" in txt or ("—" in txt and len(txt) > 10) or (len(txt) > 15 and any(char in txt for char in ["。", "、"])):
                        examples.append(txt)

                # Extract cleaned summary text
                summary_lines = []
                for p in ja_section.find_all(["p", "ol", "ul"]):
                    line = p.get_text(separator=" ", strip=True)
                    if line and len(line) > 5 and not line.startswith("See also:"):
                        summary_lines.append(line)

                clean_summary = "\n".join(summary_lines[:8])

                return {
                    "word": word,
                    "wiktionary_summary": clean_summary,
                    "examples": examples[:4],
                    "wiktionary_url": f"https://en.wiktionary.org/wiki/{encoded_word}#Japanese",
                }

        except Exception as e:
            logger.warning(f"Failed to fetch Wiktionary API for '{word}': {e}")
            return None

    async def get_vocab_knowledge(self, word: str) -> JapaneseVocabEntry:
        """
        Fetches combined vocabulary knowledge from Jisho and Wiktionary APIs,
        with caching and graceful fallbacks.
        """
        clean_word = word.strip()
        if clean_word in self._cache:
            return self._cache[clean_word]

        # Concurrently fetch Jisho and Wiktionary
        jisho_task = self.fetch_jisho(clean_word)
        wik_task = self.fetch_wiktionary(clean_word)

        jisho_res, wik_res = await asyncio.gather(jisho_task, wik_task, return_exceptions=True)

        jisho_data = jisho_res if isinstance(jisho_res, dict) else None
        wik_data = wik_res if isinstance(wik_res, dict) else None

        kanji = jisho_data.get("kanji") if jisho_data else clean_word
        reading = jisho_data.get("reading") if jisho_data else ""
        meanings = jisho_data.get("meanings", []) if jisho_data else []
        pos = jisho_data.get("parts_of_speech", []) if jisho_data else []
        jlpt = jisho_data.get("jlpt_level") if jisho_data else None
        is_common = jisho_data.get("is_common", True) if jisho_data else True

        examples = wik_data.get("examples", []) if wik_data else []
        summary = wik_data.get("wiktionary_summary", "") if wik_data else ""

        urls = []
        if jisho_data and "jisho_url" in jisho_data:
            urls.append(jisho_data["jisho_url"])
        if wik_data and "wiktionary_url" in wik_data:
            urls.append(wik_data["wiktionary_url"])

        entry = JapaneseVocabEntry(
            word=clean_word,
            kanji=kanji,
            reading=reading or clean_word,
            meanings=meanings,
            parts_of_speech=pos,
            jlpt_level=jlpt,
            is_common=is_common,
            usage_examples=examples,
            wiktionary_summary=summary,
            source_urls=urls,
        )

        self._cache[clean_word] = entry
        return entry

    async def get_topic_knowledge(
        self, topic: str, level: str = "A1", count: int = 5
    ) -> list[JapaneseVocabEntry]:
        """
        Resolves Japanese vocabulary seeds based on topic and fetches
        verified knowledge from Jisho and Wiktionary.
        """
        t_lower = topic.lower()
        matched_seeds: list[str] = []

        for key, seeds in TOPIC_VOCAB_SEEDS.items():
            if key in t_lower:
                matched_seeds.extend(seeds)

        if not matched_seeds:
            matched_seeds = DEFAULT_SEEDS

        # Select unique candidates
        unique_seeds = list(dict.fromkeys(matched_seeds))[: max(3, count)]

        # Fetch knowledge concurrently
        tasks = [self.get_vocab_knowledge(w) for w in unique_seeds]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        entries: list[JapaneseVocabEntry] = []
        for r in results:
            if isinstance(r, JapaneseVocabEntry):
                entries.append(r)

        return entries

    def format_knowledge_for_quiz_prompt(self, entries: list[JapaneseVocabEntry]) -> str:
        """
        Formats authoritative Japanese vocabulary entries into structured context
        for prompt injection into the Gemini/Gemma quiz generator.
        """
        if not entries:
            return ""

        lines = [
            "AUTHORITATIVE JAPANESE VOCABULARY KNOWLEDGE (Sourced from Jisho.org & Wiktionary APIs):",
            "Use the following authentic Kanji, verified Furigana readings, and exact meanings for exercises:",
        ]

        for e in entries:
            meaning_str = ", ".join(e.meanings) if e.meanings else "N/A"
            pos_str = f" [{', '.join(e.parts_of_speech)}]" if e.parts_of_speech else ""
            jlpt_str = f" (JLPT {e.jlpt_level})" if e.jlpt_level else ""
            lines.append(
                f"- Word: {e.kanji} | Reading: {e.reading}{jlpt_str}{pos_str} | Meanings: {meaning_str}"
            )
            if e.usage_examples:
                lines.append(f"  Example: {e.usage_examples[0]}")

        lines.append("\nACCURACY ENFORCEMENT RULES FOR JAPANESE:")
        lines.append("- All correct options and exercises MUST strictly match the authentic Japanese forms above.")
        lines.append("- Never confuse Katakana loanwords with Hiragana grammatical particles (は, が, を, に, で, へ, と).")
        lines.append("- For each question, ensure the reading matches the official Furigana reading.")

        return "\n".join(lines)


# Singleton service instance
japanese_vocab_service = JapaneseVocabService()
