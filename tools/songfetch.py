#!/usr/bin/env python3
"""曲データ取得パイプライン(song-analysisスキル用)

使い方:
  python3 tools/songfetch.py probe                     # どのドメインに出られるか診断
  python3 tools/songfetch.py songle <YouTube URL>      # Songleでサビ区間検出+コード取得
  python3 tools/songfetch.py page <コード譜ページURL>   # 静的コード譜ページの取得+コード行抽出

前提: 実行環境のネットワークポリシーで対象ドメインが許可されていること。
      遮断環境では probe が全滅を報告する(その場合はスクショ運用にフォールバック)。
"""
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request

CA_BUNDLE = "/root/.ccr/ca-bundle.crt"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36")

PROBE_TARGETS = [
    "https://ja.chordwiki.org/",
    "https://www.ufret.jp/",
    "https://gakufu.gakki.me/",
    "https://music-chord.com/",
    "https://music.j-total.net/",
    "https://widget.songle.jp/",
    "https://api.songle.jp/",
]

# コードネームらしきトークン(C, Am7, F#m7-5, B♭M9, C/E, N.C. など)
CHORD_TOKEN = re.compile(
    r"^(N\.?C\.?|[A-G](#|b|♭|♯)?"
    r"(m|maj|Maj|M|dim|aug|sus|add)?[0-9]*"
    r"(\(?(#|b|♭|♯)?[0-9]+\)?)?"
    r"(-5|\+5)?"
    r"(/[A-G](#|b|♭|♯)?)?)$"
)


def _ctx():
    try:
        return ssl.create_default_context(cafile=CA_BUNDLE)
    except FileNotFoundError:
        return ssl.create_default_context()


def fetch(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ja"})
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
        return r.read()


def cmd_probe() -> None:
    ok = []
    for url in PROBE_TARGETS:
        host = urllib.parse.urlparse(url).netloc
        try:
            fetch(url, timeout=8)
            print(f"  OK      {host}")
            ok.append(host)
        except Exception as e:
            print(f"  BLOCKED {host} ({type(e).__name__})")
    print(f"\n{len(ok)}/{len(PROBE_TARGETS)} 到達可能")
    if not ok:
        print("→ 全滅: ネットワークポリシー未開放。スクショ運用にフォールバックする")


def _songle_api(path: str, song_url: str) -> dict:
    q = urllib.parse.quote(song_url, safe="")
    url = f"https://widget.songle.jp/api/v1/{path}?url={q}"
    return json.loads(fetch(url).decode("utf-8", "replace"))


def cmd_songle(song_url: str) -> None:
    """サビ区間(RefraiD)とコードのタイムラインを取得して、サビ内の進行を出す"""
    info = _songle_api("song.json", song_url)
    print(f"# {info.get('title', '?')} / {info.get('artist', {}).get('name', '?')}")
    print(f"  duration: {info.get('duration')}s  permalink: {info.get('permalink')}")

    chords = _songle_api("song/chord.json", song_url).get("chords", [])
    print(f"  コードイベント: {len(chords)}件")

    chorus = None
    for path in ("song/chorus.json", "song/repeat.json"):
        try:
            chorus = _songle_api(path, song_url)
            break
        except Exception:
            continue
    segments = []
    if chorus:
        for key in ("chorusSegments", "repeatSegments", "segments"):
            if key in chorus:
                segments = chorus[key]
                break
    if not segments:
        print("  サビ区間データなし(この曲はSongle未解析の可能性)→ 全コードを出力")
        for c in chords:
            print(f"    {c.get('start', 0) / 1000:7.1f}s  {c.get('name')}")
        return

    print(f"  サビ/リピート区間: {len(segments)}グループ")
    for seg in segments:
        is_chorus = seg.get("isChorus") or seg.get("chorus")
        label = "サビ" if is_chorus else "リピート"
        for rep in seg.get("repeats", [seg]):
            start = rep.get("start", 0)
            dur = rep.get("duration", 0)
            end = start + dur
            names = [c.get("name") for c in chords
                     if start <= c.get("start", 0) < end]
            if names:
                print(f"  [{label}] {start/1000:6.1f}s-{end/1000:6.1f}s: {' → '.join(names)}")


def cmd_page(url: str) -> None:
    """静的コード譜ページからコード行と歌詞行を抽出して交互に表示"""
    html = fetch(url).decode("utf-8", "replace")
    # scriptとstyleを除去してタグをスペース化
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    # コード用spanの中身を目印付きで残す(ChordWiki系: class="chord")
    html = re.sub(r'<span[^>]*class="[^"]*chord[^"]*"[^>]*>(.*?)</span>',
                  r" ⟨\1⟩ ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "\n", html)
    text = re.sub(r"&nbsp;?", " ", text)
    lines = [ln.strip() for ln in text.splitlines()]
    out = []
    for ln in lines:
        if not ln:
            continue
        toks = ln.replace("⟨", " ⟨").replace("⟩", "⟩ ").split()
        marked = [t[1:-1] for t in toks if t.startswith("⟨") and t.endswith("⟩")]
        plain_chordish = [t for t in toks if CHORD_TOKEN.match(t)]
        if marked or (plain_chordish and len(plain_chordish) >= max(2, len(toks) // 2)):
            out.append(("CHORD", " ".join(marked or plain_chordish)))
        elif re.search(r"[ぁ-んァ-ヶ一-龠]", ln) and len(ln) <= 80:
            out.append(("LYRIC", ln))
    # 連続同種をまとめず、そのまま出す(コード行と歌詞行の対応を人間/AIが読む)
    for kind, ln in out:
        print(f"{kind}: {ln}")


def cmd_mc(url: str) -> None:
    """music-chord.com専用: セクション名+歌詞(タイムスタンプ付き)+コードを文書順に出す"""
    html = fetch(url).decode("utf-8", "replace")
    # 文書順にトークン化: セクション名 / タイムスタンプ / 歌詞 / コード(Base+Quality)
    pat = re.compile(
        r'Content__SectionName[^>]*>(?P<sec>[^<]*)<'
        r'|YoutubeSeekButton__Button[^>]*>(?P<ts>[^<]*)</span>\s*(?:<!--[^>]*-->)?\s*(?P<lyric>[^<]*)'
        r'|Chord__Container[^>]*>(?P<chord>.*?)</div>',
        re.S,
    )
    def chord_name(inner: str) -> str:
        base = re.search(r'Base__Container[^>]*>([^<]*)<', inner)
        qual = re.search(r'Quality__Container[^>]*>([^<]*)<', inner)
        return (base.group(1) if base else "") + (qual.group(1) if qual else "")

    row_lyric, row_chords, row_ts = None, [], ""

    def flush():
        nonlocal row_lyric, row_chords, row_ts
        if row_lyric is not None or row_chords:
            lyric = (row_lyric or "").strip() or "(インスト)"
            chords = " → ".join(c for c in row_chords if c) or "(N.C.)"
            print(f"  [{row_ts}] ♪ {lyric}")
            print(f"       {chords}")
        row_lyric, row_chords, row_ts = None, [], ""

    for m in pat.finditer(html):
        if m.group("sec") is not None:
            flush()
            print(f"\n== {m.group('sec').strip()} ==")
        elif m.group("ts") is not None:
            flush()
            row_ts = m.group("ts").strip()
            row_lyric = m.group("lyric")
        elif m.group("chord") is not None:
            name = chord_name(m.group("chord"))
            if name:
                row_chords.append(name)
    flush()


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "probe":
        cmd_probe()
    elif cmd == "songle" and len(sys.argv) > 2:
        cmd_songle(sys.argv[2])
    elif cmd == "page" and len(sys.argv) > 2:
        cmd_page(sys.argv[2])
    elif cmd == "mc" and len(sys.argv) > 2:
        cmd_mc(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
