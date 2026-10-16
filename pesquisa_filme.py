import streamlit as st
import requests

chave_api = 'Chave_aqui'
st.title('🎬 Catálogo de Filmes')

filme_nome = st.text_input('Digite o nome do filme')
pesquisar = st.button('Pesquisar')

if pesquisar:
    if filme_nome.strip() != '':
        url_api = f'https://api.themoviedb.org/3/search/movie?query={filme_nome}&language=pt-BR&api_key={chave_api}'
        st.divider()
        resposta = requests.get(url_api)
        
        if resposta.status_code == 200:
            dados_filme = resposta.json()
            
            
            for item in dados_filme['results']:
                

                col1, col2 = st.columns([1, 2])
                
                with col1:

                    if item['poster_path']:
                        imagem = 'https://image.tmdb.org/t/p/w500' + item['poster_path']
                        st.image(imagem)
                    else:
                        st.write("🚫 Capa indisponível")
                        
                with col2:
                    st.subheader(item['title'])
                    st.caption(f"Data de lançamento: {item['release_date']}")
                    st.write(item['overview'])
                

                st.divider()
