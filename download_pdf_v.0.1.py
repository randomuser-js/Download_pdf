import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.securitum.com/public-reports.html"
DOWNLOAD_DIR = "reports"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_html(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def find_all_report_links():
    soup = get_html(BASE_URL)
    all_links = soup.find_all("a", href=True)
    pdf_links = []

    for a in all_links:
        href = a['href']
        full_url = urljoin(BASE_URL, href)

        if href.lower().endswith(".pdf"):
            # Bezpośredni PDF
            pdf_links.append((a.text.strip() or os.path.basename(href), full_url))
        elif "public-reports" in href and not href.startswith("mailto:"):
            # Podstrona raportu – może zawierać PDF
            try:
                sub_soup = get_html(full_url)
                for sub_a in sub_soup.find_all("a", href=True):
                    sub_href = sub_a['href']
                    if sub_href.lower().endswith(".pdf"):
                        pdf_url = urljoin(full_url, sub_href)
                        pdf_links.append((sub_a.text.strip() or os.path.basename(sub_href), pdf_url))
            except Exception as e:
                print(f"❗ Błąd przy przetwarzaniu {full_url}: {e}")

    return list(set(pdf_links))  # usuwamy duplikaty

def download_reports(links):
    for title, url in links:
        from urllib.parse import urlparse
        safe_name = os.path.basename(urlparse(url).path)
        fn = os.path.join(DOWNLOAD_DIR, safe_name + ".pdf")
        print(f"⬇️  Pobieram: {url}")
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            with open(fn, "wb") as f:
                f.write(r.content)
            print(f" ✅ Zapisano: {fn}")
        except Exception as e:
            print(f"❌ Błąd pobierania {url}: {e}")

def main():
    print("🔍 Szukam raportów...")
    links = find_all_report_links()
    print(f"📦 Znaleziono {len(links)} plików PDF.")
    download_reports(links)

if __name__ == "__main__":
    main()
