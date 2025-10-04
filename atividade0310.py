# investidor10_cotacao_1dia.py
import os, time, shutil, tempfile, re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
# ===== AJUSTE 1: Importar o WebDriver-Manager para automatizar o chromedriver =====
from webdriver_manager.chrome import ChromeDriverManager

# ===== CONFIG =====
URL_HOME = "https://investidor10.com.br/"
TICKER   = "ITSA3"   # Troque aqui para testar outras ações (ex.: "PETR4", "VALE3")

HEADLESS = False     # Deixe False para ver o navegador funcionando
IMPLICIT_WAIT = 5
EXPLICIT_WAIT = 25
PROFILE_DIR = None

# ===== AJUSTE 2: REMOVER o caminho fixo do chromedriver. Não precisamos mais dele! =====
# CHROMEDRIVER_PATH = r"C:\Users\marco\Downloads\..." # << LINHA APAGADA

# ===== AJUSTE 3: Usar um caminho relativo para a pasta de downloads =====
# Isso cria a pasta dentro do seu projeto, evitando erros de permissão.
DOWNLOAD_DIR = "downloads_projeto"
SCREENSHOT_NAME = f"cotacao_{TICKER.lower()}_1dia.png"

# ---------- Utils ----------
def _extrair_numero_brl(texto: str):
    """
    Extrai o primeiro número em formato BR (R$ 13,45 / 13,45 / 1.234,56) -> (float, texto_original)
    """
    if not texto:
        return None, None
    m = re.search(r"(R\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+,\d+)", texto)
    if not m:
        return None, None
    bruto = m.group(0)
    num = m.group(2) if m.group(2) else bruto
    num_normal = num.replace(".", "").replace(",", ".")
    try:
        return float(num_normal), bruto.strip()
    except ValueError:
        return None, None

# ---------- Selenium setup ----------
def create_driver(headless: bool = False):
    global PROFILE_DIR
    PROFILE_DIR = tempfile.mkdtemp(prefix="selenium_profile_")

    # ===== AJUSTE 4: REMOVER a verificação do caminho antigo =====
    # A verificação 'if not os.path.exists(CHROMEDRIVER_PATH):' foi apagada.

    # Garante que a pasta de downloads exista no seu projeto
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")

    prefs = {
        "download.default_directory": os.path.abspath(DOWNLOAD_DIR), # Usar caminho absoluto gerado dinamicamente
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True,
    }
    options.add_experimental_option("prefs", prefs)

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    # ===== AJUSTE 5: Usar o WebDriver-Manager para configurar o driver automaticamente =====
    print("Configurando o ChromeDriver automaticamente...")
    service = ChromeService(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(IMPLICIT_WAIT)
    print("Driver criado com sucesso!")
    return driver

# (O restante do seu código, a partir daqui, continua igual pois já está excelente)
def clicar_elemento_por_texto(container, texto, timeout=EXPLICIT_WAIT):
    texto_lower = repr(texto.lower())[1:-1]
    xpath = (
        f".//a[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÀÉÊÍÓÔÕÚÇ','abcdefghijklmnopqrstuvwxyzáâãàéêíóôõúç'),'{texto_lower}')] | "
        f".//button[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÀÉÊÍÓÔÕÚÇ','abcdefghijklmnopqrstuvwxyzáâãàéêíóôõúç'),'{texto_lower}')] | "
        f".//*[self::li or self::span or self::div][contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÀÉÊÍÓÔÕÚÇ','abcdefghijklmnopqrstuvwxyzáâãàéêíóôõúç'),'{texto_lower}')]"
    )
    el = WebDriverWait(container, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    el.click()
    return True

def tentar_fechar_cookies(driver):
    textos = ["Aceitar", "Aceitar todos", "Concordo", "Entendi", "OK", "Fechar", "Continuar", "Prosseguir", "Permitir"]
    for t in textos:
        try:
            clicar_elemento_por_texto(driver, t, timeout=5)
            time.sleep(0.3)
            return True
        except Exception:
            pass
    return False

def abrir_pagina_acao(driver, ticker: str):
    destino = f"https://investidor10.com.br/acoes/{ticker.lower()}/"
    try:
        driver.get(destino)
        WebDriverWait(driver, EXPLICIT_WAIT).until(
            EC.presence_of_element_located((By.XPATH, f"//h1[contains(., '{ticker.upper()}')] | //h2[contains(., '{ticker.upper()}')]"))
        )
        return True
    except TimeoutException:
        driver.get(URL_HOME)
        tentar_fechar_cookies(driver)
        try:
            clicar_elemento_por_texto(driver, "Ações", timeout=8)
            time.sleep(0.5)
        except Exception:
            pass
        try:
            clicar_elemento_por_texto(driver, ticker.upper(), timeout=8)
            return True
        except Exception:
            pass
        return False

def obter_cotacao_atual(driver, ticker: str):
    wait = WebDriverWait(driver, 10)
    try:
        bloco = wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[self::div or self::section]"
            "[.//*[self::div or self::span or self::strong or self::h3 or self::h4]"
            "[normalize-space(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÀÉÊÍÓÔÕÚÇ','abcdefghijklmnopqrstuvwxyzáâãàéêíóôõúç'))='cotação']][1]"
        )))
    except TimeoutException:
        return None, None
    candidatos_xp = [
        ".//span[contains(.,'R$')][1]", ".//strong[contains(.,'R$')][1]",
        ".//div[contains(.,'R$')][1]", ".//p[contains(.,'R$')][1]",
        ".//span[normalize-space(.)][1]", ".//strong[normalize-space(.)][1]",
        ".//div[normalize-space(.)][1]", ".//p[normalize-space(.)][1]",
    ]
    texto_encontrado = ""
    for xp in candidatos_xp:
        try:
            el = bloco.find_element(By.XPATH, xp)
            txt = (el.text or "").strip()
            if not txt: continue
            if "R$" in txt or re.search(r"\d{1,3}(?:\.\d{3})*,\d{2}", txt):
                texto_encontrado = txt
                break
        except Exception:
            continue
    if not texto_encontrado: return None, None
    val, bruto = _extrair_numero_brl(texto_encontrado)
    return val, (bruto or texto_encontrado)

def encontrar_aba_1_dia(container, timeout=EXPLICIT_WAIT):
    tentativas = [
        ".//a[normalize-space(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'))='1 dia']",
        ".//button[normalize-space(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'))='1 dia']",
        ".//*[self::li or self::span or self::div][normalize-space(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'))='1 dia']",
        ".//*[@data-range='1d']",
    ]
    fim = time.time() + timeout
    last_err = None
    while time.time() < fim:
        for xp in tentativas:
            try:
                el = container.find_element(By.XPATH, xp)
                return el
            except Exception as e:
                last_err = e
        time.sleep(0.2)
    raise TimeoutException(f"Não localizei a aba '1 dia'. Último erro: {last_err}")

def mostrar_aba_1_dia_e_print(driver, ticker: str, out_path: str):
    wait = WebDriverWait(driver, EXPLICIT_WAIT)
    tentar_fechar_cookies(driver)
    sec = wait.until(EC.presence_of_element_located(
        (By.XPATH, f"//h2[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÀÉÊÍÓÔÕÚÇ','abcdefghijklmnopqrstuvwxyzáâãàéêíóôõúç'), 'cotação {ticker.lower()}')]/ancestor::*[self::section or self::div][1]")
    ))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", sec)
    time.sleep(0.4)
    driver.execute_script("window.scrollBy(0, -120);")
    try:
        aba = encontrar_aba_1_dia(sec, timeout=10)
    except TimeoutException:
        aba = encontrar_aba_1_dia(driver, timeout=8)
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(aba))
        aba.click()
    except Exception:
        driver.execute_script("arguments[0].click();", aba)
    time.sleep(1.0)
    out_full = os.path.join(DOWNLOAD_DIR, out_path)
    try:
        sec.screenshot(out_full)
        print(f"[OK] Screenshot (1 dia) salvo em: {out_full}")
    except WebDriverException:
        driver.save_screenshot(out_full)
        print(f"[WARN] Screenshot do elemento falhou; salvei a janela inteira: {out_full}")

def main():
    driver = None
    try:
        driver = create_driver(HEADLESS)
        if not abrir_pagina_acao(driver, TICKER):
            print("Não consegui abrir a página da ação.")
            return
        valor, bruto = obter_cotacao_atual(driver, TICKER)
        if valor is not None:
            print(f"[INFO] COTAÇÃO {TICKER}: {bruto}  (numérico: {valor:.2f})")
        else:
            print(f"[WARN] Não consegui ler a COTAÇÃO de {TICKER} (card 'COTAÇÃO').")
        mostrar_aba_1_dia_e_print(driver, TICKER, SCREENSHOT_NAME)
        if not HEADLESS:
            print("Deixando o navegador aberto por 6s para inspeção…")
            time.sleep(6)
        if valor is not None:
            print(f"\n==== RESUMO ====\nCOTAÇÃO {TICKER} agora: {bruto} (~{valor:.2f})\nScreenshot: {os.path.join(DOWNLOAD_DIR, SCREENSHOT_NAME)}\n")
        else:
            print("\n==== RESUMO ====\nCOTAÇÃO não encontrada. Veja o screenshot para ajustar o seletor.\n")
    finally:
        if driver:
            driver.quit()
        global PROFILE_DIR
        if PROFILE_DIR and os.path.isdir(PROFILE_DIR):
            shutil.rmtree(PROFILE_DIR, ignore_errors=True)

if __name__ == "__main__":
    main()