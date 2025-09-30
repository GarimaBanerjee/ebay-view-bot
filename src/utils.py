from __future__ import annotations
import os, time, re, urllib.parse, urllib.robotparser as robotparser
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional
import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_UA = os.getenv("USER_AGENT", "Mozilla/5.0 (compatible; ebay-view-bot/1.0)")
REQ_DELAY = float(os.getenv("REQUEST_DELAY_SECONDS", "8"))
REQ_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))

def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

@dataclass
class Fetcher:
    session: requests.Session
    ua: str = DEFAULT_UA
    delay: float = REQ_DELAY
    timeout: int = REQ_TIMEOUT
    _last_ts: float = 0.0
    _robots_cache: dict[str, robotparser.RobotFileParser] = None

    def __post_init__(self):
        self.session.headers.update({"User-Agent": self.ua})
        if self._robots_cache is None:
            self._robots_cache = {}

    def robots(self, url: str) -> robotparser.RobotFileParser:
        origin = urllib.parse.urlsplit(url)
        root = f"{origin.scheme}://{origin.netloc}"
        robots_url = f"{root}/robots.txt"
        if robots_url not in self._robots_cache:
            rp = robotparser.RobotFileParser()
            try:
                r = self.session.get(robots_url, timeout=self.timeout)
                rp.parse(r.text.splitlines())
            except Exception:
                # If robots can't be fetched, default to disallow nothing but keep delays.
                rp.set_url(robots_url); rp.read = lambda: None  # no-op
                rp.can_fetch = lambda *_: True
            self._robots_cache[robots_url] = rp
        return self._robots_cache[robots_url]

    def allowed(self, url: str) -> bool:
        return self.robots(url).can_fetch(self.ua, url)

    def wait(self):
        since = time.time() - self._last_ts
        if since < self.delay:
            time.sleep(self.delay - since)
        self._last_ts = time.time()

    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        if not self.allowed(url):
            raise PermissionError(f"robots.txt disallows: {url}")
        self.wait()
        try:
            return self.session.get(url, timeout=self.timeout, **kwargs)
        except requests.RequestException:
            return None

def make_fetcher() -> Fetcher:
    return Fetcher(session=requests.Session())
