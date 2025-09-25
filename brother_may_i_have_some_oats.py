import requests
from bs4 import BeautifulSoup
import time
import random
import json
from datetime import datetime



LOGIN_URL = "https://portal.ctdb.hcmus.edu.vn/Login?returnurl=%2f"
DANG_KY_URL = "https://portal.ctdb.hcmus.edu.vn/dang-ky-hoc-phan/sinh-vien-clc"

def create_session():
    """Tạo session với headers chuẩn"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "Accept-Language": "vi,en-US;q=0.9,en;q=0.8,ko;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    })
    return session

def login(session, username, password):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] login voi user: {username}")
    
    r = session.get(LOGIN_URL, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # print all hidding inputs in login page
    form_data = {}
    for inp in soup.find_all("input"):
        name = inp.get("name")
        if not name:
            continue
        value = inp.get("value", "")
        form_data[name] = value
        print(f"Found input: {name} = {value}")

    #input tk mk vào đây
    form_data["dnn$ctr$Login$Login_DNN$txtUsername"] = username
    form_data["dnn$ctr$Login$Login_DNN$txtPassword"] = password

    #set event target to login button - đúng như trong cURL
    form_data["__EVENTTARGET"] = "dnn$ctr$Login$Login_DNN$cmdLogin"

    #Thêm một số cookies quan trọng từ cURL request
    #multipart/form-data như browser nen phai dung files=  
    #Chuyển form_data thành định dạng files để tạo multipart chính xác
    files_data = {}
    for key, value in form_data.items():
        files_data[key] = (None, value)  # (None, value) tạo field không có filename

    post_resp = session.post(
        LOGIN_URL,
        files=files_data,
        headers={
            "Referer": LOGIN_URL,
            "Origin": "https://portal.ctdb.hcmus.edu.vn",
        },
        allow_redirects=True,
        timeout=15
    )

    #check cookies / response to confirm login
    print("Status:", post_resp.status_code)
    print("Final URL:", post_resp.url)
    print("Cookies after login:")
    for k,v in session.cookies.items():
        print(f"  {k} = {v}")

    if any(name.lower().startswith(".aspxauth") or "auth" in name.lower() for name in session.cookies.keys()):
        print("login complete have cookie auth.")
        return True
    else:
        print("login fail.")
        return False

def check_dang_ky_page(session):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Kiểm tra trang đăng ký học phần...")
    
    #vào trang đăng ký học phần
    dangky_resp = session.get(DANG_KY_URL, timeout=15)
    dangky_resp.raise_for_status()

    print(f"\ntruy cap dang ky hoc phan")
    print(f"Status: {dangky_resp.status_code}")
    print(f"Final URL: {dangky_resp.url}")

    if "Sinh viên CLC" in dangky_resp.text:
        print("Đã vào trang đăng ký học phần thành công!")
        return True
    else:
        print("Chưa vào được trang đăng ký học phần")
        return False

def dang_ky_mon_hoc(session, ma_lop_hp):
    
    #sample from browser
    '''
    curl 'https://portal.ctdb.hcmus.edu.vn/dang-ky-hoc-phan/sinh-vien-clc' \
    -H 'Accept: */*' \
    -H 'Accept-Language: vi,en-US;q=0.9,en;q=0.8,ko;q=0.7' \
    -H 'Connection: keep-alive' \
    -H 'Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryEVnx7NBGr18s4LSf' \
    -b '_ga_97T4F75GB6=GS2.1.s1751629840$o2$g0$t1751629840$j60$l0$h0; .ASPXANONYMOUS=JNA0kjZT6QuLTEJ5PiaoBFX6MQet7FGBRyby3aEUlvpbW6G5_BDDIF8pFz5Kj8spvAU5ttcJ5Tzi75tLexU8r7-e-lXot2RUQMaDqu_3YWpcBXea0; _ga=GA1.3.560714492.1751622270; _ga_FV58V7FLLC=GS2.3.s1758437299$o2$g1$t1758437579$j60$l0$h0; dnn_IsMobile=False; language=en-US; __RequestVerificationToken=QKzR8rHTaOlbGZCcSzEtDTSF3VwqMdSDVzq0QyK7Qpo2VL1USs4ku8aIYqe5uy9gOBJRmA2; authentication=DNN; .DOTNETNUKE=D306FA0966DCAC163BCA6A2704417A30275A09D1785F8C130911F08432F29FD5B50A678BA0CF984DD8B71D74676B07EFA01836D67D2F8A12D336B52DADF3A4B93ECB5C5C7E9CFFF81F5885B2; LastPageId=0:149' \
    -H 'Origin: https://portal.ctdb.hcmus.edu.vn' \
    -H 'Referer: https://portal.ctdb.hcmus.edu.vn/dang-ky-hoc-phan/sinh-vien-clc' \
    -H 'Sec-Fetch-Dest: empty' \
    -H 'Sec-Fetch-Mode: cors' \
    -H 'Sec-Fetch-Site: same-origin' \
    -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36' \
    -H 'X-OFFICIAL-REQUEST: TRUE' \
    -H 'X-Requested-With: XMLHttpRequest' \
    -H 'sec-ch-ua: "Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"' \
    -H 'sec-ch-ua-mobile: ?0' \
    -H 'sec-ch-ua-platform: "Linux"' \
    --data-raw $'------WebKitFormBoundaryEVnx7NBGr18s4LSf\r\nContent-Disposition: form-data; name="action"\r\n\r\naddMonDangKy\r\n------WebKitFormBoundaryEVnx7NBGr18s4LSf\r\nContent-Disposition: form-data; name="data"\r\n\r\n5902\r\n------WebKitFormBoundaryEVnx7NBGr18s4LSf--\r\n'''

    print(f"dang ky mon hoc : {ma_lop_hp}")
    
    #form data đăng ký
    form_data = {
        "action": (None, "addMonDangKy"),
        "data": (None, str(ma_lop_hp))
    }
    
    ajax_headers = {
        "Accept": "*/*",
        "Referer": DANG_KY_URL,
        "Origin": "https://portal.ctdb.hcmus.edu.vn",
        "X-OFFICIAL-REQUEST": "TRUE",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    
    response = session.post(
        DANG_KY_URL,
        files=form_data,
        headers=ajax_headers,
        timeout=15
    )
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        try:
            # Parse JSON response
            json_response = json.loads(response.text)
            status = json_response.get("Status", "")
            message = json_response.get("Message", "")
            
            if status == "Success":
                print(f"Lụm được một môn {message}")
                return "Success"
            elif status == "FAILED":
                print(f"Đăng ký thất bại: {message}")
                return "FAILED"
            else:
                print(f"không xác định: {status} - {message}")
                return "UNKNOWN"
                
        except json.JSONDecodeError:
            print("Response không phải JSON, restart login")
            return "NEED_RELOGIN"
    else:
        print("HTTP request thất bại!")
        return "ERROR"

def auto_dang_ky_hoc_phan(username, password, danh_sach_mon_hoc):
    """
    Tự động đăng ký học phần
    Login lại mỗi 10 phút
    Random delay 1-10s
    Retry liên tục cho đến khi thành công
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] bắt đầu Tự động đăng ký học phần")
    print(f"Danh sách môn cần đăng ký: {danh_sach_mon_hoc}")
    
    session = None
    last_login_time = 0
    LOGIN_INTERVAL = 10 * 60  # 10 phút = 600 giây
    
    while True:
        current_time = time.time()
        
        #login lại mỗi 10 phút hoặc lần đầu tiên
        if session is None or (current_time - last_login_time) > LOGIN_INTERVAL:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Thuc hien dang nhap")
            session = create_session()
            
            if not login(session, username, password):
                print("Login thất bại, thử lại sau 30s...")
                time.sleep(30)
                continue
                
            if not check_dang_ky_page(session):
                print("Không thể truy cập trang đăng ký, thử lại sau 30s...")
                time.sleep(30)
                continue
                
            last_login_time = current_time
            print(f"Login thành công lúc {datetime.now().strftime('%H:%M:%S')}")
        
        # Thử đăng ký từng môn học
        danh_sach_can_dang_ky = danh_sach_mon_hoc.copy()  # Copy để có thể xóa môn đã thành công
        
        for ma_mon in danh_sach_can_dang_ky:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📚 Đăng ký môn: {ma_mon}")
            
            try:
                result = dang_ky_mon_hoc(session, ma_mon)
                
                if result == "Success":
                    print(f"🎊 Môn {ma_mon} đã đăng ký thành công! Loại bỏ khỏi danh sách.")
                    danh_sach_mon_hoc.remove(ma_mon)
                elif result == "NEED_RELOGIN":
                    print("🔄 Cần login lại, break khỏi vòng lặp này")
                    session = None  # Force login lại
                    break
                
                #random delay 1-10 giây
                delay = random.randint(1, 2)
                print(f"⏳ Chờ {delay}s trước request tiếp theo...")
                time.sleep(delay)
                
            except Exception as e:
                print(f"Lỗi khi đăng ký môn {ma_mon}: {e}")
                continue
        
        # Nếu đã đăng ký hết tất cả môn
        if not danh_sach_mon_hoc:
            print(f"\n🎉 [{datetime.now().strftime('%H:%M:%S')}] HOÀN THÀNH! Đã đăng ký hết tất cả môn học!")
            break
        
        # Chờ một chút trước khi lặp lại toàn bộ quá trình
        
#config
USERNAME = "23127423"
PASSWORD = "sory "
DANH_SACH_MON_HOC = ["5902"]
DANH_SACH_MON_HOC = {}

if __name__ == "__main__":
    try:
        auto_dang_ky_hoc_phan(USERNAME, PASSWORD, DANH_SACH_MON_HOC)
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Dừng chương trình bởi người dùng")
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Lỗi không mong muốn: {e}")
