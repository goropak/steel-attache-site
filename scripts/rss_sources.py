"""RSS/API 소스 설정 — weekly-briefing.py에서 import해서 사용"""

# 백본 계층 (feedparser 직결)
BACKBONE_FEEDS = [
    {
        "name": "worldsteel",
        "url": "https://worldsteel.org/feed/",
        "lang": "en",
        "filter_tags": ["Press releases", "Data"],
    },
    {
        "name": "연합뉴스_산업",
        "url": "https://www.yna.co.kr/rss/industry.xml",
        "lang": "ko",
        "filter_tags": [],
    },
    {
        "name": "연합뉴스_경제",
        "url": "https://www.yna.co.kr/rss/economy.xml",
        "lang": "ko",
        "filter_tags": [],
    },
    {
        "name": "한국경제",
        "url": "https://www.hankyung.com/feed/finance",
        "lang": "ko",
        "filter_tags": [],
    },
    {
        "name": "Nikkei_Asia",
        "url": "https://asia.nikkei.com/rss/feed/nar",
        "lang": "en",
        "filter_tags": [],
    },
]

# 우회 계층 — Google News RSS (결과 0건 시 경고 필수)
GNEWS_QUERIES = [
    {"name": "GNews_KO", "url": "https://news.google.com/rss/search?q=철강+OR+포스코&hl=ko&gl=KR&ceid=KR:ko"},
    {"name": "GNews_EN", "url": "https://news.google.com/rss/search?q=steel+OR+HRC&hl=en-US&gl=US&ceid=US:en"},
    {"name": "GNews_ZH", "url": "https://news.google.com/rss/search?q=钢铁+OR+宝武&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"},
]

# 데이터 계층 — FRED API (월 1회, 별도 처리)
FRED_SERIES = {
    "HRC_US": "WPS101704",    # 열연
    "CRC_US": "WPU101707",    # 냉연
}
