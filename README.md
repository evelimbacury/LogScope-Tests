# Relatório de Testes - LogScope 1.0

## Tabela de Bugs e Sugestões
Ordem de prioridade: 
    
    0 - Sem prioridade

    1 - Estético

    2 - Simples

    3 - Grave

    4 - Catastrófico

### Teste de Interface
| Id | Tipo      | Descrição                                                                                                                                                        | Grau de Severidade | Prioridade | Data de Report |
|----|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|------------|---------------|
| 1  | Sugestão | As guias "base pura" e a "base tratada" não estão no mesmo formato de organização de tabela. A base tratada possui as colunas "above_20dBm", "15dBm_to_20dBm", "8dBm_to_15dBm", "0dBm_to_8dBm", "less_than_0dBm", enquanto a base de dados não segue esse padrão. | Sem prioridade           | 0          | 19/02/2025    |
| 2  | Sugestão | Na guia "base pura", o excesso de tratamento de erros ao clicar em **"Visualizar"** antes de selecionar um arquivo. O tratamento deve parar assim que for identificado que não há arquivo selecionado. | Estético              | 1          | 19/02/2025    |
| 3  | Sugestão | O input "entry_arquivo" deveria estar desabilitado | Estético              | 1          | 19/02/2025    |
| 4  | Sugestão | Para uma melhor experiência, o sistema poderia carregar as guias "base pura" e "base tratada" automaticamente, sem a necessidade do usuário pressionar o botão "Visualizar". | Sem prioridade | 0          | 19/02/2025    |
| 5  | Sugestão | O sistema poderia criar uma pasta própria para os arquivos de csv gerados. | Estético              | 1          | 19/02/2025    |

### Testes sem Arquivo Selecionado  

| Id | Tipo      | Descrição                                                                                                                                                        | Grau de Severidade | Prioridade | Data de Report |
|----|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|------------|---------------|   
| 6  | Erro     | Na guia "base tratada", o sistema não impede a execução de tratamentos de erro desnecessários ao clicar em **"Visualizar"** sem arquivo selecionado. Em vez de evitar o tratamento, ele tenta processá-lo de qualquer forma. | Simples              | 2          | 19/02/2025    |
| 7  | Erro     | Ao tentar gerar um gráfico em "Gráfico 4G" sem ter selecionado um arquivo, o programa não trata corretamente o erro, resultando em uma falha. | Simples              | 2          | 19/02/2025    |
| 8  | Erro     | Ao tentar gerar um gráfico em "Gráfico 5G" sem ter selecionado um arquivo, o programa não trata corretamente o erro, resultando em uma falha. | Simples              | 2          | 19/02/2025    |
| 9  | Erro     | Ao tentar gerar um gráfico em "Gráfico TX" sem ter selecionado um arquivo, o programa não trata corretamente o erro, resultando em uma falha. | Simples              | 2          | 19/02/2025    |

## Com Arquivo Selecionado
### Testes em Gráficos sem Filtro Selecionado
| Id | Tipo      | Descrição  | Grau de Severidade | Prioridade | Data de Report |
|----|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|------------|---------------|   
| 10  | Erro     | Os gráficos plotam mesmo sem nenhum filtro selecionado. | Estético              | 1          | 19/02/2025    |



### Testes em Gráficos com Filtro Selecionado
| Id | Tipo      | Descrição  | Grau de Severidade | Prioridade | Data de Report |
|----|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|------------|---------------|   
| 11  | Erro     | Ao plotar os gráficos que não possuem dados correspondentes ao filtro selecionado, o programa deveria plotar uma mensagem de aviso. | Estético              | 1          | 19/02/2025    |


---

### Log de Erros  

Erro gerado no Teste 6
```python
Exception in Tkinter callback
Traceback (most recent call last):
  File "C:\Users\eveli\AppData\Local\Programs\Python\Python313\Lib\tkinter\__init__.py", line 2068, in __call__
    return self.func(*args)
           ~~~~~~~~~^^^^^^^
  File "C:\Users\eveli\Desktop\Mob4IA\Fev\LogScope\Teste\19-02-2025\LogScope1.0.py", line 122, in combinar_tabelas
    df_combinado = pd.merge(df1, df2, on=["data", "hora"], how="outer")
  File "C:\Users\eveli\Desktop\Mob4IA\Fev\LogScope\Teste\19-02-2025\venv\Lib\site-packages\pandas\core\reshape\merge.py", line 152, in merge
    left_df = _validate_operand(left)
  File "C:\Users\eveli\Desktop\Mob4IA\Fev\LogScope\Teste\19-02-2025\venv\Lib\site-packages\pandas\core\reshape\merge.py", line 2692, in _validate_operand
    raise TypeError(
        f"Can only merge Series or DataFrame objects, a {type(obj)} was passed"
    )
TypeError: Can only merge Series or DataFrame objects, a <class 'NoneType'> was passed
```

Erro gerado no Teste 7
```python
Exception in Tkinter callback
Traceback (most recent call last):
  File "C:\Users\eveli\AppData\Local\Programs\Python\Python313\Lib\tkinter\__init__.py", line 2068, in __call__
    return self.func(*args)
           ~~~~~~~~~^^^^^^^
  File "C:\Users\eveli\Desktop\Mob4IA\Fev\LogScope\Teste\19-02-2025\LogScope1.0.py", line 189, in gerar_grafico_4G
           ~~~~~~~~~^^^^^^^
  File "C:\Users\eveli\Desktop\Mob4IA\Fev\LogScope\Teste\19-02-2025\LogScope1.0.py", line 189, in gerar_grafico_4G
    if df_combinado is None:
       ^^^^^^^^^^^^
           ~~~~~~~~~^^^^^^^
  File "C:\Users\eveli\Desktop\Mob4IA\Fev\LogScope\Teste\19-02-2025\LogScope1.0.py", line 189, in gerar_grafico_4G
    if df_combinado is None:
           ~~~~~~~~~^^^^^^^
  File "C:\Users\eveli\Desktop\Mob4IA\Fev\LogScope\Teste\19-02-2025\LogScope1.0.py", line 189, in gerar_grafico_4G
  File "C:\Users\eveli\Desktop\Mob4IA\Fev\LogScope\Teste\19-02-2025\LogScope1.0.py", line 189, in gerar_grafico_4G
    if df_combinado is None:
       ^^^^^^^^^^^^
NameError: name 'df_combinado' is not defined
```

Erro gerado no Teste 8
```python
Exception in Tkinter callback
Traceback (most recent call last):
  File "C:\Users\eveli\AppData\Local\Programs\Python\Python313\Lib\tkinter\__init__.py", line 2068, in __call__
    return self.func(*args)
           ~~~~~~~~~^^^^^^^
  File "C:\Users\eveli\Desktop\Mob4IA\Fev\LogScope\Teste\19-02-2025\LogScope1.0.py", line 189, in gerar_grafico_4G
    if df_combinado is None:
       ^^^^^^^^^^^^
NameError: name 'df_combinado' is not defined
Exception in Tkinter callback
Traceback (most recent call last):
  File "C:\Users\eveli\AppData\Local\Programs\Python\Python313\Lib\tkinter\__init__.py", line 2068, in __call__
    return self.func(*args)
           ~~~~~~~~~^^^^^^^
  File "C:\Users\eveli\Desktop\Mob4IA\Fev\LogScope\Teste\19-02-2025\LogScope1.0.py", line 257, in gerar_grafico_5G
    if df_combinado is None:
       ^^^^^^^^^^^^
NameError: name 'df_combinado' is not defined

```

Erro gerado no Teste 9
```python
Exception in Tkinter callback
Traceback (most recent call last):
  File "C:\Users\eveli\AppData\Local\Programs\Python\Python313\Lib\tkinter\__init__.py", line 2068, in __call__
    return self.func(*args)
           ~~~~~~~~~^^^^^^^
  File "C:\Users\eveli\Desktop\Mob4IA\Fev\LogScope\Teste\19-02-2025\LogScope1.0.py", line 324, in gerar_grafico_TX
    if df_combinado is None:
       ^^^^^^^^^^^^
NameError: name 'df_combinado' is not defined

```
