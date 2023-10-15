from __init__ import *
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from getpass import getpass
from time import sleep
from datetime import datetime
import subprocess


options = Options()
options.add_argument("--headless")
options.page_load_strategy = 'eager'
service = Service(executable_path=f'{os.path.expanduser("~/Downloads")}/geckodriver')


def session_desktop():
    clean_up()
    clear(command=clear_arg)
    print("Spawning session...")
    global driver, wait
    driver = webdriver.Firefox(options=options, service=service)
    wait = WebDriverWait(driver, timeout=30)
    driver.get("http://192.168.0.1/")
    sleep(5)


def session_mobile():

    # capabilities = {
    #     "browserName": "safari",
    #     "browserVersion": "", # iOS version
    #     "platformName": "iOS",
    #     "safari:deviceType": "iPhone",
    #     "safari:deviceName": "", # device name
    #     "safari:deviceUDID": "" # UDID from previous step
    #     }
    
    capabilities = dict(
    platformName='Android',
    automationName='uiautomator2',
    deviceName='Android',
    appPackage='com.android.settings',
    appActivity='.Settings',
    language='en',
    locale='US'
    )

    clean_up()
    clear(command=clear_arg)
    print("Spawning session...")
    global driver, wait
    driver = webdriver.Remote("http://192.168.0.1/", capabilities)
    wait = WebDriverWait(driver, timeout=30)
    driver.get("http://192.168.0.1/")
    sleep(5)


if platform in ("ios", "android"):
    from appium import webdriver
    from appium.webdriver.common.appiumby import AppiumBy as By
    session = session_mobile
else:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    session = session_desktop


class RSSID:

    def rssid_mac(self):
        rssid_value = subprocess.run(["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"], 
                                    stdout=subprocess.PIPE, 
                                    text=True)

        rssid_value = rssid_value.stdout.split()

        if (rssid_value[28] == "MCS:"):
            rssid = rssid_value[27]
            return rssid
        elif (rssid_value[29] == "MCS:"):
            rssid = " ".join([rssid_value[27], rssid_value[28]])
            return rssid
        elif (rssid_value[30] == "MCS:"):
            rssid = " ".join([rssid_value[27], rssid_value[28], rssid_value[30]])
            return rssid

    def rssid_windows(self):
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
    
    def rssid_linux(self):
        rssid = str(subprocess.check_output(['iwgetid -r'], shell=True)).split('\'')[1][:-2]
        return rssid

    def rssid_ios(self):
        pass


def display(rssid_init, isp=None, network_mode=None, switch=None, connection=None, state=None, percentage=None, users=None):

    print(f"SSID: {rssid_init}\t\tBATTERY: {percentage}")
    print(f"ISP: {isp}\t\tUsers: {users}".upper())
    print(f"Band: {network_mode}\t\tState: {state}".upper())
    print(f"Internet: {switch}\t\tConnection: {connection}".upper())


class Auth:

    def retry(self):
        clear(command=clear_arg)
        char = ("y", "n")
        print("\tRetry login?\n")
        print("Y. Yes")
        print("N. No")
        print("")

        asker = input("Enter here: ").lower().strip()
        if asker not in char:
            print("Invalid option")
            sleep(1)
            return self.retry()
        
        if asker == "y":
            return self.login()
        elif asker == "n":
            return "failed"


    def login(self):
        clear(command=clear_arg)
        username = input("Input your username: ")
        password = getpass("Input your password: ")
        
        settings_button = driver.find_element(By.ID, "menu2")
        wait.until(EC.element_to_be_clickable(settings_button)).click()
        sleep(2)

        username_button = driver.find_element(By.ID, "tbarouter_username")
        password_button = driver.find_element(By.ID, "tbarouter_password")
        signin_btn = driver.find_element(By.ID, "btnSignIn")
        close_login = driver.find_element(By.CSS_SELECTOR, "#loginBox > div > div.btnWrapper > a")

        username_button.send_keys(f"{username}")
        sleep(1)
        print("Logging in")
        password_button.send_keys(f"{password}")
        sleep(1)
        wait.until(EC.element_to_be_clickable(signin_btn)).click()
        sleep(3)
        
        if driver.find_element(By.CSS_SELECTOR, "#lloginfailed").is_displayed():
            print("INVALID CREDENTIALS")
            with open(f"{runtime_path}/auth_log.txt", "a+") as file:
                file.write(f"Failed login attempt at {datetime.now()}\n")
            sleep(1)
            print("This incident will be reported")
            sleep(0.5)
            close_login.click()
            sleep(1)
            return self.retry()
        
        # Indicate if network is locked
        try:
            cancel = driver.find_element(By.CSS_SELECTOR, "#confirmDlg > a:nth-child(2)")
            if (driver.find_element(By.CSS_SELECTOR, "#lt_confirmDlg_title").is_displayed) and (cancel.is_displayed):
                cancel.click()
                print("SIM RESTRICTED")
                sleep(1)
        finally:
            print("Logged in successfully")
            sleep(2)
            return


    def logout(self):
        print("Logging out")
        sleep(1)
        logout_btn = driver.find_element(By.ID, "MainLogOut")
        logout_btn.click()
        sleep(3)
        print("Logged out successfully")
        sleep(2)


class Balance:
    
    # Configured for Nigerian ISPs

    def balance_check_glo(self):
        balance_checker_button = driver.find_element(By.CSS_SELECTOR, "#mBalanceChecker > a")
        balance_checker_button.click()
        sleep(3)
        ussd_field = driver.find_element(By.CSS_SELECTOR, "#txt_send_ussd")
        ussd_send = driver.find_element(By.CSS_SELECTOR, "#btn_send_ussd_code")
        ussd_field.send_keys("*323#")
        sleep(1)
        ussd_send.click()
        print("Checking balance")
        sleep(10)

        driver.save_screenshot(desktop_location)
        print("Screenshot of balance inquiry has been saved to desktop")
        sleep(2)


    def balance_check_airtel_9mobile(self):
        balance_checker_button = driver.find_element(By.CSS_SELECTOR, "#mBalanceChecker > a")
        sms_button = driver.find_element(By.CSS_SELECTOR, "#mSMS > a")
        balance_checker_button.click()
        sleep(3)
        ussd_field = driver.find_element(By.CSS_SELECTOR, "#txt_send_ussd")
        ussd_send = driver.find_element(By.CSS_SELECTOR, "#btn_send_ussd_code")
        ussd_field.send_keys("*323#")
        sleep(1)
        ussd_send.click()
        print("Checking balance")
        sleep(10)

        # View in messages
        sms_button.click()
        sleep(2)
        message = driver.find_element(By.CSS_SELECTOR, "#LRCV9\,LRCV10\, > td:nth-child(2)")
        message.click()
        sleep(1.5)
        driver.save_screenshot(desktop_location)
        print("Screenshot of balance inquiry has been saved to desktop")
        sleep(2)
        
    
    def balance_check_mtn(self):
        balance_checker_button = driver.find_element(By.CSS_SELECTOR, "#mBalanceChecker > a")
        balance_checker_button.click()
        sleep(3)
        ussd_field = driver.find_element(By.CSS_SELECTOR, "#txt_send_ussd")
        ussd_send = driver.find_element(By.CSS_SELECTOR, "#btn_send_ussd_code")
        ussd_field.send_keys("*323*4#")
        sleep(1)
        ussd_send.click()
        print("Checking balance")
        sleep(10)

        driver.save_screenshot(desktop_location)
        print("Screenshot of balance inquiry has been saved to desktop")
        sleep(2)


def band_switch():
    char = ('1','2','3','4','5','6','0','x')
    clear(command=clear_arg)
    print("\tChoose an option:\n")
    
    print("1. 4G throttle")
    print("2. 3G throttle")

    print("3. 4G only")
    print("4. 4G/3G")
    print("5. 3G only")
    print("6. 2G only")

    print("")
    print("0. Main menu")
    print("X. Exit")

    asker = input("\nEnter here: ").lower().strip()
    if asker not in char:
        print("Invalid option!")
        sleep(1)
        return band_switch()
    elif asker == 'x':
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
            sleep(10)
            wait.until(EC.element_to_be_clickable(mode_select)).click()
            fourGO.click()
            
        elif asker == "2":
            print("Throttling 3G...")
            fourGO.click()
            save_btn.click()
            sleep(10)
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
    finally:
        print("Saving configurations")
        sleep(1)
        save_btn.click()
        sleep(10)
        wait.until(EC.element_to_be_clickable(mode_select)).click()
        print("Done")
        sleep(2)
        return band_switch()


def decider(arg1=None):
    char = ('1','2','3','4','5','6','r','x','m')
    arg = None
    sleep(0.5)
    clear(command=clear_arg)
    try:
        logout_btn_check = driver.find_element(By.ID, "MainLogOut").is_displayed()
        switch_status = driver.find_element(By.CSS_SELECTOR, "#txtConnected").get_property("innerText")
        curr_network_mode = driver.find_element(By.CSS_SELECTOR, "#txtSystemNetworkMode").get_property("innerText")
        curr_isp = driver.find_element(By.CSS_SELECTOR, "#txtNetworkOperator").get_property("innerText")
        curr_percentage = driver.find_element(By.CSS_SELECTOR, "#lDashBatteryQuantity").get_property("innerText")
        curr_users = driver.find_element(By.CSS_SELECTOR, "#lConnDeviceValue").get_attribute("value")
        curr_rate = driver.find_element(By.ID, "txtSpeed").get_property("innerText").split("\n")

        if logout_btn_check:
            curr_state = "logged in"
        else:
            curr_state = "logged out"

        if switch_status == "Disconnected":
            curr_switch = "off"
        else:
            curr_switch = "on"

        if arg1 is None:
            arg1 = f"⬆ {curr_rate[0]} ⬇ {curr_rate[-1]}"
        else:
            arg1 = f"{arg1} ⬆ {curr_rate[0]} ⬇ {curr_rate[-1]}"

        if curr_percentage in ("10%", "20%"):
            curr_percentage = f"{curr_percentage} 🚨"

    finally:
        display(rssid_init, isp=curr_isp, network_mode=curr_network_mode, switch=curr_switch, connection=arg1, state=curr_state, percentage=curr_percentage, users=curr_users)

    print("\n\tChoose an option:\n")
    print("1. Login")
    print("2. Logout")
    print("3. Test internet connection")
    print("4. Switch internet ON/OFF")
    print("5. Check data balance")
    print("6. Throttle / Switch network bands")
    print("")
    print("R. Refresh")
    print("M. Monitor mode")
    print("X. Exit")

    asker = input("\nEnter here: ").lower().strip()
    if asker not in char:
        print("Invalid option!")
        sleep(1)
        return decider()
    elif asker == 'r':
        return decider()
    elif asker == 'm':
        return decider_m()
    elif asker == 'x':
        driver.quit()
        return

   
    try:
        logout_btn_check = driver.find_element(By.ID, "MainLogOut").is_displayed()
        switch_btn = driver.find_element(By.CSS_SELECTOR, "#switchBtn_connStatus > div")
        connection_state = None

        if asker == '1':
            if logout_btn_check:
                print("Already logged in")
            else:
                auth_init.login()
            sleep(1)

        elif asker == '2':
            if logout_btn_check:
                auth_init.logout()
            else:
                print("Already logged out")
            sleep(1)

        elif asker == '3':
            original_window = driver.current_window_handle
            driver.switch_to.new_window('tab')
            try:
                driver.get("https://www.google.com/")
            except:
                print("Connection inactive")
                connection_state = "inactive"
            else:
                print("Connection active")
                connection_state = "active"
            finally:
                driver.close()
                driver.switch_to.window(original_window)
                sleep(1)
        
        elif asker == '4':
            wait.until(EC.element_to_be_clickable(switch_btn)).click()
            print("Switching...")
            sleep(8)
            print("Done")
       
        elif asker == '5':
            if not logout_btn_check:
                auth_init.login()
                wait.until(EC.element_to_be_clickable(driver.find_element(By.ID, "menu1"))).click()
                sleep(1)
            print("Loading configurations...")
            
            if ("9mobile" in curr_isp) or ("airtel" in curr_isp):
                balance_init.balance_check_airtel_9mobile()
            elif "glo" in curr_isp:
                balance_init.balance_check_glo()
            elif "mtn" in curr_isp:
                balance_init.balance_check_mtn()
            else:
                print("Invalid SIM card")
                sleep(1)

        elif asker == '6':
            arg2 = None
            if not logout_btn_check:
                arg2 = auth_init.login()
            if arg2 == "failed":
                raise Exception

            print("Loading configurations...")
            
            settings_button = driver.find_element(By.ID, "menu2")
            wait.until(EC.element_to_be_clickable(settings_button)).click()
            sleep(2)

            # Indicate if network is locked
            try:
                cancel = driver.find_element(By.CSS_SELECTOR, "#confirmDlg > a:nth-child(2)")
                if (driver.find_element(By.CSS_SELECTOR, "#lt_confirmDlg_title").is_displayed) and (cancel.is_displayed):
                    cancel.click()
                    sleep(2)
            except:
                pass

            connection = driver.find_element(By.CSS_SELECTOR, "#mInternetConn > a")
            wait.until(EC.element_to_be_clickable(connection)).click()
            sleep(2)
            
            mode_select = driver.find_element(By.CSS_SELECTOR, "#network_selectModeType")
            mode_select.click()

            arg = band_switch()

    except Exception:
        pass
    except:
        print("Exception occured")
    finally:
        if arg:
            driver.quit()
            return
        
        wait.until(EC.element_to_be_clickable(driver.find_element(By.ID, "menu1"))).click()
        return decider(arg1=connection_state)


def decider_m(arg1=None):
    try:
        sleep(0.5)
        clear(command=clear_arg)
        try:
            logout_btn_check = driver.find_element(By.ID, "MainLogOut").is_displayed()
            switch_status = driver.find_element(By.CSS_SELECTOR, "#txtConnected").get_property("innerText")
            curr_network_mode = driver.find_element(By.CSS_SELECTOR, "#txtSystemNetworkMode").get_property("innerText")
            curr_isp = driver.find_element(By.CSS_SELECTOR, "#txtNetworkOperator").get_property("innerText")
            curr_percentage = driver.find_element(By.CSS_SELECTOR, "#lDashBatteryQuantity").get_property("innerText")
            curr_users = driver.find_element(By.CSS_SELECTOR, "#lConnDeviceValue").get_attribute("value")
            curr_rate = driver.find_element(By.ID, "txtSpeed").get_property("innerText").split("\n")

            if logout_btn_check:
                curr_state = "logged in"
            else:
                curr_state = "logged out"

            if switch_status == "Disconnected":
                curr_switch = "off"
            else:
                curr_switch = "on"

            if arg1 is None:
                arg1 = f"⬆ {curr_rate[0]} ⬇ {curr_rate[-1]}"
            else:
                arg1 = f"{arg1} ⬆ {curr_rate[0]} ⬇ {curr_rate[-1]}"

            if curr_percentage in ("10%", "20%"):
                curr_percentage = f"{curr_percentage} 🚨"

        finally:
            display(rssid_init, isp=curr_isp, network_mode=curr_network_mode, switch=curr_switch, connection=arg1, state=curr_state, percentage=curr_percentage, users=curr_users)
            print("\nPress CTRL + C to exit monitor mode")
            sleep(4.5)
            return decider_m()
    except (KeyboardInterrupt, SystemExit):
        session()
        return decider()


# SSID fetch
try:
    rssid_init = RSSID()
    if platform == "darwin":
        rssid_init = rssid_init.rssid_mac()

    elif platform == "linux":
        rssid_init = rssid_init.rssid_linux()

    elif platform == "win32":
        rssid_init = rssid_init.rssid_windows()

    elif platform == "ios":
        rssid_init = rssid_init.rssid_ios()
except:
    rssid_init = "USB"


# start session
try:
    session()
except:
    driver.quit()
    exit("Router unavailable")
else:
    auth_init = Auth()
    balance_init = Balance()
    clear(command=clear_arg)




if __name__ == "__main__":

    try:
        decider()
    except:
        driver.quit()
        exit("Critical error")
    else:
        exit("Exiting")


