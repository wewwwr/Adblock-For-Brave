import urllib.request
import datetime

# --- ОСНОВНЫЕ СПИСКИ (Пойдут целиком в Brave) ---
URLS = [
    # --- AdGuard & Regional (Рунет) ---
    "https://filters.adtidy.org/extension/chromium/filters/1.txt",
    "https://filters.adtidy.org/extension/chromium/filters/14.txt",
    "https://filters.adtidy.org/extension/chromium/filters/11.txt",
    "https://filters.adtidy.org/extension/chromium/filters/3.txt",
    "https://filters.adtidy.org/extension/chromium/filters/17.txt",
    "https://filters.adtidy.org/extension/chromium/filters/4.txt",
    "https://raw.githubusercontent.com/easylist/ruadlist/master/advblock.txt",
    "https://easylist-downloads.adblockplus.org/cntblock.txt",
    "https://easylist-downloads.adblockplus.org/bitblock.txt",
    "https://raw.githubusercontent.com/easylist/ruadlist/master/css-fixes-experimental.txt",
    "https://raw.githubusercontent.com/easylist/ruadlist/master/js-fixes-experimental.txt",

    # --- uBlock Origin ---
    "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/filters.txt",
    "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/privacy.txt",
    "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/lan-block.txt",
    "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/badware.txt",
    "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/quick-fixes.txt",
    "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/unbreak.txt",
    "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/annoyances.txt",

    # --- DNS & Глобальная фильтрация ---
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/ultimate.txt",
    "https://raw.githubusercontent.com/badmojr/1Hosts/master/Lite/adblock.txt",
    "https://big.oisd.nl/",
    "https://pgl.yoyo.org/adservers/serverlist.php?hostformat=adblockplus&showintro=1&mimetype=plaintext",
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",

    # --- Узкоспециализированные (Майнеры, Куки, Spotify, Вирусы) ---
    "https://raw.githubusercontent.com/hoshsadiq/adblock-nocoin-list/master/nocoin.txt",
    "https://secure.fanboy.co.nz/fanboy-cookiemonster.txt",
    "https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Dandelion%20Sprout's%20Anti-Malware%20List.txt",
    "https://raw.githubusercontent.com/Isaaker/Spotify-AdsList/main/Lists/adguard.txt"
]

# --- СПИСКИ ДЛЯ ИСКЛЮЧЕНИЯ ДУБЛИКАТОВ ИЗ SAFARI ---
# Эти списки скачиваются только для того, чтобы вычесть их правила из файла для Safari, 
# так как они уже работают внутри приложения AdGuard Pro.
ADGUARD_BUILTIN_URLS = [
    "https://filters.adtidy.org/extension/chromium/filters/1.txt",  # Base
    "https://filters.adtidy.org/extension/chromium/filters/2.txt",  # Russian
    "https://filters.adtidy.org/extension/chromium/filters/3.txt",  # Tracking Protection
    "https://filters.adtidy.org/extension/chromium/filters/4.txt",  # Social Media
    "https://filters.adtidy.org/extension/chromium/filters/11.txt", # Mobile Ads
    "https://filters.adtidy.org/extension/chromium/filters/13.txt", # Widgets
    "https://filters.adtidy.org/extension/chromium/filters/14.txt", # Annoyances
    "https://filters.adtidy.org/extension/chromium/filters/15.txt", # Mobile App Banners
    "https://filters.adtidy.org/extension/chromium/filters/16.txt", # Popups
    "https://filters.adtidy.org/extension/chromium/filters/17.txt", # Cookie Notices
    "https://filters.adtidy.org/extension/chromium/filters/18.txt", # Other Annoyances
    "https://easylist.to/easylist/easylist.txt",                    # EasyList
    "https://easylist.to/easylist/easyprivacy.txt",                 # EasyPrivacy
    "https://easylist-downloads.adblockplus.org/cntblock.txt",      # RU Adlist Counters
    "https://secure.fanboy.co.nz/fanboy-cookiemonster.txt",         # EasyList Cookie/Fanboy
    "https://raw.githubusercontent.com/easylist/ruadlist/master/advblock.txt" # RU Adlist
]

def fetch_rules(url_list, follow_includes=False):
    rules = set()
    urls_to_process = url_list.copy()
    processed_urls = set()
    
    while urls_to_process:
        url = urls_to_process.pop(0)
        if url in processed_urls:
            continue
            
        processed_urls.add(url)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8', errors='ignore')
                
                for line in content.splitlines():
                    line = line.strip()
                    
                    if follow_includes and line.startswith('!#include'):
                        parts = line.split()
                        if len(parts) >= 2:
                            include_filename = parts[1].strip()
                            base_url = url.rsplit('/', 1)[0]
                            include_url = f"{base_url}/{include_filename}"
                            urls_to_process.append(include_url)
                        continue

                    if not line or line.startswith('!') or line.startswith('#'):
                        continue
                        
                    if line.startswith('0.0.0.0 ') or line.startswith('127.0.0.1 '):
                        parts = line.split()
                        if len(parts) >= 2:
                            line = f"||{parts[1]}^"
                            
                    rules.add(line)
            print(f"Загружен: {url}")
        except Exception as e:
            print(f"Ошибка при загрузке {url}: {e}")
            
    return rules

def generate_custom_filter():
    print("--- 1. СБОРКА ОСНОВНЫХ ПРАВИЛ ДЛЯ BRAVE ---")
    brave_rules = fetch_rules(URLS, follow_includes=True)
    
    print("\n--- 2. СКАЧИВАНИЕ БАЗ ADGUARD ДЛЯ ИСКЛЮЧЕНИЯ ДУБЛИКАТОВ ---")
    adguard_existing_rules = fetch_rules(ADGUARD_BUILTIN_URLS, follow_includes=False)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ЗАПИСЬ 1: Полный фильтр для Brave
    with open('brave_ultimate_filter.txt', 'w', encoding='utf-8') as f:
        f.write("! Title: My Ultimate Brave Filter\n")
        f.write(f"! Updated: {timestamp} (Автоматическая сборка)\n\n")
        for rule in sorted(brave_rules):
            f.write(rule + '\n')
            
    # ФИЛЬТРАЦИЯ 2: Отделяем косметику для Safari и вычитаем дубликаты
    safari_cosmetic_rules = set()
    for rule in brave_rules:
        # Признаки косметического правила (сокрытие элементов, вставка стилей)
        if '##' in rule or '#?#' in rule or '#@#' in rule:
            # Магия дедупликации: добавляем только если этого правила НЕТ в AdGuard
            if rule not in adguard_existing_rules:
                safari_cosmetic_rules.add(rule)

    # ЗАПИСЬ 2: Очищенная косметика для Safari
    with open('safari_cosmetic_filter.txt', 'w', encoding='utf-8') as f:
        f.write("! Title: Safari Cosmetic (No AdGuard Duplicates)\n")
        f.write(f"! Updated: {timestamp}\n")
        f.write(f"! Косметических правил: {len(safari_cosmetic_rules)}\n\n")
        for rule in sorted(safari_cosmetic_rules):
            f.write(rule + '\n')

    print(f"\n==============================================")
    print(f"ГОТОВО!")
    print(f"Всего уникальных правил для Brave: {len(brave_rules)}")
    print(f"Косметических правил для Safari (строго без дубликатов): {len(safari_cosmetic_rules)}")
    print(f"==============================================")

if __name__ == "__main__":
    generate_custom_filter()
