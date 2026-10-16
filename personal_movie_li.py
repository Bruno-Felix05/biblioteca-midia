import streamlit as st
import requests
import mysql.connector
import pandas as pd
st.markdown("<div id='topo'></div>", unsafe_allow_html=True)
chave_api = 'chave_aqui'


def arruma_data(lista):

    dia = lista[8:]
    mes = lista[5:7]
    ano = lista[0:4]
    data = f'{dia}/{mes}/{ano}'
    return f'Data de lançamento : {data}'
def limpar_tela():
    st.session_state['lista_de_midia'] = []
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
    
        CREATE TABLE IF NOT EXISTS midia (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(100) NOT NULL,
            imagem VARCHAR(100),
            status VARCHAR(20),
            tipo VARCHAR(20),
            nota VARCHAR(20),
            id_tmdb INT
        )
    
        """
    cursor.execute(comando_criar_tabela)

    comando_ler = 'SELECT * FROM midia'
    cursor.execute(comando_ler)
    midia_encontrada = cursor.fetchall()
    tabela = pd.DataFrame(midia_encontrada, columns=["id", "titulo", "imagem", "status", "tipo",'nota','id_tmdb'])

    
    pesquisar,filmes, series, animes = st.tabs(['Área de Pesquisa', 'Área de Filmes', 'Área de Séries', 'Área de Animes'])
    with pesquisar:
        if 'lista_de_midia' not in st.session_state:
            st.session_state['lista_de_midia'] = []
        opcoes = ['Filmes', 'Séries', 'Animes']
        selecao = st.segmented_control( "", opcoes, selection_mode='single',default='Filmes', help='Escolha o tipo de midia que deseja pesquisar',key='check_box',required=True, on_change=limpar_tela)
        midia_nome = st.text_input(f'Procure por {selecao}')
        
      
            
        pesquisa = st.button('Pesquisar',key='b_pesquisar')
        st.divider()
            

        if pesquisa:
            
            if midia_nome.strip() != '':
                if selecao == 'Filmes' :
                    url_api = f'https://api.themoviedb.org/3/search/movie?query={midia_nome}&language=pt-BR&api_key={chave_api}'
                else:
                    url_api = f'https://api.themoviedb.org/3/search/tv?query={midia_nome}&language=pt-BR&api_key={chave_api}'
                
                resposta = requests.get(url_api)
                dados_midia = resposta.json()
                st.session_state['lista_de_midia'] = dados_midia['results']

        for item in st.session_state['lista_de_midia']:    
                    imagem, informacoes = st.columns([1,2])
                    with imagem:
                        if item['poster_path']:
                            imagem = 'https://image.tmdb.org/t/p/w500' + item['poster_path']
                            st.image(imagem)
                        else:
                            imagem_url = 'https://placehold.co/500x750/2e303e/FFFFFF?text=Sem+Capa'
                            st.image(imagem_url)
                    st.divider()                
                    with informacoes:
                        if selecao == 'Filmes':
                            
                            st.subheader(item['title'])
                            filme_visto, filme_watchlist = st.columns(2)
                            with filme_visto:
                                midia_ja_existe = item['id'] in tabela['id_tmdb'].values
                                filme_v = st.button('Filme Já Assistido' if not midia_ja_existe else 'Já adicionado!', key=f'b_adicionar_{item['id'] * 2}', help='Adicionar a filmes já assistidos', width='stretch',disabled=midia_ja_existe)
                                if filme_v:# Adicionar a filmes vistos         
                                    if item['poster_path']:          
                                        comando_inserir = "INSERT INTO midia (titulo, imagem, status, tipo,nota,id_tmdb) VALUES (%s, %s, %s, %s, %s, %s)"
                                        valores = (item['title'] ,imagem ,'assistido','filme','👍',item['id'])
                                        cursor.execute(comando_inserir, valores)
                                        conexao.commit()
                                        st.badge('Filme adicionado a "Assistidos"', color='green')
                                    else:
                                        comando_inserir = "INSERT INTO midia (titulo, imagem, status, tipo,nota,id_tmdb) VALUES (%s, %s, %s, %s, %s, %s)"
                                        valores = (item['title'] ,imagem_url ,'assistido','filme','👍',item['id'])
                                        cursor.execute(comando_inserir, valores)
                                        conexao.commit()
                                        st.badge('Filme adicionado a "Assistidos"', color='green')
                                    

                            with filme_watchlist:
                                midia_ja_existe = item['id'] in tabela['id_tmdb'].values                                
                                filme_w = st.button(label='Watchlist de Filme' if not midia_ja_existe else 'Já adicionado!', key=f'b_adicionar_{item['id'] * 3}', help='Adicionar a watchlist de filmes', width='stretch',disabled=midia_ja_existe)
                                if filme_w:# Adicionar a watchlist de filmes   
                                    if item['poster_path']:                     
                                        comando_inserir = "INSERT INTO midia (titulo, imagem, status, tipo,nota,id_tmdb) VALUES (%s, %s, %s, %s, %s, %s)"
                                        valores = (item['title'], imagem, 'watchlist', 'filme','👍',item['id'])
                                        cursor.execute(comando_inserir, valores)
                                        conexao.commit()
                                        st.badge('Filme adicionado a "Watchlist"', color='blue')
                                    else:
                                        comando_inserir = "INSERT INTO midia (titulo, imagem, status, tipo,nota,id_tmdb) VALUES (%s, %s, %s, %s, %s, %s)"
                                        valores = (item['title'] ,imagem_url ,'watchlist','filme','👍',item['id'])
                                        cursor.execute(comando_inserir, valores)
                                        conexao.commit()
                                        st.badge('Filme adicionado a "Watchlist"', color='blue')

                            if len(item['overview']) > 349:
                                item['overview'] = item['overview'].replace(item['overview'][346:], '...')
                                st.caption(item['overview'][0:349])

                            else:
                                st.caption(item['overview'])
                            st.caption(f'Lingua original: {item['original_language']}')
                            st.caption(f'Nome original: {item['original_title']}')
                            st.caption(arruma_data(item['release_date']))

                        elif selecao == 'Séries':

                            st.subheader(item['name'])
                            serie_visto, serie_watchlist = st.columns(2)
                            with serie_visto:
                                midia_ja_existe = item['id'] in tabela['id_tmdb'].values 
                                serie_v = st.button(label='Série Já Assistida' if not midia_ja_existe else 'Já adicionado!', key=f'b_adicionar_{item['id'] * 4}', help='Adicionar a séries já assistidas', width='stretch',disabled=midia_ja_existe)
                                if serie_v:# Adicionar a serie vistas
                                    if item['poster_path']:                  
                                        comando_inserir = "INSERT INTO midia (titulo, imagem, status, tipo,nota,id_tmdb) VALUES (%s, %s, %s, %s, %s, %s)"
                                        valores = (item['name'], imagem,'assistido','serie','👍',item['id'])
                                        cursor.execute(comando_inserir, valores)
                                        conexao.commit()
                                        st.badge('Série adicionada a "Assistidos"', color='green')
                                    else:
                                        comando_inserir = "INSERT INTO midia (titulo, imagem, status, tipo,nota,id_tmdb) VALUES (%s, %s, %s, %s, %s, %s)"
                                        valores = (item['name'], imagem_url,'assistido','serie','👍',item['id'])
                                        cursor.execute(comando_inserir, valores)
                                        conexao.commit()
                                        st.badge('Série adicionada a "Assistidos"', color='green')


                            with serie_watchlist:
                                midia_ja_existe = item['id'] in tabela['id_tmdb'].values 
                                serie_w = st.button(label='Watchlist de Série' if not midia_ja_existe else 'Já adicionado!', key=f'b_adicionar_{item['id'] * 5}', help='Adicionar a watchlist de séries', width='stretch',disabled=midia_ja_existe) 
                                if serie_w:# Adicionar a watchlist de series   
                                    if item['poster_path']:                
                                        comando_inserir = "INSERT INTO midia (titulo, imagem, status, tipo,nota,id_tmdb) VALUES (%s, %s, %s, %s, %s, %s)"
                                        valores = (item['name'], imagem, 'watchlist','serie','👍',item['id'])
                                        cursor.execute(comando_inserir, valores)
                                        conexao.commit()
                                        st.badge('Série adicionada a "Watchlist"', color='blue')
                                    else:
                                        comando_inserir = "INSERT INTO midia (titulo, imagem, status, tipo,nota,id_tmdb) VALUES (%s, %s, %s, %s, %s, %s)"
                                        valores = (item['name'], imagem_url, 'watchlist','serie','👍',item['id'])
                                        cursor.execute(comando_inserir, valores)
                                        conexao.commit()
                                        st.badge('Série adicionada a "Watchlist"', color='blue')


                            if len(item['overview']) > 349:
                                item['overview'] = item['overview'].replace(item['overview'][346:], '...')
                                st.caption(item['overview'][0:349])

                            else:
                                st.caption(item['overview'])
                            st.caption(f'Lingua original: {item['original_language']}')
                            st.caption(f'Nome original: {item['original_name']}')
                            st.caption(arruma_data(item['first_air_date']))                       
                        else:

                            st.subheader(item['name'])
                            anime_visto, anime_watchlist = st.columns(2)
                            with anime_visto:
                                midia_ja_existe = item['id'] in tabela['id_tmdb'].values 
                                anime_v = st.button(label='Anime Já Assistido' if not midia_ja_existe else 'Já adicionado!', key=f'b_adicionar_{item['id'] * 6}', help='Adicionar a animes já assistidos', width='stretch',disabled=midia_ja_existe) 
                                if anime_v:# Adicionar a animes vistos           
                                    if item['poster_path']:        
                                        comando_inserir = "INSERT INTO midia (titulo, imagem, status, tipo,nota,id_tmdb) VALUES (%s, %s, %s, %s, %s, %s)"
                                        valores = (item['name'], imagem, 'assistido','anime','👍',item['id'])
                                        cursor.execute(comando_inserir, valores)
                                        conexao.commit()
                                        st.badge('Anime adicionado a "Assistidos"', color='green')
                                    else:
                                        comando_inserir = "INSERT INTO midia (titulo, imagem, status, tipo,nota,id_tmdb) VALUES (%s, %s, %s, %s, %s, %s)"
                                        valores = (item['name'], imagem_url, 'assistido','anime','👍',item['id'])
                                        cursor.execute(comando_inserir, valores)
                                        conexao.commit()
                                        st.badge('Anime adicionado a "Assistidos"', color='green')

                           
                            with anime_watchlist:
                                midia_ja_existe = item['id'] in tabela['id_tmdb'].values 
                                anime_w = st.button(label='Watchlist de Anime' if not midia_ja_existe else 'Já adicionado!', key=f'b_adicionar_{item['id'] * 7}', help='Adicionar a watchlist de animes', width='stretch',disabled=midia_ja_existe)                                
                                if anime_w:# Adicionar a watchlist de animes      
                                    if item['poster_path']:              
                                        comando_inserir = "INSERT INTO midia (titulo, imagem, status, tipo,nota,id_tmdb) VALUES (%s, %s, %s, %s, %s, %s)"
                                        valores = (item['name'], imagem, 'watchlist','anime','👍',item['id'])
                                        cursor.execute(comando_inserir, valores)
                                        conexao.commit()
                                        st.badge('Anime adicionado a "Watchlist"', color='blue')
                                    else:
                                        comando_inserir = "INSERT INTO midia (titulo, imagem, status, tipo,nota,id_tmdb) VALUES (%s, %s, %s, %s, %s, %s)"
                                        valores = (item['name'], imagem_url, 'watchlist','anime','👍',item['id'])
                                        cursor.execute(comando_inserir, valores)
                                        conexao.commit()
                                        st.badge('Anime adicionado a "Watchlist"', color='blue')


                            if len(item['overview']) > 349:
                                item['overview'] = item['overview'].replace(item['overview'][346:], '...')
                                st.caption(item['overview'][0:349])
                            else:
                                st.caption(item['overview'])
                            st.caption(f'Lingua original: {item['original_language']}')
                            st.caption(f'Nome original: {item['original_name']}')
                            st.caption(arruma_data(item['first_air_date']))
    #Chamar o banco de dados


    with filmes:
            st.title('Filmes🎞️')
            filmes_assistidos, filmes_watchlist = st.tabs(['Assistidos', 'Watchlist'])
            with filmes_assistidos:
                quantidade_colunas = 4
                colunas = st.columns(quantidade_colunas)
                contador = 0
                for index, linha in tabela.iterrows():           
                    if linha["status"] == "assistido" and linha["tipo"] == "filme":                                                                                                     
                        coluna_atual = colunas[contador % quantidade_colunas]
                        with coluna_atual:
   
                            with st.popover(f"{linha['titulo'][:19]}", use_container_width=True):
                                st.write(f"**{linha['titulo']}**")
                                avalicao = st.pills('Gostou ?', ['👍','👎'],key=f'texto_{linha['id']}',selection_mode='single',required=True,default=linha['nota']) 
                                if avalicao:
                                    comando_atualizar =  """
                                                        UPDATE midia
                                                        SET nota = %s
                                                        WHERE id = %s
                                                        """

                                    nota_att = (avalicao, linha['id'])
                                    cursor.execute(comando_atualizar, nota_att)
                                    conexao.commit()
                                       
                                if st.button("Excluir", key=f"del_{linha['id']}", help='Excluir filme da lista'):
                                    comando_apagar = "DELETE FROM midia WHERE id = %s"
                                    valores = (linha['id'],)
                                    cursor.execute(comando_apagar, valores)
                                    conexao.commit()
                                    st.rerun()
                                 
                            st.image(linha['imagem'], use_container_width=True)

                        contador += 1

            
            with filmes_watchlist:
                quantidade_colunas = 4
                colunas = st.columns(quantidade_colunas)
                contador = 0
                for index, linha in tabela.iterrows():           
                    if linha["status"] == "watchlist" and linha["tipo"] == "filme":
                        coluna_atual = colunas[contador % quantidade_colunas]
                        with coluna_atual:
   
                            with st.popover(f"{linha['titulo'][:19]}", use_container_width=True):
                                st.write(f"**{linha['titulo']}**")
                                if st.button("Assistido", key=f"atulizar_{linha['id']}", help='Mover para assistidos'):
                                    comando_atualizar =  """
                                                    UPDATE midia
                                                    SET status = %s
                                                    WHERE id = %s
                                                    """

                                    valores_att = ('assistido', linha['id'])
                                    cursor.execute(comando_atualizar, valores_att)
                                    conexao.commit()
                                    st.rerun()                                
                                if st.button("Excluir", key=f"del_{linha['id']}", help='Excluir filme da lista'):
                                    comando_apagar = "DELETE FROM midia WHERE id = %s"
                                    valores = (linha['id'],)
                                    cursor.execute(comando_apagar, valores)
                                    conexao.commit()
                                    st.rerun()       


                            st.image(linha['imagem'])

                        contador += 1





    with series:
        st.title('Series📺')
        series_assistidas, series_watchlist = st.tabs(['Assistidos', 'Watchlist'])
        with series_assistidas:
                quantidade_colunas = 4
                colunas = st.columns(quantidade_colunas)
                contador = 0
                for index, linha in tabela.iterrows():           
                    if linha["status"] == "assistido" and linha["tipo"] == "serie":
                        coluna_atual = colunas[contador % quantidade_colunas]
                        with coluna_atual:
   
                            with st.popover(f"{linha['titulo'][:19]}", use_container_width=True):
                                st.write(f"**{linha['titulo']}**")
                                avalicao = st.pills('Gostou ?', ['👍','👎'],key=f'texto_{linha['id']}',selection_mode='single',required=True,default=linha['nota']) 
                                if avalicao:
                                    comando_atualizar =  """
                                                        UPDATE midia
                                                        SET nota = %s
                                                        WHERE id = %s
                                                        """

                                    nota_att = (avalicao, linha['id'])
                                    cursor.execute(comando_atualizar, nota_att)
                                    conexao.commit()   
           
                                if st.button("Excluir", key=f"del_{linha['id']}", help='Excluir série da lista'):
                                    comando_apagar = "DELETE FROM midia WHERE id = %s"
                                    valores = (linha['id'],)
                                    cursor.execute(comando_apagar, valores)
                                    conexao.commit()
                                    st.rerun()                                   
                                 
                            st.image(linha['imagem'], use_container_width=True)

                        contador += 1

        
        with series_watchlist:
                quantidade_colunas = 4
                colunas = st.columns(quantidade_colunas)
                contador = 0
                for index, linha in tabela.iterrows():           
                    if linha["status"] == "watchlist" and linha["tipo"] == "serie":
                        coluna_atual = colunas[contador % quantidade_colunas]
                        with coluna_atual:
                            with st.popover(f"{linha['titulo'][:19]}", use_container_width=True):
                                st.write(f"**{linha['titulo']}**")
                                if st.button("Assistido", key=f"atulizar_{linha['id']}", help='Mover para assistidos'):
                                    comando_atualizar =  """
                                                    UPDATE midia
                                                    SET status = %s
                                                    WHERE id = %s
                                                    """

                                    valores_att = ('assistido', linha['id'])
                                    cursor.execute(comando_atualizar, valores_att)
                                    conexao.commit()
                                    st.rerun()                                
                                if st.button("Excluir", key=f"del_{linha['id']}", help='Excluir série da lista'):
                                    comando_apagar = "DELETE FROM midia WHERE id = %s"
                                    valores = (linha['id'],)
                                    cursor.execute(comando_apagar, valores)
                                    conexao.commit()
                                    st.rerun()       
                                   
                            st.image(linha['imagem'], use_container_width=True)


                        contador += 1

    with animes:
        st.title('Animes💢')
        animes_assistidos, animes_watchlist = st.tabs(['Assistidos', 'Watchlist'])
        with animes_assistidos:
                quantidade_colunas = 4
                colunas = st.columns(quantidade_colunas)
                contador = 0
                for index, linha in tabela.iterrows():           
                    if linha["status"] == "assistido" and linha["tipo"] == "anime":
                        coluna_atual = colunas[contador % quantidade_colunas]
                        with coluna_atual:
   
                            with st.popover(f"{linha['titulo'][:19]}", use_container_width=True):
                                st.write(f"**{linha['titulo']}**")
                                avalicao = st.pills('Gostou ?', ['👍','👎'],key=f'texto_{linha['id']}',selection_mode='single',required=True,default=linha['nota']) 
                                if avalicao:
                                    comando_atualizar =  """
                                                        UPDATE midia
                                                        SET nota = %s
                                                        WHERE id = %s
                                                        """

                                    nota_att = (avalicao, linha['id'])
                                    cursor.execute(comando_atualizar, nota_att)
                                    conexao.commit()   
           
                                if st.button("Excluir", key=f"del_{linha['id']}", help='Excluir anime da lista'):
                                    comando_apagar = "DELETE FROM midia WHERE id = %s"
                                    valores = (linha['id'],)
                                    cursor.execute(comando_apagar, valores)
                                    conexao.commit()
                                    st.rerun()                                   
                                 
                            st.image(linha['imagem'], use_container_width=True)


                        contador += 1

        
        with animes_watchlist:
                quantidade_colunas = 4
                colunas = st.columns(quantidade_colunas)
                contador = 0
                for index, linha in tabela.iterrows():           
                    if linha["status"] == "watchlist" and linha["tipo"] == "anime":
                        coluna_atual = colunas[contador % quantidade_colunas]
                        with coluna_atual:
                            with st.popover(f"{linha['titulo'][:19]}", use_container_width=True):
                                st.write(f"**{linha['titulo']}**")
                                if st.button("Assistido", key=f"atulizar_{linha['id']}", help='Mover para assistidos'):
                                    comando_atualizar =  """
                                                    UPDATE midia
                                                    SET status = %s
                                                    WHERE id = %s
                                                    """

                                    valores_att = ('assistido', linha['id'])
                                    cursor.execute(comando_atualizar, valores_att)
                                    conexao.commit()
                                    st.rerun()                                
                                if st.button("Excluir", key=f"del_{linha['id']}", help='Excluir anime da lista'):
                                    comando_apagar = "DELETE FROM midia WHERE id = %s"
                                    valores = (linha['id'],)
                                    cursor.execute(comando_apagar, valores)
                                    conexao.commit()
                                    st.rerun()       

                                 
                            st.image(linha['imagem'], use_container_width=True)

                        contador += 1





        
except mysql.connector.Error as erro:

    st.error(f"Erro no banco de dados: {erro}")

    st.stop()
botao_flutuante = """
    <a href="#topo" style="
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #2e303e; /* Cor do fundo de botões do Streamlit */
        color: white;
        padding: 10px 15px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        z-index: 9999;
    ">⬆️ Voltar pra cima</a>
"""
st.markdown(botao_flutuante, unsafe_allow_html=True)