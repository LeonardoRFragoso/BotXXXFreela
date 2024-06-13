import os
import json
import random
import time
import requests
import re
from google.cloud import firestore
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google.oauth2 import service_account
import sys

# Configurar a codificação do terminal para UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Carregar as credenciais do Firebase a partir do arquivo JSON
with open('firebase_credentials.json') as f:
    firebase_config = json.load(f)

credentials = service_account.Credentials.from_service_account_info(firebase_config)
db = firestore.Client(credentials=credentials)

def enviar_mensagem_ntfy(chat, mensagem, anexo=None):
    try:
        url = f'https://ntfy.sh/{chat}'
        headers = {'Content-Type': 'text/plain'}
        if anexo:
            headers['Attach'] = anexo
        response = requests.post(url, data=mensagem, headers=headers)
        if response.ok:
            print(f'Mensagem enviada com sucesso: {mensagem}')
        else:
            print(f'Falha ao enviar a mensagem: {response.status} {response.reason}')
    except Exception as e:
        print(f'Erro ao enviar a mensagem: {e}')

def make_request(method, url, data=None, auth_token=None):
    try:
        headers = {'Authorization': f'Bearer {auth_token}'} if auth_token else {}
        response = requests.request(method, url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f'Erro ao fazer a requisição: {e}')
        raise

def fetch_credentials():
    users_ref = db.collection('users')
    active_users = users_ref.where('status', '==', 'active').stream()
    users = [user.to_dict() for user in active_users]
    if not users:
        raise ValueError('Nenhum usuário ativo encontrado no banco de dados.')
    return random.choice(users)

def deactivate_user(user_id, reason):
    user_ref = db.collection('users').document(user_id)
    user_ref.update({
        'status': 'inactive',
        'reason': reason
    })
    print(f'Usuário {user_id} desativado por motivo: {reason}')

def process_requests(browser):
    api_endpoints = [
        "http://66.94.119.151:8665/guard.php",
        "http://66.94.119.151:8665/guard-alt.php",
        "http://66.94.119.151:8665/guard-alt3.php"
    ]

    erro = False
    count = 0

    print(" ## X-RED DOWNLOADER 1.0")
    print(' -- DEV_MODE', os.getenv('DEV_MODE'))
    print(' -- LIMIT_HITS', os.getenv('LIMIT_HITS'))
    if os.getenv('DEV_MODE') == '0':
        pass
    else:
        print(' -- SIMULAÇÂO, NÃO SERA ENVIADO')
    print(" -- Starting... ")

    print(" -- Navegando para xvideos.red ")
    browser.get('https://www.xvideos.red/')
    logout(browser)

    print(" -- Verificando disclaimer")
    time.sleep(0.5)
    try:
        # Aceitar a confirmação de idade
        button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="disclaimer-over18btn"]'))
        )
        button.click()
        print(' -- Disclaimer encontrado e clicado.')
    except:
        print(' -- Disclaimer não encontrado.')

    print(' -- Obtendo credenciais ')
    credentials = fetch_credentials()
    email, password, user_id = credentials['email'], credentials['password'], credentials['id']
    print(" -- Usuário:", email)
    print(" -- Senha:", password)

    print(' -- Clicando no login ')
    time.sleep(0.5)
    try:
        link = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.ID, 'main-signin-btn'))
        )
        link.click()
    except Exception as e:
        print(f'Erro ao clicar no login: {e}')
        return

    print(' -- Preenchendo credenciais')
    time.sleep(1)
    email_field = browser.find_element(By.ID, 'signin-form_login')
    email_field.clear()
    email_field.send_keys(email)
    time.sleep(0.5)
    password_field = browser.find_element(By.ID, 'signin-form_password')
    password_field.clear()
    password_field.send_keys(password)
    time.sleep(0.5)

    browser.find_element(By.CSS_SELECTOR, '.btn.login-submit.btn-danger.btn-lg').click()
    time.sleep(2.5)

    try:
        error_element = WebDriverWait(browser, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.help-block.error-block'))
        )
        print("Erro de login: Incapaz de entrar. Por favor, verifique o seu login / senha.")
        deactivate_user(user_id, 'email')
        erro = True
    except:
        print(' -- Usuário autenticado')

    time.sleep(1.5)
    try:
        verification_input_element = browser.find_element(By.ID, 'unknown-browser-form_code')
        print(" -- Desabilitando usuario")
        deactivate_user(user_id, 'security')
        erro = True
    except:
        print(" -- Elemento de código de verificação não encontrado.")

    try:
        expired_elements = browser.find_elements(By.XPATH, "//h3[text()='Your membership has expired. Please renew it to continue accessing XV PREMIUM.']")
        if expired_elements:
            print("A mensagem de associação expirada foi encontrada!")
            deactivate_user(user_id, 'expired')
            print(' -- o usuário foi desativado')
            erro = True
        else:
            print(" -- A mensagem de associação expirada não foi encontrada.")
    except:
        pass

    if not erro:
        print(" 🟩 Trabalhando...")
        time.sleep(1)

        processed_requests = set()  # Armazenar IDs de vídeos já processados

        while count < 26:  # Limitando para 26 solicitações
            for api_endpoint in api_endpoints:
                print(' -- Navegando para xvideos.red')
                print(api_endpoint)

                print(" -- Consultando novos pedidos...")

                leia = f"{api_endpoint}?action=readserver&value=0"
                browser.get(leia)
                line = browser.find_element(By.TAG_NAME, 'body').text

                if line == "sem pedidos...":
                    print(' -- Não há novos pedidos...')
                    time.sleep(0.5)
                else:
                    print(' -- Solicitação: ', line)
                    print(' --')

                    video = {}
                    nurl2 = line.split("/")
                    nurl = nurl2[3]

                    final_line = line.replace('xvideos.com', 'xvideos.red')
                    print(" -- Objetivo: ", final_line)

                    if line in processed_requests:
                        print(f" -- Vídeo {line} já processado. Pulando para o próximo.")
                        continue  # Pular para o próximo vídeo

                    try:
                        browser.get(final_line)

                        time.sleep(1)
                        try:
                            link_check = browser.find_element(By.ID, 'main-signin-btn')
                            erro = True
                            print(" -- FALHOU")
                            return
                        except:
                            print(' -- Usuário autenticado')

                        mensagem_presente = 'Network error: Please refresh the page.' in browser.page_source

                        if mensagem_presente:
                            print('Mensagem encontrada! Iniciando tentativas...')

                            tentativas = 0
                            max_tentativas = 5

                            while tentativas < max_tentativas:
                                browser.refresh()
                                mensagem_presente = 'Network error: Please refresh the page.' in browser.page_source

                                if mensagem_presente:
                                    print(f'Tentativa {tentativas + 1}: Mensagem encontrada! Pressionando F5...')
                                    tentativas += 1
                                else:
                                    print('Mensagem não encontrada. Saindo do loop de tentativas.')
                                    break
                        else:
                            print('Mensagem não encontrada inicialmente. Não iniciando tentativas.')

                        image_url = browser.find_element(By.CSS_SELECTOR, 'meta[property="og:image"]').get_attribute('content')
                        video['thumb'] = image_url

                        video_url = browser.find_element(By.CSS_SELECTOR, 'meta[property="og:url"]').get_attribute('content')
                        video_id = video_url.split('/')[-1]

                        video_title = browser.find_element(By.CSS_SELECTOR, 'meta[property="og:title"]').get_attribute('content')
                        video['nome'] = video_title

                        print('ID do vídeo:', video_id)
                    except Exception as e:
                        devolvexx = f"{api_endpoint}?action=update&value={line}&nome=0&thumb=0&shortname=0&linkhd=0"
                        browser.get(devolvexx)
                        continue

                    script_tags = browser.find_elements(By.TAG_NAME, 'script')

                    video_url_low_script_content = None

                    for script_tag in script_tags:
                        script_content = script_tag.get_attribute('innerHTML')

                        if script_content and "html5player.setVideoUrlLow" in script_content:
                            video_url_low_script_content = script_content
                            break

                    if video_url_low_script_content:
                        match = re.search(r"html5player\.setVideoUrlLow\('([^']+)'", video_url_low_script_content)
                        if match:
                            video_url_low = match.group(1)
                            video['video'] = video_url_low
                            print('Valor de html5player.setVideoUrlLow:', video_url_low)
                        else:
                            print('Não foi possível encontrar o valor de html5player.setVideoUrlLow')
                    else:
                        print('Script não encontrado na página')

                    try:
                        video_url = browser.find_element(By.CSS_SELECTOR, 'meta[property="og:url"]').get_attribute('content')
                        video_id = video_url.split('/')[-1]

                        print('ID do vídeo:', video_id)

                        link2 = f'https://www.xvideos.red/video-download/{video_id}/'

                        temporary_error = ''
                        print('------------------------ LINK ')
                        print(link2)
                        print('------------------------ LINK ')

                        print(' link2: ', link2)
                        browser.get(link2)
                        time.sleep(0.6)
                        nav2 = browser.page_source

                        print(nav2)

                        try:
                            json_match = re.search(r"<pre[^>]*>([\s\S]*?)<\/pre>", nav2)
                            if json_match:
                                json_text = json_match.group(1)
                                json_data = json.loads(json_text)

                                if 'ERROR' in json_data:
                                    print(' -- Erro ao tentar baixar o vídeo: ', json_data['ERROR'])

                                    if json_data['ERROR'] == 'This uploader has disabled downloads for their content.':
                                        print(video)
                                        temporary_error = 'DOWNLOAD_DISABLED'

                                    if json_data['ERROR'] == 'Este criador desativou os downloads do seu conte&amp;uacute;do.':
                                        print(video)
                                        temporary_error = 'DOWNLOAD_DISABLED'

                                    if json_data['ERROR'] == 'Access denied':
                                        print(video)
                                        temporary_error = 'PAID_VIDEO'

                                if temporary_error == 'DOWNLOAD_DISABLED':
                                    continue
                                else:
                                    if 'URL_MP4HD' in json_data:
                                        video['video'] = json_data['URL_MP4HD']
                                    elif 'MP4HD_AVAILABLE' in json_data:
                                        video['video'] = json_data['URL']
                                    elif 'URL_LOW' in json_data:
                                        video['video'] = json_data['URL_LOW']
                                    elif 'URL' in json_data:
                                        video['video'] = json_data['URL']

                                    try:
                                        video['video'] = video['video'].replace('?download=1', '')
                                    except Exception as e:
                                        print(' -- Erro ao tentar baixar o vídeo: ', e)

                                if temporary_error == 'PAID_VIDEO':
                                    raise ValueError('PAID_VIDEO')

                                print(json_data)
                                print('--------------')
                                print('Line:', line)
                                print('Name:', video['nome'])
                                print('thumb:', video['thumb'])
                                print('shortname:', nurl)
                                print('Video:', video['video'])
                                print('--------------')

                                if 'video' not in video:
                                    if video_url_low_script_content:
                                        devolve = f"{api_endpoint}?action=update&value={line}&nome={video['nome']}&thumb={video['thumb']}&shortname={nurl}&linkhd={video_url_low_script_content}"
                                        print(devolve)

                                        print('-----------')
                                        print('-----------')
                                        print('-------------- CONFIRMACAO RAPIDA')
                                        print(devolve)
                                        print('-------------- RAPIDA')

                                        if os.getenv('DEV_MODE') == '0':
                                            browser.get(devolve)
                                            count += 1
                                    else:
                                        raise ValueError('PAID_VIDEO')
                                else:
                                    devolve = f"{api_endpoint}?action=update&value={line}&nome={video['nome']}&thumb={video['thumb']}&shortname={nurl}&linkhd={video['video']}"

                                    print('-------------- CONFIRMACAO V1')
                                    print(devolve)
                                    print('-------------- CONFIRMACAO V1')
                                    if os.getenv('DEV_MODE') == '0':
                                        browser.get(devolve)
                                        print('Devolvido com sucesso!', devolve)

                                        print(video['nome'], video['video'], video['thumb'])

                                    print('Devolvido com sucesso!', devolve)
                                    count += 1
                            else:
                                raise ValueError('No JSON match found')
                        except Exception as e:
                            print(' -- Erro ao tentar obter os dados usando o JSON, tentando da forma legada')
                            print(e)
                            print(' -- Não foi possivel obter os dados usando o JSON, tentando da forma legada')

                            try:
                                video['video'] = re.search(r'URL_MP4HD(.*?)\?download=1', nav2).group(1)
                                print(video)
                                devolve = f"{api_endpoint}?action=update&value={line}&nome={video['nome']}&thumb={video['thumb']}&shortname={nurl}&linkhd={video['video']}"

                                print('-----------')
                                print('-----------')
                                print('-------------- CONFIRMACAO')
                                print(devolve)
                                print('-------------- CONFIRMACAO')

                                if os.getenv('DEV_MODE') == '0':
                                    browser.get(devolve)
                                    print('Devolvido com sucesso!', devolve)

                                enviar_mensagem_ntfy('XRED_ERROS_ALPHA', f'LEGACY-RAW-HTTP - O Processo foi obtido usando o método legado | {line}')

                                print("Link: " + video['video'])
                                print('-----------')
                                print('-----------')
                                count += 1
                            except Exception as xe:
                                enviar_mensagem_ntfy('XRED_ERROS_ALPHA', f'ERRO-10666X-HTTP - Erro ao tentar obter os dados primários | {line} | {xe} | {nav2}')

                                print(" -- VIDEO PAGO --")
                                print(" -- Erro: ", xe)
                                erro = True

                                devolvexx = f"{api_endpoint}?action=update&value={line}&nome=0&thumb=0&shortname=0&linkhd={line}&reason=purchase"
                                print('----------- CANCELANDO')
                                print(devolvexx)
                                print('----------- CANCELANDO')
                                if os.getenv('DEV_MODE') == '0':
                                    browser.get(devolvexx)
                    except Exception as e:
                        enviar_mensagem_ntfy('XRED_ERROS_ALPHA', f'INVALID {line} | {e} | ')

                        print(' Conteúdo inválido')
                        print(' Conteúdo inválido')
                        print(' ')
                        print(e)
                        print(' ')
                        print(' Conteúdo inválido')
                        devolvexx = f"{api_endpoint}?action=update&value={line}&nome=0&thumb=0&shortname=0&linkhd={line}&reason=invalid"

                        print('-----------')
                        print(devolvexx)
                        print('-----------')
                        if os.getenv('DEV_MODE') == '0':
                            browser.get(devolvexx)
                            time.sleep(0.4)

                    print(' [COUNT] ', count)

                    processed_requests.add(line)  # Adicionar o ID do vídeo aos processados

                    if count >= 26:
                        print('--------- LOGOUT')
                        enviar_mensagem_ntfy('XRED_SUCCESS_ALPHA', 'Efetuando Logout')
                        erro = True
                        logout(browser)
                        break

                if count >= 26:
                    break

            if count >= 26:
                break
    else:
        print('---------------------------------')
        print('Inconsistência no login')
        print('---------------------------------')

    browser.quit()
    print('Navegador fechado após processar 26 solicitações.')

def logout(browser):
    print('Realizando logout...')
    browser.get('https://www.xvideos.red/account/signout')
    print(" Limpando Cookies www.xvideos.red")
    cookies = browser.get_cookies()
    for cookie in cookies:
        browser.delete_cookie(cookie['name'])
    print("Logout realizado e cookies limpos.")

if __name__ == '__main__':
    print("Script iniciado")

    chrome_options = Options()
    chrome_options.add_argument('--incognito')  # Adiciona a opção de navegação anônima
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-plugins-discovery')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Caminho para o executável do ChromeDriver
    chrome_service = Service('C:/Users/Administrador/Documents/chromedriver-win64/chromedriver.exe')

    # Inicializar o navegador
    browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

    try:
        process_requests(browser)
    except Exception as e:
        print('Erro ao executar o script:', e)
        print('Encerrando o script...')

    print("Script encerrado após processar 26 solicitações.")
