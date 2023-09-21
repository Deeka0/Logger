from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sys import platform
from getpass import getpass
import time, os, subprocess, pathlib, glob



options = Options()
options.add_argument("--headless")
options.page_load_strategy = 'eager'
service = Service(executable_path=f'{os.path.expanduser("~/Downloads")}/geckodriver')
runtime_path = str(pathlib.Path(__file__).parent.resolve())


def clean_up():
    files = glob.glob(f"{runtime_path}/*")
    for file in files:
        if file.endswith(".log"):
            os.remove(file)


class RSSID:
    def __init__(self) -> None:
        pass

    def rssid_mac():
        rssid_value = subprocess.run(["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"], 
                                    stdout=subprocess.PIPE, 
                                    text=True)

        rssid_value = rssid_value.stdout.split()
        rssid = rssid_value[27]
        return rssid

    def rssid_windows():
        subprocess_result = subprocess.Popen('netsh wlan show interfaces',
        shell=True,
        stdout=subprocess.PIPE)
        subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
        
        try:
            rssid_value = subprocess_output[0].decode('utf-8')
            rssid_value = rssid_value.split()

            if (rssid_value[30] == "BSSID"):
                rssid = rssid_value[29]
                return rssid
            elif (rssid_value[31] == "BSSID"):
                rssid = " ".join([rssid_value[29], rssid_value[30]])
                return rssid
            elif (rssid_value[32] == "BSSID"):
                rssid = " ".join([rssid_value[29], rssid_value[30], rssid_value[31]])
                return rssid
            
        except UnicodeDecodeError:
            rssid_value = str(subprocess_output).split()
        
            if (rssid_value[73] == "\\r\\n\\r\\n"):
                rssid = rssid_value[72]
                return rssid
            elif (rssid_value[74] == "\\r\\n\\r\\n"):
                rssid = " ".join([rssid_value[72], rssid_value[73]])
                return rssid
            elif (rssid_value[75] == "\\r\\n\\r\\n"):
                rssid = " ".join([rssid_value[72], rssid_value[73], rssid_value[74]])
                return rssid
    
    def rssid_linux():
        rssid = str(subprocess.check_output(['iwgetid -r'], shell=True)).split('\'')[1][:-2]
        return rssid

    def rssid_ios():
        pass


def display(rssid_init, isp=None, network_mode=None, switch=None, connection=None, state=None, percentage=None, users=None):
    print(f"SSID: {rssid_init}                                  BATTERY: {percentage}")
    print(f"ISP: {isp}                                      State: {state}".upper())
    print(f"Band: {network_mode}                                         Users: {users}".upper())
    print(f"Internet: {switch}                                     Connection: {connection}".upper())


def clear(command):
    return os.system(command)


def session_firefox():
    clean_up()
    clear(command=clear_arg)
    print("Spawning session...")
    global driver, wait
    driver = webdriver.Firefox(options=options, service=service)
    wait = WebDriverWait(driver, timeout=30)
    driver.get("http://192.168.0.1/")
    return time.sleep(5)


def session_safari():
    desired_cap = {
        "browserName": "safari",
        "browserVersion": "", # iOS version
        "platformName": "iOS",
        "safari:deviceType": "iPhone",
        "safari:deviceName": "", # device name
        "safari:deviceUDID": "" # UDID from previous step
        }
    clean_up()
    clear(command=clear_arg)
    print("Spawning session...")
    global driver, wait
    driver = webdriver.Safari(desired_capabilities=desired_cap)
    wait = WebDriverWait(driver, timeout=30)
    driver.get("http://192.168.0.1/")
    return time.sleep(5)


try:
    if (platform == "darwin") or (platform == "linux") or (platform == "linux2") or (platform == "ios"):
        clear_arg = "clear"
        desktop_location = f'{os.path.expanduser("~/Desktop")}/balance.png'
        
        if (platform == "darwin"):
            rssid_init = RSSID.rssid_mac()
        
        elif (platform == "linux") or (platform == "linux2"):
            rssid_init = RSSID.rssid_linux()
        
        elif (platform == "ios"):
            rssid_init = RSSID.rssid_ios()

    elif platform == "win32":
        clear_arg = "cls"
        desktop_location = f'{os.path.expanduser("~/Desktop")}\\balance.png'
        rssid_init = RSSID.rssid_windows()
    
    else:
        print("OS not available yet")

    if platform == "ios":
        session_safari()
    else:
        session_firefox()
        
    clear(command=clear_arg)
except:
    driver.quit()
    exit("Router unavailable")


class Auth:
    def __init__(self) -> None:
        pass

    def login():
        clear(command=clear_arg)
        username = input("Input your username: ")
        password = getpass("Input your password: ")
        
        settings_button = driver.find_element(By.ID, "menu2")
        wait.until(EC.element_to_be_clickable(settings_button)).click()
        time.sleep(2)

        username_button = driver.find_element(By.ID, "tbarouter_username")
        password_button = driver.find_element(By.ID, "tbarouter_password")
        signin_btn = driver.find_element(By.ID, "btnSignIn")
        close_login = driver.find_element(By.CSS_SELECTOR, "#loginBox > div > div.btnWrapper > a")

        username_button.send_keys(f"{username}")
        time.sleep(1)
        print("Logging in")
        password_button.send_keys(f"{password}")
        time.sleep(1)
        wait.until(EC.element_to_be_clickable(signin_btn)).click()
        time.sleep(3)
        
        if driver.find_element(By.CSS_SELECTOR, "#lloginfailed").is_displayed():
            print("INVALID CREDENTIALS")
            time.sleep(1)
            close_login.click()
            time.sleep(1)
            return Auth.login()

        # Indicate if network is locked
        try:
            cancel = driver.find_element(By.CSS_SELECTOR, "#confirmDlg > a:nth-child(2)")
            if (driver.find_element(By.CSS_SELECTOR, "#lt_confirmDlg_title").is_displayed) and (cancel.is_displayed):
                cancel.click()
                print("SIM RESTRICTED")
                time.sleep(1)
        except:
            pass
        print("Logged in successfully")
        return time.sleep(2)


    def logout():
        print("Logging out")
        time.sleep(1)
        logout_btn = driver.find_element(By.ID, "MainLogOut")
        logout_btn.click()
        time.sleep(3)
        print("Logged out successfully")
        return time.sleep(2)


class Balance:
    def __init__(self) -> None:
        pass

    def balance_check_glo():
        balance_checker_button = driver.find_element(By.CSS_SELECTOR, "#mBalanceChecker > a")
        balance_checker_button.click()
        time.sleep(3)
        ussd_field = driver.find_element(By.CSS_SELECTOR, "#txt_send_ussd")
        ussd_send = driver.find_element(By.CSS_SELECTOR, "#btn_send_ussd_code")
        ussd_field.send_keys("*323#")
        time.sleep(1)
        ussd_send.click()
        print("Checking balance")
        time.sleep(10)

        driver.save_screenshot(desktop_location)
        print("Screenshot of balance inquiry has been saved to desktop")
        time.sleep(2)


    def balance_check_airtel():
        balance_checker_button = driver.find_element(By.CSS_SELECTOR, "#mBalanceChecker > a")
        balance_checker_button.click()
        time.sleep(3)
        ussd_field = driver.find_element(By.CSS_SELECTOR, "#txt_send_ussd")
        ussd_send = driver.find_element(By.CSS_SELECTOR, "#btn_send_ussd_code")
        ussd_field.send_keys("*323#")
        time.sleep(1)
        ussd_send.click()
        print("Checking balance")
        time.sleep(10)

        # View in messages

        driver.save_screenshot(desktop_location)
        print("Screenshot of balance inquiry has been saved to desktop")
        time.sleep(2)
        
    
    def balance_check_mtn():
        pass

    def balance_check_9mobile():
        pass


def isp_choice():
    char = ('1','2','3','4','0','x','X')
    clear(command=clear_arg)
    print("\t\t\t\tSelect an ISP or network provider\t\t\t\t\n")
    print("1. 9mobile")
    print("2. Glo")
    print("3. Airtel")
    print("4. MTN")
    print("")
    print("0. Main menu")
    print("X. Exit")
    
    asker = input("\nEnter here: ").strip()
    if asker not in char:
        print("Invalid option")
        time.sleep(1)
        return isp_choice()
    elif (asker == 'x') or (asker == 'X'):
        return True
    elif asker == "0":
        return False
    
    try:
        if (asker == "1") or (asker == "4"):
            print("Unavailable")
            time.sleep(1)
            return isp_choice()
        elif asker == "2":
            Balance.balance_check_glo()
        elif asker == "3":
            Balance.balance_check_airtel()
    finally:
        return isp_choice()


def band_switch():
    char = ('1','2','3','4','5','6','0','x','X')
    clear(command=clear_arg)
    print("\t\t\t\tChoose an option\t\t\t\t\n")
    
    print("1. 4G throttle")
    print("2. 3G throttle")

    print("3. 4G only")
    print("4. 4G/3G")
    print("5. 3G only")
    print("6. 2G only")

    print("")
    print("0. Main menu")
    print("X. Exit")

    asker = input("\nEnter here: ").strip()
    if asker not in char:
        print("\t\t\tInvalid option!")
        time.sleep(1)
        return band_switch()
    elif (asker == 'x') or (asker == 'X'):
        return True
    elif asker == "0":
        return False
    
    try:
        mode_select = driver.find_element(By.CSS_SELECTOR, "#network_selectModeType")
        fourGO = driver.find_element(By.CSS_SELECTOR, "#type_4g_only")
        fourG_threeG = driver.find_element(By.CSS_SELECTOR, "#type_4g3g")
        threeGO = driver.find_element(By.CSS_SELECTOR, "#type_3g_only")
        twoGO = driver.find_element(By.CSS_SELECTOR, "#dropdown2Gonly")
        save_btn = driver.find_element(By.CSS_SELECTOR, "#btn_network_mode_apply")
        
        if (asker == "1"):
            print("Throttling 4G...")
            threeGO.click()
            save_btn.click()
            time.sleep(10)
            wait.until(EC.element_to_be_clickable(mode_select)).click()
            fourGO.click()
            
        elif asker == "2":
            print("Throttling 3G...")
            fourGO.click()
            save_btn.click()
            time.sleep(10)
            wait.until(EC.element_to_be_clickable(mode_select)).click()
            threeGO.click()

        if (asker == "3"):
            fourGO.click()
        elif (asker == "4"):
            fourG_threeG.click()
        elif asker == "5":
            threeGO.click()
        elif asker == "6":
            twoGO.click()

    except:
        pass
    finally:
        print("Saving configurations")
        time.sleep(1)
        save_btn.click()
        time.sleep(10)
        wait.until(EC.element_to_be_clickable(mode_select)).click()
        print("Done")
        time.sleep(2)
        return band_switch()
    

def decider():

    char = ('1','2','3','4','5','6','r','R','x','X')
    arg = None
    clear(command=clear_arg)
    try:
        logout_btn_check = driver.find_element(By.ID, "MainLogOut").is_displayed()
        switch_status = driver.find_element(By.CSS_SELECTOR, "#txtConnected").get_property("innerText")
        curr_network_mode = driver.find_element(By.CSS_SELECTOR, "#txtSystemNetworkMode").get_property("innerText")
        curr_isp = driver.find_element(By.CSS_SELECTOR, "#txtNetworkOperator").get_property("innerText")
        curr_percentage = driver.find_element(By.CSS_SELECTOR, "#lDashBatteryQuantity").get_property("innerText")
        curr_users = driver.find_element(By.CSS_SELECTOR, "#lConnDeviceValue").get_attribute("value")

        if logout_btn_check:
            curr_state = "Logged In"
        else:
            curr_state = "Logged Out"

        if switch_status == "Disconnected":
            curr_switch = "Off"
        else:
            curr_switch = "On"

    except:
        pass
    display(rssid_init, isp=curr_isp, network_mode=curr_network_mode, switch=curr_switch, connection=False, state=curr_state, percentage=curr_percentage, users=curr_users)

    print("\n\t\t\t\tChoose an option\t\t\t\t\n")
    print("1. Login")
    print("2. Logout")
    print("3. Test internet connection")
    print("4. Switch internet ON/OFF")
    print("5. Check data balance")
    print("6. Throttle / Switch network bands")
    print("")
    print("R. Refresh")
    print("X. Exit")

    asker = input("\nEnter here: ").strip()
    if asker not in char:
        print("\t\t\tInvalid option!")
        time.sleep(1)
        return decider()
    elif (asker == 'r') or (asker == 'R'):
        return decider()
    elif (asker == 'x') or (asker == 'X'):
        driver.quit()
        return exit()
   
    try:
        logout_btn_check = driver.find_element(By.ID, "MainLogOut").is_displayed()
        switch_btn = driver.find_element(By.CSS_SELECTOR, "#switchBtn_connStatus > div")
        
        if asker == '1':
            if logout_btn_check:
                print("Already logged in")
            else:
                Auth.login()
            time.sleep(1)

        elif asker == '2':
            if logout_btn_check:
                Auth.logout()
            else:
                print("Already logged out")
            time.sleep(1)

        elif asker == '3':
            original_window = driver.current_window_handle
            driver.switch_to.new_window('tab')
            try:
                driver.get("https://www.google.com/")
                time.sleep(3)
                # connection_state = "active"
                print("Connection active")
            except:
                # connection_state = "inactive"
                print("Connection inactive, try throttling")
            finally:
                driver.close()
                driver.switch_to.window(original_window)
                time.sleep(1)
        
        elif asker == '4':
            wait.until(EC.element_to_be_clickable(switch_btn)).click()
            print("Switching...")
            time.sleep(8)
            print("Done")
       
        elif asker == '5':
            if not logout_btn_check:
                Auth.login()
            print("Loading configurations...")
            arg = isp_choice()

        elif asker == '6':
            if not logout_btn_check:
                Auth.login()

            print("Loading configurations...")
            settings_button = driver.find_element(By.ID, "menu2")
            wait.until(EC.element_to_be_clickable(settings_button)).click()
            time.sleep(2)

            connection = driver.find_element(By.CSS_SELECTOR, "#mInternetConn > a")
            wait.until(EC.element_to_be_clickable(connection)).click()
            time.sleep(2)
            
            mode_select = driver.find_element(By.CSS_SELECTOR, "#network_selectModeType")
            mode_select.click()

            arg = band_switch()
    except:
        print("Exception occured")
    finally:
        if arg:
            driver.quit()
            return exit()
        
        wait.until(EC.element_to_be_clickable(driver.find_element(By.ID, "menu1"))).click()
        return decider()




if __name__ == "__main__":
    
    try:
        decider()
    except:
        driver.quit()
        if exit:
            exit("Exiting")
        exit("Critical error")


