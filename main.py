import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import feedparser
import google.generativeai as genai

# 1. Gemini API 설정
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-3.6-flash')

# 2. RSS 뉴스 수집 (다양한 관점의 글로벌 출처 균형 수집)
rss_urls = [
    # 객관성 및 글로벌 표준 매체
    "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
    "https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
    "https://www.ft.com/?format=rss",
    "https://www.economist.com/finance-and-economics/rss.xml",
    "https://www.economist.com/the-world-this-week/rss.xml",
    
    # 시장 친화 및 보수적 관점 매체
    "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "https://feeds.content.dowjones.io/public/rss/wsj_world_news",
    "https://www.nationalreview.com/feed/",
    "https://www.washingtontimes.com/rss/headlines/news/business/",
    
    # 사회·정책 분석 및 심층 관점 매체
    "http://feeds.bbci.co.uk/news/business/rss.xml",
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.theguardian.com/business/rss",
    "https://www.theguardian.com/world/rss"
]

raw_news = []
for url in rss_urls:
    feed = feedparser.parse(url)
    for entry in feed.entries[:5]: # 출처당 상위 5개 수집
        raw_news.append(f"출처: {feed.feed.get('title', 'Global News')}\n제목: {entry.title}\n요약: {entry.get('summary', '')}\n링크: {entry.link}\n---")

news_data = "\n".join(raw_news)

# 3. AI 요약 요청
prompt = f"""
너는 최고 수준의 경제/일간지 에디터야. 아래 뉴스 데이터를 바탕으로 아침 뉴스레터를 작성해줘.

[규칙]
1. 중복된 사건은 하나로 통합할 것.
2. [경제/금융], [국제정치], [산업/기술], [글로벌 무역] 카테고리로 분류할 것.
3. 각 뉴스마다 핵심 요약 2~3줄 + 시사점 1줄을 작성할 것.
4. 뉴스 끝에는 반드시 원문 제목과 해당 원문 링크를 포함할 것.
5. 보기 좋은 HTML 포맷(CSS 스타일 포함)으로 응답만 출력할 것.

[뉴스 데이터]
{news_data}
"""

response = model.generate_content(prompt)
email_content = response.text

# 4. 이메일 발송
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_email = os.environ["EMAIL_USER"]
sender_password = os.environ["EMAIL_PASS"]
receiver_email = os.environ["TO_EMAIL"]

msg = MIMEMultipart("alternative")
msg["Subject"] = "☕ [AI Daily News] 오늘의 글로벌 아침 뉴스 브리핑"
msg["From"] = sender_email
msg["To"] = receiver_email
msg.attach(MIMEText(email_content, "html"))

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
