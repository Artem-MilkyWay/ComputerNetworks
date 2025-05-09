import socket
import subprocess
import csv
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def resolve_dns(domain):
    """Выполняет DNS-запрос и возвращает IP-адрес"""
    try:
        return socket.gethostbyname(domain)
    except (socket.gaierror, socket.herror):
        return None

def perform_traceroute(ip):
    """Выполняет traceroute и возвращает результат"""
    try:
        # Для Linux/Mac
        traceroute_cmd = ['traceroute', '-n', '-q', '1', '-w', '1', ip]
        # Для Windows раскомментируйте следующую строку:
        # traceroute_cmd = ['tracert', '-d', '-w', '1000', ip]
        
        result = subprocess.run(traceroute_cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Traceroute timed out"
    except Exception as e:
        return f"Traceroute error: {str(e)}"

def process_domain(domain):
    """Обрабатывает один домен: DNS + traceroute"""
    ip = resolve_dns(domain)
    if not ip:
        return domain, None, None
    
    traceroute_result = perform_traceroute(ip)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    trace_filename = f"traceroute_{domain.replace('.', '_')}_{timestamp}.txt"
    
    with open(trace_filename, 'w') as f:
        f.write(f"=== Traceroute for {domain} ({ip}) ===\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write("===================================\n")
        f.write(traceroute_result)
    
    return domain, ip, trace_filename

def main():
    # Список доменов для проверки
    domains = [
        "google.com",
        "youtube.com",
        "github.com",
        "stackoverflow.com",
        "amazon.com",
        "microsoft.com",
        "twitter.com",
        "linkedin.com"
    ]
    
    # Имя выходного файла с временной меткой
    csv_filename = f"network_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Заголовки CSV
    headers = ['Domain', 'IP Address', 'Traceroute File', 'Timestamp']
    
    # Обработка доменов с многопоточностью
    with ThreadPoolExecutor(max_workers=5) as executor, \
         open(csv_filename, 'w', newline='') as csvfile:
        
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        futures = {executor.submit(process_domain, domain): domain for domain in domains}
        
        for future in as_completed(futures):
            domain = futures[future]
            try:
                domain, ip, trace_file = future.result()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if ip:
                    print(f"[✓] {domain} → {ip}")
                    writer.writerow([domain, ip, trace_file, timestamp])
                else:
                    print(f"[×] {domain} → Failed to resolve")
                    writer.writerow([domain, "N/A", "N/A", timestamp])
                    
            except Exception as e:
                print(f"[!] Error processing {domain}: {str(e)}")
                writer.writerow([domain, "Error", str(e), timestamp])
    
    print(f"\nReport saved to: {csv_filename}")

if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"\nExecution time: {time.time() - start_time:.2f} seconds")
