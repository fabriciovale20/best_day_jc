import os
from datetime import datetime
import unicodedata
import mysql.connector
from flask import Flask, render_template, request

conexao = mysql.connector.connect(
    host='us-cdbr-east-06.cleardb.net',
    user='b051c39ae5d253',
    password='ba97c9af',
    database='heroku_4560c69d2cc9573',
)
app = Flask(__name__)

cursor = conexao.cursor()

lista_brincadeiras_suor = {}
lista_brincadeiras_leve = {}
lista_brincadeiras_sentado = {}
lista_brincadeiras_dormir = {}

lista_brincadeiras = {}

dir_suor = './static/brincadeiras/suor'
dir_leve = './static/brincadeiras/leve'
dir_sentado = './static/brincadeiras/sentado'
dir_dormir = './static/brincadeiras/dormir'

id = 0

for imagem in os.listdir(dir_suor):
    if os.path.isfile(os.path.join(dir_suor, imagem)):
        nome = imagem[:imagem.find('.'):]
        lista_brincadeiras_suor[id] = [imagem, nome]
        lista_brincadeiras[id] = [imagem, nome]
        id += 1


for imagem in os.listdir(dir_leve):
    if os.path.isfile(os.path.join(dir_leve, imagem)):
        nome = imagem[:imagem.find('.'):]
        lista_brincadeiras_leve[id] = [imagem, nome]
        lista_brincadeiras[id] = [imagem, nome]
        id += 1
    
for imagem in os.listdir(dir_sentado):
    if os.path.isfile(os.path.join(dir_sentado, imagem)):
        nome = imagem[:imagem.find('.'):]
        lista_brincadeiras_sentado[id] = [imagem, nome]
        lista_brincadeiras[id] = [imagem, nome]
        id += 1

for imagem in os.listdir(dir_dormir):
    if os.path.isfile(os.path.join(dir_dormir, imagem)):
        nome = imagem[:imagem.find('.'):]
        lista_brincadeiras_dormir[id] = [imagem, nome]
        lista_brincadeiras[id] = [imagem, nome]
        id += 1

@app.route('/', methods=['GET', 'POST'])
def home():
    global usuario, senha, nome_aluno

    conexao.cursor()
    
    # Coletando usuário e senha preenchidos no formulário
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    print(usuario)
    print(senha)

    # Coletando lista dos usuários cadastrados no Banco de Dados para realizar validação
    comando = f'SELECT * FROM usuarios'
    cursor.execute(comando)
    lista_dados = cursor.fetchall()

    # Validação do Usuário e Senha inseridos na page Home
    if usuario != None and senha != None:
        for user in lista_dados:
            if user[5] == usuario and user[6] == senha: # Acesso adiministrador
                if usuario == 'jcadmin' and senha == '123':
                    return render_template('pageadmin.html')
                else: # Caso o login for válido, será redirecionado para a próxima página
                    nome_aluno=user[1]
                    nome_aluno = nome_aluno[:nome_aluno.find(' '):] # Para pegar apenas o primeiro nome do aluno
                    
                    return render_template('pagemanha.html', 
                    nome_aluno=nome_aluno, 
                    lista_brincadeiras_suor=lista_brincadeiras_suor, 
                    lista_brincadeiras_leve=lista_brincadeiras_leve, 
                    lista_brincadeiras_sentado=lista_brincadeiras_sentado,
                    lista_brincadeiras=lista_brincadeiras
                    )
        else: # Caso o Usuário e Senha não possuam no Banco de Dados é retornado a mensagem de Login inválido
            incorreto = True
            msg = 'Login inválido, tente novamente!'
            return render_template('home.html', incorreto=incorreto, msg=msg)

    # Acessando a página pela primeira vez
    return render_template('home.html')

@app.route('/admin')
def administratador():
    return render_template('pageadm.html')

@app.route('/listagem', methods=['GET', 'POST'])
def listagem():
    lista_escolas = []

    comando = f'SELECT * FROM usuarios'
    cursor.execute(comando)
    lista_dados = cursor.fetchall()
    
    for escola in lista_dados:
        if escola[3] != None and escola[3] not in lista_escolas:
            lista_escolas.append(escola[3])

    print(lista_escolas)
    return render_template('pageadmin.html', lista_dados=lista_dados, lista_escolas=lista_escolas)


@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    nome_completo = request.form.get('nome_completo')
    data_nascimento = request.form.get('data_nascimento')
    escola = request.form.get('escola')
    print(nome_completo)
    print(data_nascimento)
    print(escola)

    # Caso o preenchimento do cadastro do aluno possua algum dado em branco
    if nome_completo == '' or data_nascimento == '' or escola == '':
        erro_preenchimento = True
        msg = '*Preencha todos os campos*'
        print(msg)
        return render_template('pageadmin.html', erro_preenchimento=erro_preenchimento ,msg=msg)

    # Validando data de nascimento
    format = "%d/%m/%Y"
    res = True
    
    # Usando try-except para testar o valor da data (True ou False)
    try:
        res = bool(datetime.strptime(data_nascimento, format))
    except ValueError:
        res = False

    # Caso a data seja verdadeira, prossegue com a validação
    if res:
        dia, mes, ano = map(str, data_nascimento.split('/')) # Separando a data de nascimneto em dia, mês e ano
        
        # Formatando o nome do aluno, retirando acentos
        nome_formatado = unicodedata.normalize('NFD', nome_completo) 
        nome_formatado = nome_formatado.encode('ascii', 'ignore').decode('utf8').casefold()
        nome = nome_formatado.lower().split()
        primeiro_nome = nome[0]
        ultimo_nome = nome[len(nome)-1]

        # Criação do Usuário e senha automático
        usuario = primeiro_nome + ultimo_nome + dia + mes
        senha = 'jc' + dia + mes
        print(f'Usuário: {usuario}')
        print(f'Senha: {senha}')

        comando = f'INSERT INTO usuarios (nome_completo, data_nascimento, escola, usuario, senha) VALUES ("{nome_completo}", "{data_nascimento}", "{escola}", "{usuario}", "{senha}");'
        cursor.execute(comando)
        conexao.commit()

    return render_template('pageadmin.html')


# Listas para salvar os Checkbox selecionados, para caso retorne para a página anterior, ficar salvo
brincadeiras_selecionadas_manha = []
brincadeiras_selecionadas_tarde = []
brincadeiras_selecionadas_noite = []
brincadeiras_selecionadas_dormir = []

@app.route('/manha', methods=['GET', 'POST'])
def manha():
    global brincadeiras_selecionadas_manha

    itens_selecionados = [] # Lista na qual ficará salvo os Checkbox selecionados cada vez que acessar a página

    cont = 0
    print(brincadeiras_selecionadas_manha)
    
    # Verificando imagens selecionadas conforme o número de brincadeiras cadastradas
    for c in range(len(lista_brincadeiras)+1):
        a = request.form.get(f'{c}') # Percorrendo todos Checkbox
        print(a)

        if a is not None and a not in itens_selecionados: # Caso o Checkbox tenha sido selecionado é adicionado a lista
            cont += 1
            itens_selecionados.append(a)

    if len(itens_selecionados) > 0: # Atualizar a Lista de Brincadeiras selecionadas com apenas os Checkbox selecionados atualmente
            brincadeiras_selecionadas_manha = itens_selecionados[:]
    
    print(itens_selecionados)
    print(f'{usuario} escolheu {cont} brincadeiras.')  
    print(brincadeiras_selecionadas_manha)

    # Validando se o usuário selecionou a quantidade necessária para prosseguir
    if cont == 5:
        registrar_manha_tarde(
            'm1', brincadeiras_selecionadas_manha[0],
            'm2', brincadeiras_selecionadas_manha[1],
            'm3', brincadeiras_selecionadas_manha[2],
            'm4', brincadeiras_selecionadas_manha[3],
            'm5', brincadeiras_selecionadas_manha[4]
            ) # Registrando as brincadeiras selecionadas ao Banco de Dados
        return render_template('pagetarde.html', 
        nome_aluno=nome_aluno, 
        lista_brincadeiras_suor=lista_brincadeiras_suor, 
        lista_brincadeiras_leve=lista_brincadeiras_leve, 
        lista_brincadeiras_sentado=lista_brincadeiras_sentado
        )
    elif len(brincadeiras_selecionadas_manha) == 0:
        return render_template('pagemanha.html', 
        nome_aluno=nome_aluno, 
        lista_brincadeiras_suor=lista_brincadeiras_suor, 
        lista_brincadeiras_leve=lista_brincadeiras_leve, 
        lista_brincadeiras_sentado=lista_brincadeiras_sentado
        )
    else:
        return render_template('pagemanha.html', 
        nome_aluno=nome_aluno, 
        lista_brincadeiras_suor=lista_brincadeiras_suor, 
        lista_brincadeiras_leve=lista_brincadeiras_leve, 
        lista_brincadeiras_sentado=lista_brincadeiras_sentado,
        lista_brincadeiras=lista_brincadeiras,
        brincadeiras_selecionadas_manha=brincadeiras_selecionadas_manha
        )


@app.route('/tarde', methods=['GET', 'POST'])
def tarde():
    global brincadeiras_selecionadas_tarde

    itens_selecionados = [] # Lista na qual ficará salvo os Checkbox selecionados cada vez que acessar a página

    cont = 0
    print(brincadeiras_selecionadas_tarde)
    
    # Verificando imagens selecionadas conforme o número de brincadeiras cadastradas
    for c in range(len(lista_brincadeiras)+1):
        a = request.form.get(f'{c}') # Percorrendo todos Checkbox
        print(a)

        if a is not None and a not in itens_selecionados: # Caso o Checkbox tenha sido selecionado é adicionado a lista
            cont += 1
            itens_selecionados.append(a)

    if len(itens_selecionados) > 0: # Atualizar a Lista de Brincadeiras selecionadas com apenas os Checkbox selecionados atualmente
            brincadeiras_selecionadas_tarde = itens_selecionados[:]
    
    print(itens_selecionados)
    print(f'{usuario} escolheu {cont} brincadeiras.')  
    print(brincadeiras_selecionadas_tarde)

    # Validando se o usuário selecionou a quantidade necessária para prosseguir
    if cont == 5:
        registrar_manha_tarde(
            't1', brincadeiras_selecionadas_tarde[0],
            't2', brincadeiras_selecionadas_tarde[1],
            't3', brincadeiras_selecionadas_tarde[2],
            't4', brincadeiras_selecionadas_tarde[3],
            't5', brincadeiras_selecionadas_tarde[4]
            ) # Registrando as brincadeiras selecionadas ao Banco de Dados
        return render_template('pagenoite.html', 
        nome_aluno=nome_aluno, 
        lista_brincadeiras_suor=lista_brincadeiras_suor, 
        lista_brincadeiras_leve=lista_brincadeiras_leve, 
        lista_brincadeiras_sentado=lista_brincadeiras_sentado
        )
    elif len(brincadeiras_selecionadas_tarde) == 0:
        return render_template('pagetarde.html', 
        nome_aluno=nome_aluno, 
        lista_brincadeiras_suor=lista_brincadeiras_suor, 
        lista_brincadeiras_leve=lista_brincadeiras_leve, 
        lista_brincadeiras_sentado=lista_brincadeiras_sentado
        )
    else:
        return render_template('pagetarde.html', 
        nome_aluno=nome_aluno, 
        lista_brincadeiras_suor=lista_brincadeiras_suor, 
        lista_brincadeiras_leve=lista_brincadeiras_leve, 
        lista_brincadeiras_sentado=lista_brincadeiras_sentado,
        lista_brincadeiras=lista_brincadeiras,
        brincadeiras_selecionadas_tarde=brincadeiras_selecionadas_tarde
        )

@app.route('/noite', methods=['GET', 'POST'])
def noite():
    global brincadeiras_selecionadas_noite

    itens_selecionados = [] # Lista na qual ficará salvo os Checkbox selecionados cada vez que acessar a página

    cont = 0
    print(brincadeiras_selecionadas_noite)
    
    # Verificando imagens selecionadas conforme o número de brincadeiras cadastradas
    for c in range(len(lista_brincadeiras)+1):
        a = request.form.get(f'{c}') # Percorrendo todos Checkbox
        print(a)

        if a is not None and a not in itens_selecionados: # Caso o Checkbox tenha sido selecionado é adicionado a lista
            cont += 1
            itens_selecionados.append(a)

    if len(itens_selecionados) > 0: # Atualizar a Lista de Brincadeiras selecionadas com apenas os Checkbox selecionados atualmente
            brincadeiras_selecionadas_noite = itens_selecionados[:]
    
    print(itens_selecionados)
    print(f'{usuario} escolheu {cont} brincadeiras.')  
    print(brincadeiras_selecionadas_noite)

    # Validando se o usuário selecionou a quantidade necessária para prosseguir
    if cont == 4:
        registrar_noite(
            'n1', brincadeiras_selecionadas_noite[0],
            'n2', brincadeiras_selecionadas_noite[1],
            'n3', brincadeiras_selecionadas_noite[2],
            'n4', brincadeiras_selecionadas_noite[3]
            ) # Registrando as brincadeiras selecionadas ao Banco de Dados
        return render_template('pagedormir.html', 
        nome_aluno=nome_aluno, 
        lista_brincadeiras_dormir=lista_brincadeiras_dormir
        )
    elif len(brincadeiras_selecionadas_noite) == 0:
        return render_template('pagenoite.html', 
        nome_aluno=nome_aluno, 
        lista_brincadeiras_suor=lista_brincadeiras_suor, 
        lista_brincadeiras_leve=lista_brincadeiras_leve, 
        lista_brincadeiras_sentado=lista_brincadeiras_sentado
        )
    else:
        return render_template('pagenoite.html', 
        nome_aluno=nome_aluno, 
        lista_brincadeiras_suor=lista_brincadeiras_suor, 
        lista_brincadeiras_leve=lista_brincadeiras_leve, 
        lista_brincadeiras_sentado=lista_brincadeiras_sentado,
        lista_brincadeiras=lista_brincadeiras,
        brincadeiras_selecionadas_noite=brincadeiras_selecionadas_noite
        )

@app.route('/dormir', methods=['GET', 'POST'])
def dormir():
    global brincadeiras_selecionadas_dormir

    itens_selecionados = [] # Lista na qual ficará salvo os Checkbox selecionados cada vez que acessar a página

    cont = 0
    print(brincadeiras_selecionadas_dormir)
    
    # Verificando imagens selecionadas conforme o número de brincadeiras cadastradas
    for c in range(len(lista_brincadeiras)+1):
        a = request.form.get(f'{c}') # Percorrendo todos Checkbox
        print(a)

        if a is not None and a not in itens_selecionados: # Caso o Checkbox tenha sido selecionado é adicionado a lista
            cont += 1
            itens_selecionados.append(a)

    if len(itens_selecionados) > 0: # Atualizar a Lista de Brincadeiras selecionadas com apenas os Checkbox selecionados atualmente
            brincadeiras_selecionadas_dormir = itens_selecionados[:]
    
    print(itens_selecionados)
    print(f'{usuario} escolheu {cont} brincadeiras.')  
    print(brincadeiras_selecionadas_dormir)

    # Validando se o usuário selecionou a quantidade necessária para prosseguir
    if cont == 1:
        registrar_dormir(
            'd1', brincadeiras_selecionadas_dormir[0]
            ) # Registrando as brincadeiras selecionadas ao Banco de Dados
        return render_template('pagefinal.html', 
        nome_aluno=nome_aluno, 
        lista_brincadeiras_dormir=lista_brincadeiras_dormir
        )
    elif len(brincadeiras_selecionadas_dormir) == 0:
        return render_template('pagedormir.html', 
        nome_aluno=nome_aluno, 
        lista_brincadeiras_dormir=lista_brincadeiras_dormir
        )
    else:
        return render_template('pagedormir.html', 
        nome_aluno=nome_aluno, 
        lista_brincadeiras_dormir=lista_brincadeiras_dormir,
        lista_brincadeiras=lista_brincadeiras,
        brincadeiras_selecionadas_dormir=brincadeiras_selecionadas_dormir
        )


@app.route('/final', methods=['GET', 'POST'])
def final():
    print(datetime.today())

    comando = f'UPDATE usuarios SET hora_avaliacao = "{datetime.today()}" WHERE usuario = "{usuario}"'
    cursor.execute(comando) # Executa o comando acima de UPDATE
    conexao.commit()

    return render_template('home.html')

# Função para registrar as atividades no Banco de Dados (Página Manhã e Tarde, que tem 5 atividades selecionadas)
def registrar_manha_tarde(a, a1, b, b1, c, c1, d, d1, e, e1):
    comando = f'UPDATE usuarios SET {a} = "{a1}", {b} = "{b1}", {c} = "{c1}", {d} = "{d1}", {e} = "{e1}" WHERE usuario = "{usuario}"'
    cursor.execute(comando) # Executa o comando acima de UPDATE
    conexao.commit()

# Função para registrar as atividades no Banco de Dados (Página Noite que tem 4 atividades selecionadas)
def registrar_noite(a, a1, b, b1, c, c1, d, d1):
    comando = f'UPDATE usuarios SET {a} = "{a1}", {b} = "{b1}", {c} = "{c1}", {d} = "{d1}" WHERE usuario = "{usuario}"'
    cursor.execute(comando) # Executa o comando acima de UPDATE
    conexao.commit()

# Função para registrar as atividades no Banco de Dados (Página Dormir que tem apenas 1 atividade selecionada)
def registrar_dormir(a, a1):
    comando = f'UPDATE usuarios SET {a} = "{a1}" WHERE usuario = "{usuario}"'
    cursor.execute(comando) # Executa o comando acima de UPDATE
    conexao.commit()

if __name__ == "__main__":
    app.run(debug=True)