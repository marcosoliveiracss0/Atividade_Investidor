## Como Executar o Código (Passo a Passo)
Passo 1: Abrir a Pasta do Projeto
Abra o Visual Studio Code.

Vá em Arquivo (File) > Abrir Pasta... (Open Folder...).

Selecione a pasta do seu projeto (ex: Selenium-Investidor10-main) e clique em Selecionar pasta.

Passo 2: Abrir o Terminal Integrado
Com o projeto aberto, vá ao menu superior e clique em Terminal > Novo Terminal (New Terminal).

Um painel de terminal aparecerá na parte inferior do VS Code.

Passo 3: Ativar o Ambiente Virtual (O Passo Mais Importante!)
No terminal que acabou de abrir, digite o comando abaixo e pressione Enter:

PowerShell

.\.venv\Scripts\Activate.ps1
Confirmação: Você saberá que deu certo quando o início da linha do terminal mudar e mostrar (.venv), assim:

(venv) PS C:\Users\marco\Downloads\Selenium-Investidor10-main>

Passo 4: Executar o Script Python
Agora, com o ambiente virtual ativo, você está pronto para rodar o código. Digite o comando abaixo e pressione Enter:

Bash

python investidor10_cotacao_1dia.py
(Atenção: Se o nome do seu arquivo for diferente, substitua investidor10_cotacao_1dia.py pelo nome correto).

## O que Vai Acontecer em Seguida?
Se tudo estiver correto, você verá a mágica acontecer:

O terminal mostrará as mensagens que adicionamos, como "Configurando o ChromeDriver automaticamente...".

Uma janela do navegador Google Chrome se abrirá sozinha.

O robô navegará até o site investidor10.com.br, irá para a página da ação ITSA3.

Ele vai rolar a página, clicar na aba "1 dia" e extrair a cotação.

O terminal mostrará o valor da cotação e a mensagem de que o screenshot foi salvo.

Após uma pausa de 6 segundos, o navegador se fechará.

Na barra lateral do seu VS Code, uma nova pasta chamada downloads_projeto aparecerá, e dentro dela estará a imagem cotacao_itsa3_1dia.png.
