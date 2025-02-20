import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import AutoDateLocator, DateFormatter
import mplcursors

#========> seleção de arquivo no diretório do usuário <========#
def selecionar_arquivo():
    global caminho_arquivo
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione um arquivo",
        filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
    )
    if caminho_arquivo:
        entry_arquivo.delete(0, tk.END)
        entry_arquivo.insert(0, caminho_arquivo)

#========> Ler, processar e salvar dados extraídos <========#
def processar_tabela(padrao, colunas, nome_csv, tabela, processador_dados):
    global caminho_arquivo
    if not caminho_arquivo:
        messagebox.showerror("Erro", "Por favor, selecione um arquivo primeiro!")
        return
    
    dados = []
    with open(caminho_arquivo, "r") as file:
        for linha in file:
            correspondencia = padrao.search(linha)
            if correspondencia:
                dados.append(processador_dados(correspondencia))

    if dados:
        df = pd.DataFrame(dados, columns=colunas)
        df.to_csv(nome_csv, index=False)
        atualizar_tabela(tabela, df)
        return df
    else:
        messagebox.showwarning("Aviso", "Nenhuma correspondência encontrada no arquivo.")
        return None

#========> Adiciona uma aba para visualização das tabelas combinadas sem tratar <========#
def tabelas_combinadas():
    processar_tabela1()
    processar_tabela2()
    if df1 is not None and df2 is not None:
        df_combinado = pd.merge(df1, df2, on=["data", "hora"], how="outer")
        df_combinado.fillna(2147483647, inplace=True)
        tabela_tratada.delete(*tabela_tratada.get_children())
        atualizar_tabela(tabela_combinada, df_combinado)
    else:
        messagebox.showerror("Erro", "As tabelas 1 e 2 precisam ser processadas primeiro!")   

#========> Atualiza uma tabela com dados do csv <========#
def atualizar_tabela(tabela, dataframe):
    tabela.delete(*tabela.get_children())
    for _, row in dataframe.iterrows():
        tabela.insert("", "end", values=list(row))

#========> Processa os dados do arquivo em uma tabela <========#
def processar_tabela1():
    padrao1 = re.compile(
        r'(?P<data>\d{2}-\d{2})\s(?P<hora>\d{2}:\d{2}:\d{2})'
        r'.*rssi=(?P<rssi>-?\d+)'
        r'.*?rsrp=(?P<rsrp>-?\d+)'
        r'.*?rsrq=(?P<rsrq>-?\d+)'
        r'.*?rssnr=(?P<rssnr>-?\d+)'
        r'.*?ssRsrp\s=\s(?P<ssrsrp>-?\d+)'
        r'.*?ssRsrq\s=\s(?P<ssrsrq>-?\d+)'
        r'.*?ssSinr\s=\s(?P<sssinr>-?\d+)'
    )
    
    global df1
    df1 = processar_tabela(
        padrao1,
        ["data", "hora", "rssi", "rsrp", "rsrq", "rssnr", "ssrsrp", "ssrsrq", "sssinr"],
        "dados_filtrados_p1.csv",
        tabela_tratada,
        lambda m: m.groupdict()
    )

#========> Processa os dados do arquivo em uma segunda tabela <========#
def processar_tabela2():
    padrao2 = re.compile(
        r'(?P<data>\d{2}-\d{2})\s(?P<hora>\d{2}:\d{2}:\d{2})'
        r'.*?mTxTimeMs\[\]=\[(?P<valores>[\d,\s]+)\]'
    )
    
    def extrair_dados(m):
        valores = [int(v.strip()) for v in m.group("valores").split(",")]
        if len(valores) == 5:
            return {
                "data": m.group("data"),
                "hora": m.group("hora"),
                "above_20dBm": valores[0],
                "15dBm_to_20dBm": valores[1],
                "8dBm_to_15dBm": valores[2],
                "0dBm_to_8dBm": valores[3],
                "less_than_0dBm": valores[4],
            }
        
    global df2
    df2 = processar_tabela(
        padrao2,
        ["data", "hora", "above_20dBm", "15dBm_to_20dBm", "8dBm_to_15dBm", "0dBm_to_8dBm", "less_than_0dBm"],
        "dados_filtrados_p2.csv",
        tabela_tratada,
        extrair_dados
    )

#========> Combina e Trata os dados do arquivo <========#
def combinar_tabelas():
    global df1, df2, df_combinado
    processar_tabela1()
    processar_tabela2()

    df_combinado = pd.merge(df1, df2, on=["data", "hora"], how="outer")

    colunas_numericas = df_combinado.select_dtypes(include=['number']).columns
    df_combinado[colunas_numericas] = df_combinado[colunas_numericas].fillna(0)

    df_combinado.sort_values(by=["data", "hora"], inplace=True)

    colunas_tabela2 = [col for col in df2.columns if col not in ["data", "hora"]]
    colunas_tabela1 = [col for col in df1.columns if col not in ["data", "hora"]]
    nova_ordem_colunas = ["data", "hora"] + colunas_tabela2 + colunas_tabela1
    df_combinado = df_combinado[nova_ordem_colunas]

    df_combinado = df_combinado.fillna(method='ffill').fillna(method='bfill')

    for coluna in colunas_numericas:
        df_combinado[coluna] = df_combinado[coluna].replace(0, pd.NA)
        df_combinado[coluna] = df_combinado[coluna].fillna(0)

    colunas_substituir = ["rssnr","sssinr"]
    for coluna in colunas_substituir:
        if coluna in df_combinado.columns:
            df_combinado[coluna] = df_combinado[coluna].replace("2147483647", "NA")

    if 'rssi' in df_combinado.columns:
        df_combinado['rede_atual'] = df_combinado['rssi'].apply(lambda x: '5G' if x == "2147483647" else '4G')

    df_combinado.to_csv("arquivo_combinado.csv", index=False)

    atualizar_tabela(tabela_tratada, df_combinado)

    messagebox.showinfo("Sucesso", "Csv gerado, Salvo na pasta aonde está o código!")

#========> Cria a tabela e mostra pro usuário <========#
def executar_tabela(frame, colunas, texto_botao, comando):
    tabela_frame = tk.Frame(frame)
    tabela_frame.pack(fill="both", expand=True)

    tabela = ttk.Treeview(tabela_frame, columns=colunas, show="headings", height=15)
    for col in colunas:
        tabela.heading(col, text=col)
        tabela.column(col, width=50)
    scrollbar = tk.Scrollbar(tabela_frame, orient="vertical", command=tabela.yview)
    scrollbar.pack(side="right", fill="y")
    tabela.configure(yscrollcommand=scrollbar.set)
    tabela.pack(side="left", fill="both", expand=True)

    botao = tk.Button(frame, text=texto_botao, command=comando)
    botao.pack(pady=10)

    return tabela

def salvar_grafico(fig, nome_arquivo="grafico.png"):
    caminho_arquivo = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("Arquivos PNG", "*.png"), ("Todos os arquivos", "*.*")],
        title="Salvar gráfico como",
        initialfile=nome_arquivo
    )
    if caminho_arquivo:
        fig.savefig(caminho_arquivo, dpi=300)
        messagebox.showinfo("Sucesso", f"Gráfico salvo em:\n{caminho_arquivo}")

grafico_atual = None

def gerar_grafico_4G():
    global df_combinado, grafico_atual, fig_4G, canvas_4G, toolbar_4G
    
    if df_combinado is None:
        messagebox.showerror("Erro", "Por favor, combine as tabelas primeiro!")
        return
    
    if grafico_atual is not None:
        grafico_atual.get_tk_widget().destroy()
        if hasattr(grafico_atual, 'toolbar'):
            grafico_atual.toolbar.destroy()
    
    fig_4G, ax = plt.subplots(figsize=(10, 5))

    linhas = []

    df_combinado['hora'] = pd.to_datetime(df_combinado['hora'], errors='coerce')
    
    df_4G = df_combinado[df_combinado['rede_atual'] == '4G'].copy()

    colunas_sinal_4G = ['rssi', 'rsrp', 'rsrq', 'rssnr']
    for col in colunas_sinal_4G:
        df_4G[col] = pd.to_numeric(df_4G[col], errors='coerce')
        df_4G[col].replace(2147483647, np.nan, inplace=True)
    df_4G.dropna(subset=colunas_sinal_4G, inplace=True)

    if var_rssi.get():
        linha, =ax.plot(df_4G['hora'], df_4G['rssi'], marker='', linestyle='-', label='RSSI', alpha=0.7)
        linhas.append(linha)
    if var_rsrp.get():
        linha, =ax.plot(df_4G['hora'], df_4G['rsrp'], marker='', linestyle='-', label='RSRP', alpha=0.7)
        linhas.append(linha)
    if var_rsrq.get():
        linha, =ax.plot(df_4G['hora'], df_4G['rsrq'], marker='', linestyle='-', label='RSRQ', alpha=0.7)
        linhas.append(linha)
    if var_rssnr.get():
        linha, =ax.plot(df_4G['hora'], df_4G['rssnr'], marker='', linestyle='-', label='RSSNR', alpha=0.7)
        linhas.append(linha)
    
    ax.set_ylim(-120, 30)
    ax.set_xlabel("Hora")
    ax.set_ylabel("dBm")
    ax.set_title("Variação dos Sinais 4G ao Longo do Tempo")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)

    ax.xaxis.set_major_locator(AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    canvas_4G = FigureCanvasTkAgg(fig_4G, master=bgraficos4G)
    canvas_4G.get_tk_widget().pack(fill="both", expand=True)
    
    toolbar_4G = NavigationToolbar2Tk(canvas_4G, bgraficos4G)
    toolbar_4G.update()
    canvas_4G.get_tk_widget().pack(fill="both", expand=True)

    cursor = mplcursors.cursor(linhas, hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(
        f"Hora: {ax.xaxis.get_major_formatter().format_data(sel.target[0])}\n"
        f"Valor: {sel.target[1]:.0f}"
    ))
    
    grafico_atual = canvas_4G
    grafico_atual.draw()


def gerar_grafico_5G():
    global df_combinado, grafico_atual, fig_5G, canvas_5G, toolbar_5G

    if df_combinado is None:
        messagebox.showerror("Erro", "Por favor, combine as tabelas primeiro!")
        return

    if grafico_atual is not None:
        grafico_atual.get_tk_widget().destroy()
        if hasattr(grafico_atual, 'toolbar'):
            grafico_atual.toolbar.destroy()

    df_5G = df_combinado[df_combinado['rede_atual'] == '5G'].copy()

    linhas = []

    df_5G['hora'] = pd.to_datetime(df_5G['hora'])

    colunas_sinal = ['ssrsrp', 'ssrsrq', 'sssinr']
    for col in colunas_sinal:
        df_5G[col] = pd.to_numeric(df_5G[col], errors='coerce')
        df_5G[col].replace(2147483647, np.nan, inplace=True)

    df_5G.dropna(subset=colunas_sinal, inplace=True)

    fig_5G, ax = plt.subplots(figsize=(10, 5))

    if var_ssrsrp.get():
        linha, =ax.plot(df_5G['hora'], df_5G['ssrsrp'], marker='', linestyle='-', alpha=0.7, label='SSRSRP')
        linhas.append(linha)
    if var_ssrsrq.get():
        linha, =ax.plot(df_5G['hora'], df_5G['ssrsrq'], marker='', linestyle='-', alpha=0.7, label='SSRSRQ')
        linhas.append(linha)
    if var_sssinr.get():
        linha, =ax.plot(df_5G['hora'], df_5G['sssinr'], marker='', linestyle='-', alpha=0.7, label='SSSINR')
        linhas.append(linha)

    ax.set_xlabel("Hora")
    ax.set_ylabel("dBm")
    ax.set_title("Variação do Sinal 5G ao Longo do Tempo")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)

    ax.xaxis.set_major_locator(AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    plt.xticks(rotation=90, ha='right')

    ax.set_ylim(-130, 30)

    plt.tight_layout()

    canvas_5G = FigureCanvasTkAgg(fig_5G, master=bgraficos5G)
    canvas_5G.get_tk_widget().pack(fill="both", expand=True)

    toolbar_5G = NavigationToolbar2Tk(canvas_5G, bgraficos5G)
    toolbar_5G.update()
    canvas_5G.get_tk_widget().pack(fill="both", expand=True)

    cursor = mplcursors.cursor(linhas, hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(
        f"Hora: {ax.xaxis.get_major_formatter().format_data(sel.target[0])}\n"
        f"Valor: {sel.target[1]:.0f}"
    ))

    grafico_atual = canvas_5G
    grafico_atual.draw()

def gerar_grafico_TX():
    global df_combinado, grafico_atual, fig_TX, canvas_TX, toolbar_TX
    
    if df_combinado is None:
        messagebox.showerror("Erro", "Por favor, combine as tabelas primeiro!")
        return
    
    if grafico_atual is not None:
        grafico_atual.get_tk_widget().destroy()
        if hasattr(grafico_atual, 'toolbar'):
            grafico_atual.toolbar.destroy()
    
    fig_TX, ax = plt.subplots(figsize=(10, 5))

    linhas = []

    df_combinado['hora'] = pd.to_datetime(df_combinado['hora'])
    
    if var_above_20dBm.get():
        linha, =ax.plot(df_combinado['hora'], df_combinado['above_20dBm'], marker='', linestyle='-', label='above_20dBm')
        linhas.append(linha)
    if var_15dBm_to_20dBm.get():
        linha, =ax.plot(df_combinado['hora'], df_combinado['15dBm_to_20dBm'], marker='', linestyle='-', label='15dBm_to_20dBm')
        linhas.append(linha)
    if var_8dBm_to_15dBm.get():
        linha, =ax.plot(df_combinado['hora'], df_combinado['8dBm_to_15dBm'], marker='', linestyle='-', label='8dBm_to_15dBm')
        linhas.append(linha)
    if var_0dBm_to_8dBm.get():
        linha, =ax.plot(df_combinado['hora'], df_combinado['0dBm_to_8dBm'], marker='', linestyle='-', label='0dBm_to_8dBm')
        linhas.append(linha)
    if var_less_than_0dBm.get():
        linha, =ax.plot(df_combinado['hora'], df_combinado['less_than_0dBm'], marker='', linestyle='-', label='less_than_0dBm')
        linhas.append(linha)
    
    ax.set_xlabel("Hora")
    ax.set_ylabel("dBm")
    ax.set_title("Variação dos Valores de TX ao Longo do Tempo")
    ax.legend()
  
    ax.xaxis.set_major_locator(AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))

    ax.grid(False)

    plt.xticks(rotation=90, ha='right')
    plt.tight_layout()
    
    canvas_TX = FigureCanvasTkAgg(fig_TX, master=bgraficosTX)
    canvas_TX.get_tk_widget().pack(fill="both", expand=True)
    
    toolbar_TX = NavigationToolbar2Tk(canvas_TX, bgraficosTX)
    toolbar_TX.update()
    canvas_TX.get_tk_widget().pack(fill="both", expand=True)

    cursor = mplcursors.cursor(linhas, hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(
        f"Hora: {ax.xaxis.get_major_formatter().format_data(sel.target[0])}\n"
        f"Valor: {sel.target[1]:.0f}"
    ))
    
    grafico_atual = canvas_TX
    grafico_atual.draw()


#========> Configuração da janela principal <========#
root = tk.Tk()
root.title("LogScope")
largura_janela = 1500
altura_janela = 800

largura_tela = root.winfo_screenwidth()
altura_tela = root.winfo_screenheight()

pos_x = (largura_tela - largura_janela) // 2
pos_y = (altura_tela - altura_janela) // 2

root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

#========> Definição de variáveis globais <========#
caminho_arquivo = None
df1 = None
df2 = None

#========> Frame de seleção de arquivo <========#
frame_selecao = tk.Frame(root)
frame_selecao.pack(pady=10)

tk.Label(frame_selecao, text="Selecione o arquivo para realizar a tratamento de dados", font=("Verdana", 10)).grid(row=0, column=0, columnspan=2, pady=5)

tk.Label(frame_selecao, text="Selecionar arquivo:", font=("Verdana", 10)).grid(row=1, column=0, padx=5)
entry_arquivo = tk.Entry(frame_selecao, width=50)
entry_arquivo.grid(row=1, column=1, padx=5)
tk.Button(frame_selecao, text="Selecionar", command=selecionar_arquivo).grid(row=1, column=2, padx=5)

#========> Configuração do notebook <========#
notebook = ttk.Notebook(root)
notebook.pack(pady=20, fill="both", expand=True)

bpura = ttk.Frame(notebook)
notebook.add(bpura, text="Base Pura")

btratada = ttk.Frame(notebook) 
notebook.add(btratada, text="Base Tratada")

bgraficos4G = ttk.Frame(notebook)
notebook.add(bgraficos4G, text="Gráficos 4G")

bgraficos5G = ttk.Frame(notebook)
notebook.add(bgraficos5G, text="Gráficos 5G")

bgraficosTX = ttk.Frame(notebook)
notebook.add(bgraficosTX, text="Gráficos TX")

#========> Criação da Tabela Completa <========#
colunas_combinadas = ["data", "hora", "rssi", "rsrp", "rsrq", "rssnr", "ssrsrp", "ssrsrq", "sssinr", "above_20dBm", "15dBm_to_20dBm", "8dBm_to_15dBm", "0dBm_to_8dBm", "less_than_0dBm"]
tabela_combinada = executar_tabela(bpura, colunas_combinadas, "Visualizar", tabelas_combinadas)

colunas_tratadas = ["data", "hora", "above_20dBm", "15dBm_to_20dBm", "8dBm_to_15dBm", "0dBm_to_8dBm", "less_than_0dBm", "rssi", "rsrp", "rsrq", "rssnr", "ssrsrp", "ssrsrq", "sssinr", "rede_atual"]
tabela_tratada = executar_tabela(btratada, colunas_tratadas, "Visualizar", combinar_tabelas)

#========> Adicionando checkboxes para filtro de gráficos <========#
#4G
var_rssi = tk.BooleanVar()
var_rsrp = tk.BooleanVar()
var_rsrq = tk.BooleanVar()
var_rssnr = tk.BooleanVar()

#5G
var_ssrsrp = tk.BooleanVar()
var_ssrsrq = tk.BooleanVar()
var_sssinr = tk.BooleanVar()

#TX
var_above_20dBm = tk.BooleanVar()
var_15dBm_to_20dBm = tk.BooleanVar()
var_8dBm_to_15dBm = tk.BooleanVar()
var_0dBm_to_8dBm = tk.BooleanVar()
var_less_than_0dBm = tk.BooleanVar()

# Frame para os checkboxes 4G
frame_tempo = tk.Frame(bgraficos4G)
frame_tempo.pack(side="bottom", pady=10)

frame_filtro_4G = tk.Frame(bgraficos4G)
frame_filtro_4G.pack(side="bottom", pady=10)

label_filtro_4G = tk.Label(frame_filtro_4G, text="Filtros 4G:", font=("Verdana", 10, "bold"))
label_filtro_4G.grid(row=0, column=0, padx=5)

tk.Checkbutton(frame_filtro_4G, text="RSSI", variable=var_rssi).grid(row=0, column=1, padx=5)
tk.Checkbutton(frame_filtro_4G, text="RSRP", variable=var_rsrp).grid(row=0, column=2, padx=5)
tk.Checkbutton(frame_filtro_4G, text="RSRQ", variable=var_rsrq).grid(row=0, column=3, padx=5)
tk.Checkbutton(frame_filtro_4G, text="RSSNR", variable=var_rssnr).grid(row=0, column=4, padx=5)

# Frame para os checkboxes 5G
frame_tempo_5G = tk.Frame(bgraficos5G)
frame_tempo_5G.pack(side="bottom", pady=10)

frame_filtro_5G = tk.Frame(bgraficos5G)
frame_filtro_5G.pack(side="bottom", pady=10)

label_filtro_5G = tk.Label(frame_filtro_5G, text="Filtros 5G:", font=("Verdana", 10, "bold"))
label_filtro_5G.grid(row=0, column=0, padx=5)

tk.Checkbutton(frame_filtro_5G, text="SSRSRP", variable=var_ssrsrp).grid(row=0, column=1, padx=5)
tk.Checkbutton(frame_filtro_5G, text="SSRSRQ", variable=var_ssrsrq).grid(row=0, column=2, padx=5)
tk.Checkbutton(frame_filtro_5G, text="SSSINR", variable=var_sssinr).grid(row=0, column=3, padx=5)

# Frame para os checkboxes TX
frame_tempo_TX = tk.Frame(bgraficosTX)
frame_tempo_TX.pack(side="bottom", pady=10)

frame_filtro_TX = tk.Frame(bgraficosTX)
frame_filtro_TX.pack(side="bottom", pady=10)

label_filtro_TX = tk.Label(frame_filtro_TX, text="Filtros TX:", font=("Verdana", 10, "bold"))
label_filtro_TX.grid(row=0, column=0, padx=5)

tk.Checkbutton(frame_filtro_TX, text="Above 20dBm", variable=var_above_20dBm).grid(row=0, column=1, padx=5)
tk.Checkbutton(frame_filtro_TX, text="15dBm to 20dBm", variable=var_15dBm_to_20dBm).grid(row=0, column=2, padx=5)
tk.Checkbutton(frame_filtro_TX, text="8dBm to 15dBm", variable=var_8dBm_to_15dBm).grid(row=0, column=3, padx=5)
tk.Checkbutton(frame_filtro_TX, text="0dBm to 8dBm", variable=var_0dBm_to_8dBm).grid(row=0, column=4, padx=5)
tk.Checkbutton(frame_filtro_TX, text="Less Than 0dBm", variable=var_less_than_0dBm).grid(row=0, column=5, padx=5)

# Botão para gerar o gráfico com os filtros selecionados
btn_grafico_4G = tk.Button(frame_filtro_4G, text="Gerar Gráfico", command=gerar_grafico_4G)
btn_grafico_4G.grid(row=0, column=5, padx=10)

# Botão para gerar o gráfico com os filtros selecionados
btn_grafico_5G = tk.Button(frame_filtro_5G, text="Gerar Gráfico", command=gerar_grafico_5G)
btn_grafico_5G.grid(row=0, column=4, padx=10)

# Botão para gerar o gráfico com os filtros selecionados
btn_grafico_TX = tk.Button(frame_filtro_TX, text="Gerar Gráfico", command=gerar_grafico_TX)
btn_grafico_TX.grid(row=0, column=6, padx=10)

root.mainloop()