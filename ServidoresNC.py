import streamlit as st
from datetime import datetime
import math
import json
import os

# Estrutura para armazenar os servidores
class Servidor:
    def __init__(self, nome, cargo, remuneracao, cidade, escolaridade, especialidade, 
                 taxa_absenteismo, avaliacao, data_inicio=None):
        self.nome = nome.upper()
        self.cargo = cargo.upper()
        self.remuneracao = remuneracao
        self.cidade = cidade.upper()
        self.escolaridade = escolaridade.upper()
        self.especialidade = especialidade.upper()
        self.taxa_absenteismo = taxa_absenteismo
        self.avaliacao = avaliacao
        self.data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d %H:%M:%S.%f") if data_inicio else datetime.now()

    @property
    def tempo_servico(self):
        delta = datetime.now() - self.data_inicio
        return delta.days  # Retorna o tempo de serviço em dias

# Tabela hash para armazenar servidores
servidores_hash = {}

# Função para salvar os servidores em arquivo JSON
def salvar_servidores():
    with open('servidores.json', 'w') as f:
        json.dump({nome: vars(servidor) for nome, servidor in servidores_hash.items()}, f)

# Função para carregar os servidores de um arquivo JSON
def carregar_servidores():
    if os.path.exists('servidores.json'):
        with open('servidores.json', 'r') as f:
            data = json.load(f)
            for nome, servidor_data in data.items():
                servidor_data['data_inicio'] = servidor_data['data_inicio']  # Manter o formato da data
                servidor = Servidor(**servidor_data)
                servidores_hash[nome] = servidor

# Função para adicionar um servidor
def adicionar_servidor_hash(nome, cargo, remuneracao, cidade, escolaridade, especialidade, 
                            taxa_absenteismo, avaliacao):
    if not nome:
        st.error("O nome do servidor é obrigatório.")
        return
    
    nome = nome.upper()
    cargo = cargo.upper()
    cidade = cidade.upper()

    novo_servidor = Servidor(
        nome=nome,
        cargo=cargo,
        remuneracao=remuneracao,
        cidade=cidade,
        escolaridade=escolaridade,
        especialidade=especialidade,
        taxa_absenteismo=taxa_absenteismo,
        avaliacao=avaliacao
    )

    servidores_hash[nome] = novo_servidor
    salvar_servidores()  # Salvar os servidores no arquivo JSON
    st.success(f"{nome} ({cargo}) adicionado com sucesso!")

# Algoritmo Quicksort para ordenar os servidores por nome
def quicksort_nome(lista):
    if len(lista) <= 1:
        return lista
    pivo = lista[0]
    menores = [x for x in lista[1:] if x.nome.lower() <= pivo.nome.lower()]
    maiores = [x for x in lista[1:] if x.nome.lower() > pivo.nome.lower()]
    return quicksort_nome(menores) + [pivo] + quicksort_nome(maiores)

# Mostrar servidores em ordem alfabética
def mostrar_servidores_alfabetica():
    ordenados = quicksort_nome(list(servidores_hash.values()))
    st.write("### Servidores em ordem alfabética:")
    for s in ordenados:
        st.write(s.nome)

# Algoritmo Selection Sort para ordenar os servidores por tempo de serviço
def selection_sort_tempo(lista):
    for i in range(len(lista)):
        max_index = i
        for j in range(i + 1, len(lista)):
            if lista[j].tempo_servico > lista[max_index].tempo_servico:
                max_index = j
        lista[i], lista[max_index] = lista[max_index], lista[i]
    return lista

# Mostrar servidores por tempo de serviço
def mostrar_servidores_tempo_servico():
    ordenados = selection_sort_tempo(list(servidores_hash.values()))
    st.write("### Servidores por tempo de serviço:")
    for s in ordenados:
        st.write(f"{s.nome} - {s.tempo_servico} dias - R${s.remuneracao:.2f}")

# Mostrar remuneração dos servidores
def mostrar_remuneracao():
    st.write("### Remuneração dos servidores:")
    for s in servidores_hash.values():
        st.write(f"{s.nome} - {s.cargo} - R${s.remuneracao:.2f}")

# Função para calcular a distância entre servidores (para KNN)
def calcular_distancia(s1, s2):
    return math.sqrt(
        (s1.taxa_absenteismo - s2.taxa_absenteismo) ** 2 +
        (s1.avaliacao - s2.avaliacao) ** 2 +
        (s1.remuneracao - s2.remuneracao) ** 2
    )

# Implementação do KNN
def knn(k, servidor_alvo):
    distancias = [
        (calcular_distancia(servidor_alvo, servidor), servidor)
        for servidor in servidores_hash.values() if servidor != servidor_alvo
    ]
    distancias.sort(key=lambda x: x[0])
    return [servidor for _, servidor in distancias[:k]]

# Mostrar servidores mais similares usando KNN
def mostrar_servidores_similares(nome, k):
    nome = nome.upper()
    if nome in servidores_hash:
        servidor_alvo = servidores_hash[nome]
        similares = knn(k, servidor_alvo)
        st.write(f"{k} servidores mais próximos de {servidor_alvo.nome}:")
        for s in similares:
            st.write(f"{s.nome} - Avaliação: {s.avaliacao}/100 - Absenteísmo: {s.taxa_absenteismo}% - R${s.remuneracao:.2f}")
    else:
        st.error("Servidor não encontrado.")

# Interface do aplicativo no Streamlit
def interface():
    st.title("Sistema de Gerenciamento de Servidores")

    menu = ["Adicionar servidor", "Mostrar servidores por ordem alfabética", 
            "Mostrar servidores por tempo de serviço", "Mostrar remuneração", 
            "Mostrar servidores mais similares (KNN)"]
    escolha = st.sidebar.selectbox("Menu", menu)

    if escolha == "Adicionar servidor":
        st.subheader("Adicionar novo servidor")
        nome = st.text_input("Nome")
        cargo = st.text_input("Cargo")
        cidade = st.text_input("Cidade")
        escolaridade = st.text_input("Escolaridade")
        especialidade = st.text_input("Especialidade")
        taxa_absenteismo = st.number_input("Taxa de absenteísmo (%)", 0.0, 100.0)
        avaliacao = st.slider("Avaliação de desempenho (0 a 100)", 0, 100)
        remuneracao = st.number_input("Remuneração (R$)", 0.0)

        if st.button("Adicionar"):
            adicionar_servidor_hash(nome, cargo, remuneracao, cidade, escolaridade, 
                                    especialidade, taxa_absenteismo, avaliacao)

    elif escolha == "Mostrar servidores por ordem alfabética":
        mostrar_servidores_alfabetica()

    elif escolha == "Mostrar servidores por tempo de serviço":
        mostrar_servidores_tempo_servico()

    elif escolha == "Mostrar remuneração":
        mostrar_remuneracao()

    elif escolha == "Mostrar servidores mais similares (KNN)":
        nome = st.text_input("Nome do servidor")
        k = st.number_input("Número de servidores similares (K)", min_value=1, value=3)
        if st.button("Mostrar servidores similares"):
            mostrar_servidores_similares(nome, k)

# Carregar servidores salvos e rodar a interface
if __name__ == "__main__":
    carregar_servidores()  # Carregar servidores salvos
    interface()
