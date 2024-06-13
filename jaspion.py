import flet as ft
import pandas as pd
import os
from datetime import datetime

def main(page: ft.Page):
    page.title = "Jaspion"

    produtos_vendidos = []
    produtos_temp = []

    # Variáveis de tema
    tema_escuro = True
    page.bgcolor = ft.colors.GREY_900 if tema_escuro else ft.colors.WHITE
    text_color = ft.colors.WHITE if tema_escuro else ft.colors.BLACK
    cor_red = '#DC143C'
    tamanho_texto = 18
    

    def alternar_tema(e):
        nonlocal tema_escuro, text_color
        tema_escuro = not tema_escuro
        page.bgcolor = ft.colors.GREY_900 if tema_escuro else ft.colors.WHITE
        text_color = ft.colors.WHITE if tema_escuro else ft.colors.BLACK
        update_tema()
        page.update()

    def update_tema():
        
        # alternar a cor e o tamanho dos textos dentro das caixas de input
        for field in [nome_produto_venda, valor_produto, quantidade_produto, desconto_produto, valor_pago, nome_produto_pesquisa]:
            field.label_style = ft.TextStyle(color=text_color, size=tamanho_texto)
            field.text_style = ft.TextStyle(color=text_color, size=tamanho_texto)
        
        # alternar a cor e tamanho dos resultados exibidos na tela
        for label in [total_resultado, troco_resultado, troco_detalhado_resultado, pesquisa_resultado, relatorio_text]:
            label.color = text_color
            label.size = tamanho_texto

        for control in lista_de_produtos.controls:
            control.color = text_color
            control.size = tamanho_texto

        
        for container in [adicionar_calcular_container, pesquisar_valor_container, relatorio_container, configuracoes_container, home_container]:
            for control in container.content.controls:
                if isinstance(control, ft.Text):
                    control.color = text_color
                    control.size = tamanho_texto
        for control in adicionar_calcular_container.content.controls[0].controls:
            if isinstance(control, ft.Text):
                control.color = text_color

        for control in adicionar_calcular_container.content.controls[1].controls:
            if isinstance(control, ft.Text):
                control.color = text_color
                
        for control in adicionar_calcular_container.content.controls[2].controls:
            if isinstance(control, ft.Text):
                control.color = text_color

        for control in home_container.content.controls:
            if isinstance(control, ft.Text):
                control.color = text_color
                
        for control in pesquisar_valor_container.content.controls:
            if isinstance(control, ft.Text):
                control.color = text_color       

        for control in relatorio_container.content.controls:
            if isinstance(control, ft.Text):
                control.color = text_color

        for control in configuracoes_container.content.controls:
            if isinstance(control, ft.Text):
                control.color = text_color

    def adicionar_produto(e):
        try:
            nome = nome_produto_venda.value
            valor = float(valor_produto.value.replace(",", "."))
            quantidade = int(quantidade_produto.value)
            total = valor * quantidade
            produtos_temp.append((nome, quantidade, total))
            lista_de_produtos.controls.append(ft.Text(f"{nome} - Qtde: {quantidade}, Total: R$ {total:.2f}", size=18, color=text_color))
            lista_de_produtos.update()
        except ValueError:
            total_resultado.value = "Por favor, insira valores válidos."
            page.update()

    def calcular_total(e):
        try:
            desconto = float(desconto_produto.value.replace(",", ".")) / 100
            total_sem_desconto = sum([total for _, _, total in produtos_temp])
            total_com_desconto = total_sem_desconto * (1 - desconto)
            total_resultado.value = f"Total: R$ {total_com_desconto:.2f}"

            # Adicionando os produtos na lista de produtos vendidos com a data atual
            data_venda = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for nome, quantidade, total in produtos_temp:
                produtos_vendidos.append((data_venda, nome, quantidade, total * (1 - desconto)))
            registro_de_vendas()
            produtos_temp.clear()
            lista_de_produtos.controls.clear()
            lista_de_produtos.update()

            page.update()
        except ValueError:
            total_resultado.value = "Por favor, insira valores válidos."
            page.update()

    def calcular_troco(e):
        try:
            total_text = total_resultado.value.split(':')[1].strip().replace("R$", "").replace(",", ".")
            total = float(total_text)
            pago = float(valor_pago.value.replace(",", "."))
            troco = pago - total
            troco_resultado.value = f"Troco: R$ {troco:.2f}"

            # Calcular a melhor forma de troco
            if troco >= 0:
                troco_detalhado = calcular_melhor_troco(troco)
                troco_detalhado_resultado.value = "Troco detalhado:\n" + "\n".join(troco_detalhado)
            else:
                troco_detalhado_resultado.value = "Valor pago insuficiente."

            page.update()
        except ValueError:
            troco_resultado.value = "Por favor, insira valores válidos."
            page.update()

    def calcular_melhor_troco(troco):
        denominacoes = [
            200.0, 100.0, 50.0, 20.0, 10.0, 5.0, 2.0, 1.0,
            0.50, 0.25, 0.10, 0.05, 0.01
        ]
        resultado = []
        for denominacao in denominacoes:
            quantidade, troco = divmod(troco, denominacao)
            if quantidade > 0:
                resultado.append(f"{int(quantidade)} x R$ {denominacao:.2f}")
        return resultado

    def registro_de_vendas():
        df = pd.DataFrame(produtos_vendidos, columns=["Data", "Nome", "Quantidade", "Total (R$)"])
        file_path = "planilhas/itens_vendidos.xlsx"  # Salva na pasta onde o programa está sendo executado
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Certifica-se que o diretório existe
        if os.path.exists(file_path):
            # Se o arquivo já existe, adiciona os novos dados
            with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
        else:
            # Caso contrário, cria um novo arquivo
            df.to_excel(file_path, index=False)
            
    def ajustar_tamanho_texto(e):
        nonlocal tamanho_texto
        tamanho_texto = e.control.value
        update_tema()
        page.update()       

    def pesquisar_valor(e):
        try:
            item_nome = nome_produto_pesquisa.value.strip()
            df = pd.read_excel("planilhas/itens_cadastrados.xlsx")
            resultado = df.loc[df['Nome'].str.lower() == item_nome.lower()]
            if not resultado.empty:
                valor_item = resultado['Valor'].values[0]
                pesquisa_resultado.value = f"Valor de '{item_nome}': R$ {valor_item:.2f}"
            else:
                pesquisa_resultado.value = f"Item '{item_nome}' não encontrado."
            page.update()
        except Exception as ex:
            pesquisa_resultado.value = f"Erro ao pesquisar: {str(ex)}"
            page.update()

    def gerar_relatorio():
        df = pd.DataFrame(produtos_vendidos, columns=["Data", "Nome", "Quantidade", "Total (R$)"])
        if df.empty:
            relatorio_text.value = "Nenhum produto foi vendido ainda."
        else:
            resumo = df.groupby("Nome").agg({"Quantidade": "sum", "Total (R$)": "sum"}).reset_index()
            relatorio_text.value = "\n".join([f"{row['Nome']}: Quantidade Vendida: {row['Quantidade']}, Lucro Total: R$ {row['Total (R$)']:.2f}" for _, row in resumo.iterrows()])
        page.update()

    nome_produto_venda = ft.TextField(label="Nome do Produto", width=250)
    valor_produto = ft.TextField(label="Valor do Produto (R$)", width=250)
    quantidade_produto = ft.TextField(label="Quantidade", width=250)
    desconto_produto = ft.TextField(label="Desconto (%)", width=250)
    valor_pago = ft.TextField(label="Valor Pago (R$)", width=250)

    lista_de_produtos = ft.ListView(height=700, spacing=10)
    total_resultado = ft.Text(value="Total: R$ 0.00", size=22, color=text_color)
    troco_resultado = ft.Text(value="Troco: R$ 0.00", size=22, color=text_color)
    troco_detalhado_resultado = ft.Text(value="", size=18, color=text_color)

    adicionar_produto_btn = ft.ElevatedButton(text="Adicionar Produto", on_click=adicionar_produto, bgcolor=cor_red, color=text_color, style=ft.ButtonStyle(padding=15))
    calcular_total_btn = ft.ElevatedButton(text="Calcular Total", on_click=calcular_total, bgcolor=cor_red, color=text_color, style=ft.ButtonStyle(padding=15))
    calcular_troco_btn = ft.ElevatedButton(text="Calcular Troco", on_click=calcular_troco, bgcolor=cor_red, color=text_color, style=ft.ButtonStyle(padding=15))

    # Adicionando a imagem do Jaspion e logo do CETEP
    logo_path_jaspion = os.path.join(os.path.dirname(__file__), "assets/jaspion_logo.png")
    jaspion_logo = ft.Image(src=logo_path_jaspion, width=100, height=100, fit=ft.ImageFit.CONTAIN)
    logo_path_cetep = os.path.join(os.path.dirname(__file__), "assets/cetep_logo.png") if tema_escuro else os.path.join(os.path.dirname(__file__), "assets/cetep_logo_black.png")
    cetep_logo = ft.Image(src=logo_path_cetep, width=100, height=100, fit=ft.ImageFit.CONTAIN)

    # Campos para pesquisa de valor de item
    nome_produto_pesquisa = ft.TextField(label="Nome do Produto para Pesquisa", width=250)
    pesquisa_resultado = ft.Text(value="", size=18, color=text_color)
    pesquisar_valor_btn = ft.ElevatedButton(text="Pesquisar Valor", on_click=pesquisar_valor, bgcolor=cor_red, color=text_color, style=ft.ButtonStyle(padding=15))

    # Relatório de produtos vendidos
    relatorio_text = ft.Text(value="", size=18, color=text_color)

    # Adicionando a barra de navegação lateral
    def show_section(section):
        home_container.visible = section == "home"
        adicionar_calcular_container.visible = section == "adicionar_calcular"
        pesquisar_valor_container.visible = section == "pesquisar"
        relatorio_container.visible = section == "relatorio"
        configuracoes_container.visible = section == "configuracoes"
        if section == "relatorio":
            gerar_relatorio()
        page.update()

    nav_items = ft.Column(
        [
            ft.ListTile(
                title=ft.Text("Home", size=15, color=text_color),
                bgcolor = cor_red,
                leading=ft.Icon(name=ft.icons.HOME),
                on_click=lambda e: show_section("home")
            ),
            ft.ListTile(
                title=ft.Text("Venda de produtos", size=15, color=text_color),
                bgcolor = cor_red,
                leading=ft.Icon(name=ft.icons.ADD_SHOPPING_CART),
                on_click=lambda e: show_section("adicionar_calcular")
            ),
            ft.ListTile(
                title=ft.Text("Pesquisar Valor de Produto", size=15, color=text_color),
                bgcolor = cor_red,
                leading=ft.Icon(name=ft.icons.SEARCH),
                on_click=lambda e: show_section("pesquisar")
            ),
            ft.ListTile(
                title=ft.Text("Relatório de Vendas", size=15, color=text_color),
                bgcolor = cor_red,
                leading=ft.Icon(name=ft.icons.ASSESSMENT),
                on_click=lambda e: show_section("relatorio")
            ),
            ft.ListTile(
                title=ft.Text("Configurações", size=15, color=text_color),
                bgcolor = cor_red,
                leading=ft.Icon(name=ft.icons.SETTINGS),
                on_click=lambda e: show_section("configuracoes")
            ),
        ],
        width=200,
    )

    # Contêineres de cada seção
    adicionar_calcular_container = ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("Adicionar Produto", size=22, color=text_color),
                        nome_produto_venda,
                        valor_produto,
                        quantidade_produto,
                        adicionar_produto_btn,
                    
                    ],
                    spacing=30,
                ),
                
                

                ft.Column(
                    [
                        ft.Text("Calcular Total e Troco", size=22, color=text_color),
                        desconto_produto,
                        calcular_total_btn,
                        total_resultado,
                        valor_pago,
                        calcular_troco_btn,
                        troco_resultado,
                        troco_detalhado_resultado,
                    ],
                    spacing=30,
                ),
                
                ft.Column(
                    [
                        
                        ft.Text("Lista de produtos adicionados:", size=20, color=text_color),
                        lista_de_produtos,
                    ],
                    spacing=30,
                ),

            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        visible=False,
    )

    pesquisar_valor_container = ft.Container(
        content=ft.Column(
            [
                ft.Text("Pesquisar o preço de um produto", size=22, color=text_color),
                nome_produto_pesquisa,
                pesquisar_valor_btn,
                pesquisa_resultado,
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
        ),
        visible=False,
    )

    # Adicionando a imagem do Jaspion na home
    home_container = ft.Container(
        content=ft.Column(
            [
                ft.Text("Bem-vindo ao sistema Jaspion!", size=20, color=text_color),
                jaspion_logo,
                ft.Text("""
Desenvolvido para auxiliar microempreendedores e pequenos comerciantes a agilizar e gerenciar suas vendas.
Versão: 0.1
Website: Em breve
""", size=20, color=text_color),
                ft.Text('''"Um livro, uma caneta, uma criança e um professor podem mudar o mundo." Malala Yousafzai
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        ''', size=15, color=text_color),
                cetep_logo,
            ],
                
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        ),
        visible=True,
    )

    # Adicionando o contêiner de relatório de vendas
    relatorio_container = ft.Container(
        content=ft.Column(
            [
                ft.Text("Relatório de Produtos Vendidos", size=22, color=text_color),
                relatorio_text,
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
        ),
        visible=False,
    )

    # Adicionando o contêiner de configurações
    configuracoes_container = ft.Container(
        content=ft.Column(
            [
                ft.Text("Configurações", size=22, color=text_color),
                ft.ElevatedButton(text="Alternar Tema", on_click=alternar_tema, bgcolor=cor_red, color=text_color, style=ft.ButtonStyle(padding=15)),
                ft.Text("Tamanho do Texto", size=tamanho_texto, color=text_color),
                ft.Slider(min=12, max=24, value=tamanho_texto, divisions=12, on_change=ajustar_tamanho_texto)
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
        ),
        visible=False,
    )

    # Organizando as seções em uma linha
    container = ft.Container(
        content=ft.Row(
            [
                nav_items,
                ft.VerticalDivider(color=text_color),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        [
                            home_container,
                            adicionar_calcular_container,
                            pesquisar_valor_container,
                            relatorio_container,
                            configuracoes_container,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        padding=20
    )

    page.add(container)
    update_tema()

ft.app(target=main)