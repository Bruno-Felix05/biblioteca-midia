import streamlit as st
import requests
import mysql.connector
import time

chave_api = 'chave_aqui'

st.set_page_config(page_title="Biblioteca de jogos", layout="centered")

try:
    #CONECXÃO COM BANCO DE DADOS
    conexao = mysql.connector.connect(
        host="your_host",
        user="your_user",
        password="your_password",
        database="'database_name'"
    )
    cursor = conexao.cursor()

    comando_criar_tabela = """

    CREATE TABLE IF NOT EXISTS 'biblioteca' (
        id INT AUTO_INCREMENT PRIMARY KEY,
        titulo VARCHAR(100) NOT NULL,
        imagem VARCHAR(100),
        status VARCHAR(20),
        avaliacao VARCHAR(20),
        plataforma VARCHAR(20)
    )

    """
    cursor.execute(comando_criar_tabela)

    tab1, tab2 = st.tabs(["Pesquisa", "Minha Biblioteca"])

    with tab1:
            if 'lista_de_jogos' not in st.session_state:
                st.session_state['lista_de_jogos'] = []
            st.title('Pesquisa de jogos')
            nome_jogo = st.text_input('Digite o nome do jogo') # Caixa de pesquisa
            pesquisar = st.button(label='Pesquisar', key='b_pesquisar') # Botao de pesquuisa
            st.divider() # Linha divisoria

            if pesquisar: # Chama API

                with st.spinner('Pesquisando...',show_time=True):
                    time.sleep(4)
                    if nome_jogo.strip() != '':
                        url_api = f'https://api.rawg.io/api/games?key={chave_api}&search={nome_jogo}&page_size=20' # Chama URL de pesquisa
                        resposta = requests.get(url_api)
                        dados_jogo = resposta.json()
                        st.session_state['lista_de_jogos'] = dados_jogo['results'] #Recebe o json

            for item in st.session_state['lista_de_jogos']: # Percorre o json
                imagem, info, add_library = st.columns([4,2,1])
                st.divider() # Linha divisoria

                with imagem: # Capa do Jogo
                    if item['background_image']:
                        st.image(item['background_image'])
                    else:
                        st.write("🚫 Capa indisponível")  

                with info:
                    st.subheader(item['name'])
                    st.caption(f"Data de lançamento: {item['released']}")
                    st.caption(f'Nota: {item['metacritic']}')                         

                with add_library:
                    jogado = st.button(label='🎮 Adicionar', key=f'b_adicionar{item['id']}', help='Adicionar na biblioteca')  

                    if jogado:# Adicionar dados                  
                        comando_inserir = "INSERT INTO biblioteca (titulo, imagem, status, avaliacao,plataforma) VALUES (%s, %s, %s, %s,%s)"
                        valores = (item['name'], item['background_image'], '', '','')
                        cursor.execute(comando_inserir, valores)
                        conexao.commit()
                        st.success(f'{item['name']} adicionado a sua biblioteca')

    with tab2: #Leitura dos dados na outra aba (minha biblioteca)
        import pandas as pd

        st.header("Minha Biblioteca🎮")
        comando_ler = 'SELECT * FROM biblioteca'
        cursor.execute(comando_ler)
        jogos_encontrado = cursor.fetchall()

        if len(jogos_encontrado) == 0:
            st.write('Nenhum jogo adicionado ainda!')
        else:

            tabela = pd.DataFrame(jogos_encontrado, columns=["id", "titulo", "imagem", "status", "avaliacao", "plataforma"])
            
            for index, linha in tabela.iterrows():
                capa, informacoes, status_avaliacao_remover = st.columns([4, 2, 2])
               
                with capa:
                    st.image(linha['imagem'])

                with informacoes:

                    st.subheader(linha['titulo'])
                    st.caption(f"Status: {linha['status']}")
                    st.caption(f"Nota: {linha['avaliacao']}")
                    st.caption(f"Plataforma: {linha['plataforma']}")

                with status_avaliacao_remover: #Coluna onde conte as opçoes de Altera e remover
                    botao_remover = st.button('🗑️',key=index, help='Romover o jogo da sua biblioteca')
                    if botao_remover: #Remover da biblioteca
                        comando_apagar = "DELETE FROM biblioteca WHERE id = %s"
                        valores = (linha['id'],)
                        cursor.execute(comando_apagar, valores)
                        conexao.commit()
                        st.rerun()

                    with st.popover('✏️'): #Adicionar o status ou avaliação
                        #atualizar_status = st.text_input('Status atual do jogo', value=linha['status'],key=f'texto_{index}').upper()
                        atualizar_status = st.radio('Status atual do jogo', ['Não iniciado','Em Jogo', 'Zerado'],key=f'texto_{index}')
                        #atualizar_avaliacao = st.text_input('Avaliação do jogo(Nota ou analise)', value=linha['avaliacao'],key=f'avaliacao_{index}').upper()
                        atualizar_avaliacao = st.slider('Avaliação do jogo', min_value=0, max_value=10, value= 0, key=f'avaliacao_{index}')
                        atualizar_plataforma = st.selectbox('Plataforma', ['XBOX','PLAYSTATION','STEAM','EPIC GAMES'],key=f'plataforma_{index}')
                        botao_atulizar = st.button('Alterar', key=f'Salvar_{index}')

                        if botao_atulizar:                              
                                comando_atualizar =  """
                                                    UPDATE biblioteca
                                                    SET status = %s, avaliacao = %s, plataforma = %s
                                                    WHERE id = %s
                                                    """

                                valores = (atualizar_status, atualizar_avaliacao,atualizar_plataforma, linha['id'])
                                cursor.execute(comando_atualizar, valores)
                                conexao.commit()
                                st.rerun()
                st.divider()

except mysql.connector.Error as erro:

    st.error(f"Erro no banco de dados: {erro}")

    st.stop()