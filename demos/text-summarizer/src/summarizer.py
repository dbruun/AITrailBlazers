"""Summarization logic for the AI Text Summarizer demo.

Two modes are supported:

* ``offline`` – a dependency-free extractive summarizer (always available).
* ``azure-openai`` – uses an Azure OpenAI chat deployment when the
  ``AZURE_OPENAI_ENDPOINT``, ``AZURE_OPENAI_API_KEY`` and
  ``AZURE_OPENAI_DEPLOYMENT`` environment variables are set.
"""

import json
import os
import re
import urllib.request
from collections import Counter

STOP_WORDS = frozenset(
    """a an and are as at be but by for from has have he her his i in is it its of on or
    our she that the their them they this to was we were will with you your not can
    so if than then there these those which who what when where how all also into""".split()
)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
WORD = re.compile(r"[a-zA-Z']+")

DEFAULT_API_VERSION = "2024-06-01"
SYSTEM_PROMPT = (
    "You are a helpful assistant that writes concise, factual summaries. "
    "Summarize the user's text in at most {n} sentences."
)


def split_sentences(text):
    return [s.strip() for s in SENTENCE_SPLIT.split(text.strip()) if s.strip()]


def summarize_offline(text, max_sentences=3):
    """Return the highest-scoring sentences, kept in their original order."""
    sentences = split_sentences(text)
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    words = [w.lower() for w in WORD.findall(text) if w.lower() not in STOP_WORDS]
    freq = Counter(words)
    if not freq:
        return " ".join(sentences[:max_sentences])
    top = max(freq.values())

    def score(sentence):
        tokens = [w.lower() for w in WORD.findall(sentence)]
        if not tokens:
            return 0.0
        return sum(freq.get(t, 0) / top for t in tokens) / len(tokens)

    ranked = sorted(range(len(sentences)), key=lambda i: score(sentences[i]), reverse=True)
    keep = sorted(ranked[:max_sentences])
    return " ".join(sentences[i] for i in keep)


def azure_openai_configured(env=None):
    env = os.environ if env is None else env
    return all(
        env.get(k)
        for k in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT")
    )


def summarize_azure_openai(text, max_sentences=3, env=None, timeout=30):
    env = os.environ if env is None else env
    url = "%s/openai/deployments/%s/chat/completions?api-version=%s" % (
        env["AZURE_OPENAI_ENDPOINT"].rstrip("/"),
        env["AZURE_OPENAI_DEPLOYMENT"],
        env.get("AZURE_OPENAI_API_VERSION", DEFAULT_API_VERSION),
    )
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.format(n=max_sentences)},
            {"role": "user", "content": text},
        ],
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "api-key": env["AZURE_OPENAI_API_KEY"]},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body["choices"][0]["message"]["content"].strip()


def summarize(text, max_sentences=3, env=None):
    """Summarize ``text`` and return ``(summary, mode)``."""
    if azure_openai_configured(env):
        return summarize_azure_openai(text, max_sentences, env=env), "azure-openai"
    return summarize_offline(text, max_sentences), "offline"
