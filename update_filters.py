import urllib.request
import datetime

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

def generate_custom_filter():
    unique_rules = set()
    urls_to_process = URLS.copy()
    processed_urls = set()
    
    while urls_to_process:
        url = urls_to_process.pop(0)
        
        # Защита от зацикливания, если файлы ссылаются друг на друга
        if url in processed_urls:
            continue
            
        processed_urls.add(url)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8', errors='ignore')
                
                for line in content.splitlines():
                    line = line.strip()
                    
                    # Магия: Обработка скрытых ссылок uBlock Origin (!#include)
                    if line.startswith('!#include'):
                        parts = line.split()
                        if len(parts) >= 2:
                            include_filename = parts[1].strip()
                            # Формируем новую ссылку относительно текущей папки на GitHub
                            base_url = url.rsplit('/', 1)[0]
                            include_url = f"{base_url}/{include_filename}"
                            urls_to_process.append(include_url)
                        continue

                    # Пропускаем обычные пустые строки и текстовые комментарии
                    if not line or line.startswith('!') or line.startswith('#'):
                        continue
                        
                    # Конвертируем старый формат Hosts в формат AdBlock
                    if line.startswith('0.0.0.0 ') or line.startswith('127.0.0.1 '):
                        parts = line.split()
                        if len(parts) >= 2:
                            line = f"||{parts[1]}^"
                            
                    unique_rules.add(line)
            print(f"Успешно загружен: {url}")
        except Exception as e:
            print(f"Ошибка при загрузке {url}: {e}")

    # Запись итогового файла
    output_filename = 'brave_ultimate_filter.txt'
    with open(output_filename, 'w', encoding='utf-8') as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write("! Title: My Ultimate Brave Filter\n")
        f.write(f"! Updated: {timestamp} (Автоматическая сборка)\n")
        f.write(f"! Собрано из {len(processed_urls)} исходных файлов (включая скрытые под-списки uBlock).\n\n")
        
        for rule in sorted(unique_rules):
            f.write(rule + '\n')
            
    print(f"\nГотово! Обработано файлов: {len(processed_urls)}. Собрано уникальных правил: {len(unique_rules)}")

if __name__ == "__main__":
    generate_custom_filter()
