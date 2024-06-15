# X-RED Downloader 1.0

## Descrição

Este projeto é um script Python que automatiza o processo de login e download de vídeos do site xvideos.red. Ele utiliza Selenium para navegar no site, fazer login com credenciais de usuários ativos armazenados no Firestore e processar solicitações de vídeos através de APIs.

Este bot foi desenvolvido sob medida em um trabalho meu como freelancer.

## Funcionalidades

- Login automático no site xvideos.red
- Processamento de até 26 solicitações de vídeo por execução
- Extração de informações de vídeo (URL, thumbnail, título)
- Download de vídeos e envio de mensagens de status
- Desativação de usuários inválidos ou inativos
- Envio de notificações utilizando o serviço ntfy.sh

## Requisitos

- Python 3.8 ou superior
- Google Cloud SDK configurado
- Selenium
- Google Cloud Firestore
- Google Cloud Service Account Credentials
- WebDriver para Google Chrome (chromedriver)

## Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/x-red-downloader.git
   cd x-red-downloader

