import os
import time
import random
import requests
import subprocess
import warnings
import sys
from datetime import datetime, timedelta, timezone

warnings.filterwarnings("ignore")

API_BASE = "https://gateway.golike.net/api"

VIDEO_FILE = "tiktok_links.txt"
WATCHED_FILE = "watched_videos.txt"

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

# ===== TOTAL ALL ACC RESET 0H =====
def get_total_all_acc(stats):
    now = datetime.now(timezone.utc) + timedelta(hours=7)
    today = now.strftime("%d/%m/%Y")

    total = 0
    for v in stats.values():
        ts = v.get("ts", int(time.time()))
        t = datetime.fromtimestamp(ts, timezone.utc) + timedelta(hours=7)

        if t.strftime("%d/%m/%Y") == today:
            total += v.get("xu", 0)

    return total

def resolve_tiktok_url(url):
    try:
        r = session.get(url, allow_redirects=True, timeout=10)
        return r.url
    except:
        return url

def load_video_links():
    if not os.path.exists(VIDEO_FILE):
        return []
    with open(VIDEO_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def load_watched():
    if not os.path.exists(WATCHED_FILE):
        return set()
    return set(open(WATCHED_FILE).read().splitlines())

def save_watched(watched):
    with open(WATCHED_FILE, "w") as f:
        for i in watched:
            f.write(i + "\n")

def save_video_link():
    while True:
        link = input("Nhập link video (Enter để dừng): ").strip()
        if not link:
            break
        if not link.startswith("http"):
            print("❌ Link không hợp lệ!")
            continue
        print("🔄 Đang xử lý...")
        real = resolve_tiktok_url(link)
        print("➡️", real)

        links = load_video_links()
        if real in links:
            print("⚠️ Đã tồn tại\n")
            continue

        with open(VIDEO_FILE, "a") as f:
            f.write(real + "\n")
        print("✔ Đã lưu\n")

def watch_videos(name, stats, acc_id):
    watched = load_watched()
    links = list(dict.fromkeys(load_video_links()))
    if not links:
        return

    available = [l for l in links if l not in watched]
    if not available:
        watched.clear()
        available = links

    num = random.randint(3, 5)
    if len(available) < num:
        num = len(available)

    selected = random.sample(available, num)

    for link in selected:
        watched.add(link)
        save_watched(watched)

        try:
            subprocess.run(["am","start","-a","android.intent.action.VIEW","-d",link],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

        delay = random.randint(15, 25)

        for i in range(1, delay + 1):
            draw_box(name,"WATCH VIDEO","",0,0,0,
                     i,delay,
                     stats.get(acc_id, {}).get("xu", 0),
                     get_total_all_acc(stats),
                     f"🎬 Đang xem video {i}/{delay}s...")
            time.sleep(1)

def farm_tiktok(name, minutes):
    links = load_video_links()
    if not links:
        print("❌ Không có video!")
        time.sleep(2)
        return

    end_time = time.time() + minutes * 60
    index = 0

    while time.time() < end_time:
        link = links[index % len(links)]
        index += 1

        try:
            subprocess.run([
                "am","start",
                "-a","android.intent.action.VIEW",
                "-d",link
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

        delay = random.randint(15, 30)

        for i in range(1, delay + 1):
            remaining = int(end_time - time.time())
            if remaining <= 0:
                break

            draw_box(
                name,
                "FARM TIKTOK",
                "",
                0,0,0,
                i,delay,
                0,
                0,
                f"🎬 Đang chăm acc | còn {remaining}s"
            )
            time.sleep(1)

    print("\n✅ Xong thời gian chăm acc!")
    time.sleep(2)

def keep_awake():
    try:
        subprocess.run(["termux-wake-lock"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

def prevent_sleep():
    try:
        subprocess.run(["svc","power","stayon","true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

class Color:
    RED="\033[1;91m";GREEN="\033[1;92m";YELLOW="\033[1;93m"
    BLUE="\033[1;94m";PURPLE="\033[1;95m";CYAN="\033[1;96m"
    WHITE="\033[1;97m";GRAY="\033[1;90m";RESET="\033[0m"
    ORANGE = "\033[38;5;208m"

RAINBOW=[Color.RED,Color.YELLOW,Color.GREEN,Color.CYAN,Color.BLUE,Color.PURPLE]

def get_vn_time():
    now=datetime.now(timezone.utc)+timedelta(hours=7)
    days=["Thứ 2","Thứ 3","Thứ 4","Thứ 5","Thứ 6","Thứ 7","Chủ Nhật"]
    return f"{days[now.weekday()]}, {now.strftime('%d/%m/%Y %H:%M:%S')}"

last_ping=0;last_ping_time=0
def get_ping():
    global last_ping,last_ping_time
    if time.time()-last_ping_time<5: return last_ping
    try:
        t=time.time()
        session.get("https://1.1.1.1",timeout=3)
        last_ping=int((time.time()-t)*1000)
    except: last_ping=999
    last_ping_time=time.time()
    return last_ping

IP_INFO=("Vietnam","0.0.0.0","Unknown",False)

def get_ip_country_once():
    global IP_INFO
    try:
        r=session.get("http://ip-api.com/json/",timeout=5).json()
        IP_INFO=(
            r.get("country","VN"),
            r.get("query","0.0.0.0"),
            r.get("isp","Unknown"),
            r.get("proxy",False)
        )
    except:
        pass

def get_ip_country():
    return IP_INFO

def get_network_type():
    try:
        net = subprocess.check_output(
            ["getprop", "gsm.network.type"],
            stderr=subprocess.DEVNULL
        ).decode().strip().upper()

        if "NR" in net or "5G" in net: return "📶 5G"
        if "LTE" in net: return "📶 4G"
        if "HSPA" in net or "UMTS" in net: return "📶 3G"
        if "EDGE" in net or "GPRS" in net: return "📶 2G"
    except:
        pass

    try:
        wifi = subprocess.check_output(
            ["getprop", "wifi.interface"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        if wifi: return "📡 WiFi"
    except:
        pass

    return "❓ Unknown"

def dot_bar(c,t,l=10):
    if t == 0: t = 1
    filled=int(l*c//t)
    shift=int(time.time()*5)
    bar=""
    for i in range(l):
        if i<filled:
            bar+=RAINBOW[(i+shift)%len(RAINBOW)]+"●"+Color.RESET
        else:
            bar+=Color.GRAY+"○"+Color.RESET
    return bar

def format_job_type(t):
    t=str(t).lower()
    if "follow" in t:return "FOLLOW"
    if "like" in t:return "LIKE"
    return t.upper()

def load_acc_stats():
    stats={}
    if os.path.exists("acc_stats.txt"):
        for line in open("acc_stats.txt"):
            try:
                aid,job,xu,ts=line.strip().split("|")
                job=int(job);xu=int(xu);ts=int(ts)
                if time.time()-ts>=86400:
                    stats[aid]={"job":0,"xu":0,"ts":int(time.time())}
                else:
                    stats[aid]={"job":job,"xu":xu,"ts":ts}
            except: pass
    return stats

def save_acc_stats(stats):
    with open("acc_stats.txt","w") as f:
        for k,v in stats.items():
            f.write(f"{k}|{v['job']}|{v['xu']}|{v['ts']}\n")

def draw_box(name, job_type, link, done, maxj, total, i, delay, daily, total_all, status="", price=0):
    print("\033[2J\033[H", end="")

    time_str=get_vn_time()
    ping=get_ping()
    country, ip_addr, isp, is_proxy = get_ip_country()
    net = get_network_type()
    bar=dot_bar(i,delay)

    vpn = "🔴 Đang dùng VPN" if is_proxy else "🟢 IP Thật"

    print(f"{Color.YELLOW}⏰ {time_str}{Color.RESET}")
    print(f"{Color.CYAN}🌍 {country} | 🌐 {ip_addr}{Color.RESET}")
    print(f"{Color.GREEN}{net} | 📡 {ping}ms | {vpn}{Color.RESET}")
    print(f"{Color.PURPLE}🏢 ISP: {isp}{Color.RESET}")

    print(f"{Color.WHITE}👤 {name}{Color.RESET}")
    
    if price > 0:
        print(f"{Color.YELLOW}🎯 LOẠI JOB: {job_type} | GIÁ: {price} xu{Color.RESET}")
    else:
        print(f"{Color.YELLOW}🎯 JOB: {job_type}{Color.RESET}")

    if job_type != "WATCH VIDEO":
        print(f"{Color.BLUE}🔗 {link}{Color.RESET}")

    print(f"{Color.CYAN}⏳ {i}/{delay}s {bar}{Color.RESET}")
    print(f"{Color.GREEN}🔄 {status}{Color.RESET}")

    print(f"{Color.YELLOW}📦 {done}/{maxj}   💰 {total} xu{Color.RESET}")
    print(f"{Color.CYAN}💎 Tổng Xu Đã Làm Trong Ngày: {daily} xu{Color.RESET}")
    print(f"{Color.GREEN}💰 Tổng Xu Tất Cả Acc: {total_all} xu{Color.RESET}")

    sys.stdout.flush()

def xu_fly(xu):
    for i in range(3):
        print(f"💰 +{xu}")
        time.sleep(0.1)

def rq(m,u,**k):
    for _ in range(3):
        try:
            r=session.request(m,u,timeout=10,**k)
            if r.status_code==200:
                return r.json()
        except: pass
        time.sleep(2)
    return None

def get_acc(h): return rq("GET",f"{API_BASE}/tiktok-account",headers=h)
def get_job(h,id): return rq("GET",f"{API_BASE}/advertising/publishers/tiktok/jobs",headers=h,params={"account_id":id})
def complete(h,jid,id): return rq("POST",f"{API_BASE}/advertising/publishers/tiktok/complete-jobs",headers=h,json={"ads_id":jid,"account_id":id})

def skip(h,d,acc_id):
    try:
        payload={"ads_id":d.get("id"),"account_id":acc_id,"type":d.get("type")}
        if d.get("object_id"):
            payload["object_id"]=d["object_id"]
        session.post(f"{API_BASE}/advertising/publishers/tiktok/skip-jobs",
                      headers=h,json=payload,timeout=10)
    except: pass

def load():
    open("Authorization.txt","a").close()
    open("token.txt","a").close()
    a=open("Authorization.txt").read().strip()
    t=open("token.txt").read().strip()
    if a and t and input(f"{Color.CYAN}Dùng Token Cũ? Enter=OK: {Color.RESET}")=="":
        return a,t
    a=input("Authorization: ")
    t=input("Token: ")
    open("Authorization.txt","w").write(a)
    open("token.txt","w").write(t)
    return a,t

def main():
    keep_awake()
    prevent_sleep()
    stats=load_acc_stats()

    auth,token=load()
    h={"Authorization":auth,"t":token}
    get_ip_country_once()

    while True:
        print(f"{Color.CYAN}\n1. Chạy Tool{Color.RESET}")
        print(f"{Color.CYAN}2. Nhập link video TikTok{Color.RESET}")
        print(f"{Color.CYAN}3. Chăm Acc TikTok{Color.RESET}")
        menu=input(f"{Color.YELLOW}Chọn: {Color.RESET}")

        if menu=="2":
            save_video_link()
            continue

        if menu=="3":
            name = "TIKTOK FARM"
            try:
                minutes = int(input("⏱ Nhập số phút muốn chăm acc: "))
            except:
                continue
            input("👉 Nhấn Enter để bắt đầu...")
            farm_tiktok(name, minutes)
            continue

        accs=get_acc(h)
        if not accs or "data" not in accs:
            print("Token Lỗi");return

        print(f"{Color.CYAN}\n=== DANH SÁCH TÀI KHOẢN ==={Color.RESET}")
        for i,a in enumerate(accs["data"],1):
            aid=str(a["id"])
            print(
                f"{Color.YELLOW}{i}.{Color.RESET} "
                f"{Color.GREEN}{a.get('nickname')}{Color.RESET} "
                f"{Color.ORANGE}({a.get('unique_username')}){Color.RESET}"
            )

        choice = input("Chọn Acc (STT hoặc Username): ").strip()
        acc = None

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(accs["data"]):
                acc = accs["data"][idx]
        else:
            for a in accs["data"]:
                if a.get("unique_username") == choice:
                    acc = a
                    break

        if not acc:
            print("❌ Không tìm thấy tài khoản!")
            continue

        id=str(acc["id"])
        name=f"{acc.get('nickname')} ({acc.get('unique_username')})"

        print("\n1. Follow\n2. Like\n3. Cả 2")
        choice=input("Chọn loại job: ")
        job_filter=["follow","like"] if choice=="3" else ["follow"] if choice=="1" else ["like"]

        # ===== MENU LỌC XU THEO YÊU CẦU =====
        print(f"\n{Color.CYAN}=== CÀI ĐẶT LỌC XU ==={Color.RESET}")
        print("1. Làm job >= 40 xu")
        print("2. Làm job dưới 40 xu")
        print("3. Làm job tất cả xu")
        xu_choice = input("Chọn cấu hình lọc xu: ").strip()
        if xu_choice not in ["1", "2", "3"]:
            xu_choice = "3"
        # ====================================

        dmin=int(input("Delay Min: "))
        dmax=int(input("Delay Max: "))
        maxj=int(input("Số Job: "))
        retry=int(input("Retry: "))
        max_fail=int(input("Số Lỗi Liên Tiếp: "))
        rest_after=int(input("Bao nhiêu job thì nghỉ xem video: "))

        input("\n👉 Nhấn Enter Để Chạy...")

        total=done=fail=0

        while done<maxj:
            job=get_job(h,id)
            if not job or not job.get("data"):
                print("❌ Không có job nào để làm. Đang chờ 10 giây...")
                time.sleep(10)
                continue

            d=job["data"]
            if not isinstance(d,dict):
                continue

            raw=d.get("type","").lower()
            xu_job = d.get("price_after_cost", 0)

            # Sàng lọc các job không đúng thể loại
            if any(x in raw for x in ["comment","share","view","join"]):
                draw_box(name,"SKIP","",done,maxj,total,0,1,
                         stats.get(id,{}).get("xu",0),
                         get_total_all_acc(stats),
                         f"🚫 Bỏ qua job {raw.upper()}")
                time.sleep(1)
                skip(h,d,id)
                continue

            if not any(x in raw for x in job_filter):
                draw_box(name,"SKIP","",done,maxj,total,0,1,
                         stats.get(id,{}).get("xu",0),
                         get_total_all_acc(stats),
                         f"🚫 Bỏ qua job {format_job_type(raw)}")
                time.sleep(1)
                skip(h,d,id)
                continue

            # ===== LOGIC KIỂM TRA ĐIỀU KIỆN LỌC XU =====
            if xu_choice == "1" and xu_job < 40:
                draw_box(name, "SKIP XU", "", done, maxj, total, 0, 1,
                         stats.get(id, {}).get("xu", 0),
                         get_total_all_acc(stats),
                         f"🚫 Bỏ qua job thấp xu ({xu_job} xu < 40 xu)", xu_job)
                time.sleep(1)
                skip(h, d, id)
                continue

            elif xu_choice == "2" and xu_job >= 40:
                draw_box(name, "SKIP XU", "", done, maxj, total, 0, 1,
                         stats.get(id, {}).get("xu", 0),
                         get_total_all_acc(stats),
                         f"🚫 Bỏ qua job cao xu ({xu_job} xu >= 40 xu)", xu_job)
                time.sleep(1)
                skip(h, d, id)
                continue
            # ============================================

            link=d.get("link")
            if not link:
                skip(h,d,id)
                continue

            job_type=format_job_type(d["type"])

            try:
                subprocess.run(["am","start","-a","android.intent.action.VIEW","-d",link],
                               stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            except: pass

            delay=random.randint(dmin,dmax)

            for i in range(1,delay+1):
                draw_box(name,job_type,link,done,maxj,total,i,delay,
                         stats.get(id,{}).get("xu",0),
                         get_total_all_acc(stats),
                         "Đang Làm Job.", xu_job)
                time.sleep(1)

            ok=False;xu=0

            for attempt in range(1, retry + 1):
                draw_box(name,job_type,link,done,maxj,total,delay,delay,
                         stats.get(id,{}).get("xu",0),
                         get_total_all_acc(stats),
                         f"Đang hoàn thành lần {attempt}/{retry}...", xu_job)
                r=complete(h,d["id"],id)

                if r and r.get("status")==200:
                    # ĐỒNG BỘ NGUỒN XU 1: Ưu tiên dùng thẳng xu_job nhận từ lúc lấy Job
                    xu = xu_job if xu_job > 0 else r.get("data", {}).get("prices", 0)
                    
                    if xu>0:
                        ok=True
                        xu_fly(xu)

                        draw_box(name,job_type,link,done,maxj,total,delay,delay,
                                 stats.get(id,{}).get("xu",0),
                                 get_total_all_acc(stats),
                                 f"🔥 Bú Job +{xu} Xu", xu_job)

                        time.sleep(1.5)

                        stats.setdefault(id,{"job":0,"xu":0,"ts":int(time.time())})
                        stats[id]["job"]+=1
                        stats[id]["xu"]+=xu
                        save_acc_stats(stats)
                        break

                time.sleep(2)

            if not ok:
                fail+=1

                draw_box(name,"ERROR",link,done,maxj,total,delay,delay,
                         stats.get(id,{}).get("xu",0),
                         get_total_all_acc(stats),
                         "❌ Hoàn thành thất bại → Bỏ qua job")
                time.sleep(2)

                skip(h,d,id)

                if fail>=max_fail:
                    draw_box(name,"WARNING","",done,maxj,total,0,1,
                             stats.get(id,{}).get("xu",0),
                             get_total_all_acc(stats),
                             "⚠️ Lỗi liên tiếp quá nhiều, reset...")
                    time.sleep(2)
                    fail=0

                continue

            total+=xu
            done+=1
            fail=0

            if rest_after > 0 and done % rest_after == 0:
                watch_videos(name, stats, id)

        print("\n🔁 Hoàn Thành, Quay Lại Menu...\n")

if __name__=="__main__":
    while True:
        try:
            main()
        except Exception as e:
            print("Lỗi, restart...", e)
            time.sleep(5)
