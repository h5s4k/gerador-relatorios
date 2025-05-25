import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import numpy as np
import os
from fpdf import FPDF

class GeradorRelatoriosFinanceiros:
    def __init__(self):
        """Inicializa a classe com dados vazios"""
        self.dados = pd.DataFrame(columns=['Data', 'Categoria', 'Valor', 'Tipo'])
        self.carregar_dados()  # Chama o método de carregamento de dados
        
    def carregar_dados(self):
        """Oferece opções para carregar dados: exemplo ou do usuário"""
        print("\nOPÇÕES DE CARREGAMENTO DE DADOS:")
        print("1. Usar dados de exemplo (gerados automaticamente)")
        print("2. Inserir meus próprios dados")
        print("3. Continuar com dados vazios")
        
        while True:
            opcao = input("Escolha uma opção (1/2/3): ")
            
            if opcao == '1':
                self.carregar_dados_exemplo()
                break
            elif opcao == '2':
                self.inserir_dados_manualmente()
                break
            elif opcao == '3':
                print("Continuando com DataFrame vazio.")
                break
            else:
                print("Opção inválida. Tente novamente.")
    
    def carregar_dados_exemplo(self):
        """Gera dados de exemplo para demonstração"""
        np.random.seed(42)
        dates = pd.date_range(end=datetime.today(), periods=90).tolist()
        categorias = ['Vendas', 'Despesas Operacionais', 'Custos de Produção', 'Investimentos', 'Outros']
        
        dados = {
            'Data': dates * len(categorias),
            'Categoria': sorted(categorias * len(dates)),
            'Valor': np.random.normal(loc=10000, scale=3000, size=len(dates)*len(categorias)).round(2),
            'Tipo': np.random.choice(['Receita', 'Despesa'], size=len(dates)*len(categorias))
        }
        
        self.dados = pd.DataFrame(dados)
        self.dados['Mês'] = self.dados['Data'].dt.to_period('M')
        print("\nDados de exemplo carregados com sucesso!")
    
    def inserir_dados_manualmente(self):
        """Permite ao usuário inserir seus próprios dados"""
        print("\nINSERÇÃO DE DADOS FINANCEIROS")
        print("Formato esperado: Data (DD/MM/AAAA), Categoria, Valor, Tipo (Receita/Despesa)")
        print("Digite 'sair' para terminar a entrada de dados\n")
        
        registros = []
        contador = 1
        
        while True:
            print(f"Registro #{contador}")
            data = input("Data (DD/MM/AAAA): ")
            if data.lower() == 'sair':
                break
                
            categoria = input("Categoria: ")
            if categoria.lower() == 'sair':
                break
                
            valor = input("Valor: ")
            if valor.lower() == 'sair':
                break
                
            tipo = input("Tipo (Receita/Despesa): ")
            if tipo.lower() == 'sair':
                break
            
            try:
                data_obj = datetime.strptime(data, '%d/%m/%Y')
                valor_float = float(valor)
                tipo = tipo.capitalize()
                
                if tipo not in ['Receita', 'Despesa']:
                    print("Tipo deve ser 'Receita' ou 'Despesa'. Registro ignorado.")
                    continue
                    
                registros.append({
                    'Data': data_obj,
                    'Categoria': categoria,
                    'Valor': valor_float,
                    'Tipo': tipo
                })
                contador += 1
            except ValueError as e:
                print(f"Erro na entrada: {e}. Por favor, tente novamente.")
        
        if registros:
            self.dados = pd.DataFrame(registros)
            self.dados['Mês'] = self.dados['Data'].dt.to_period('M')
            print(f"\n{len(registros)} registros carregados com sucesso!")
        else:
            print("Nenhum dado válido inserido. Continuando com DataFrame vazio.")
    
    def resumo_mensal(self):
        """Gera um resumo financeiro mensal"""
        if self.dados.empty:
            print("Nenhum dado disponível para análise.")
            return None
            
        try:
            resumo = self.dados.groupby(['Mês', 'Tipo'])['Valor'].sum().unstack()
            resumo['Lucro'] = resumo.get('Receita', 0) - resumo.get('Despesa', 0)
            return resumo
        except Exception as e:
            print(f"Erro ao gerar resumo mensal: {e}")
            return None
    
    def relatorio_por_categoria(self):
        """Gera um relatório por categoria"""
        if self.dados.empty:
            print("Nenhum dado disponível para análise.")
            return None
            
        try:
            return self.dados.groupby(['Categoria', 'Tipo'])['Valor'].sum().unstack()
        except Exception as e:
            print(f"Erro ao gerar relatório por categoria: {e}")
            return None
    
    def plot_evolucao_mensal(self):
        """Cria um gráfico de evolução mensal"""
        if self.dados.empty:
            print("Nenhum dado disponível para plotar.")
            return None
            
        resumo = self.resumo_mensal()
        if resumo is None or resumo.empty:
            return None
        
        plt.figure(figsize=(10, 6))
        
        # Verifica quais colunas existem para plotar
        colunas_disponiveis = []
        if 'Receita' in resumo.columns:
            colunas_disponiveis.append('Receita')
        if 'Despesa' in resumo.columns:
            colunas_disponiveis.append('Despesa')
        
        if not colunas_disponiveis:
            print("Nenhum dado de Receita ou Despesa disponível para plotar.")
            plt.close()
            return None
            
        resumo[colunas_disponiveis].plot(kind='bar', stacked=False)
        plt.title('Evolução Mensal de Receitas e Despesas')
        plt.ylabel('Valor (R$)')
        plt.xlabel('Mês')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--')
        plt.tight_layout()
        return plt

    def plot_distribuicao_categorias(self):
        """Cria um gráfico de pizza com distribuição por categoria"""
        if self.dados.empty:
            print("Nenhum dado disponível para plotar.")
            return None
            
        # Verifica se há despesas para plotar
        if 'Despesa' not in self.dados['Tipo'].unique():
            print("Nenhuma despesa encontrada para plotar.")
            return None
            
        dados_plot = self.dados[self.dados['Tipo'] == 'Despesa'].groupby('Categoria')['Valor'].sum()
        
        if dados_plot.empty:
            print("Nenhuma despesa encontrada para plotar.")
            return None
            
        plt.figure(figsize=(8, 8))
        dados_plot.plot(kind='pie', autopct='%1.1f%%', startangle=90)
        plt.title('Distribuição de Despesas por Categoria')
        plt.ylabel('')
        return plt
    
    def exportar_para_excel(self, caminho='relatorio_financeiro.xlsx'):
        """Exporta os relatórios para um arquivo Excel"""
        if self.dados.empty:
            print("Nenhum dado disponível para exportar.")
            return
            
        try:
            with pd.ExcelWriter(caminho) as writer:
                resumo = self.resumo_mensal()
                if resumo is not None:
                    resumo.to_excel(writer, sheet_name='Resumo Mensal')
                
                rel_cat = self.relatorio_por_categoria()
                if rel_cat is not None:
                    rel_cat.to_excel(writer, sheet_name='Por Categoria')
            
            print(f"Relatório exportado para {caminho}")
        except Exception as e:
            print(f"Erro ao exportar para Excel: {e}")
    
    def exportar_para_pdf(self, caminho='relatorio_financeiro.pdf'):
        #Exporta os relatórios para PDF com gráficos"""
        if self.dados.empty:
            print("Nenhum dado disponível para exportar.")
            return
            
        fig1 = None
        fig2 = None
        fig1_path = None
        fig2_path = None
        
        try:
            # Criar PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12, style='B')
            pdf.cell(200, 10, txt="Relatório Financeiro", ln=True, align='C')
            pdf.set_font("Arial", size=10)
            pdf.cell(200, 10, txt=f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
            
            # Adicionar resumo mensal
            pdf.ln(10)
            pdf.cell(200, 10, txt="Resumo Mensal:", ln=True)
            pdf.ln(5)
            
            # Converter DataFrame para texto para o PDF
            resumo = self.resumo_mensal()
            if resumo is not None:
                resumo_text = resumo.to_string()
                for line in resumo_text.split('\n'):
                    pdf.cell(200, 6, txt=line, ln=True)
            
            # Adicionar gráfico de evolução mensal
            plt.figure()  # Cria uma nova figura
            self.plot_evolucao_mensal()
            fig1 = plt.gcf()  # Obtém a figura atual
            if fig1 is not None:
                fig1_path = 'temp_evolucao.png'
                fig1.savefig(fig1_path, bbox_inches='tight')
                plt.close(fig1)  # Fecha a figura específica
                
                pdf.ln(10)
                pdf.cell(200, 10, txt="Evolução Mensal:", ln=True)
                pdf.image(fig1_path, x=10, y=None, w=180)
            
            # Adicionar gráfico de distribuição
            plt.figure()  # Cria uma nova figura
            self.plot_distribuicao_categorias()
            fig2 = plt.gcf()  # Obtém a figura atual
            if fig2 is not None:
                fig2_path = 'temp_distribuicao.png'
                fig2.savefig(fig2_path, bbox_inches='tight')
                plt.close(fig2)  # Fecha a figura específica
                
                pdf.ln(85 if fig1 is not None else 10)
                pdf.cell(200, 10, txt="Distribuição de Despesas:", ln=True)
                pdf.image(fig2_path, x=30, y=None, w=140)
            
            # Salvar PDF
            pdf.output(caminho)
            print(f"Relatório exportado para {caminho}")
            
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
        finally:
            # Limpar arquivos temporários
            if fig1_path and os.path.exists(fig1_path):
                os.remove(fig1_path)
            if fig2_path and os.path.exists(fig2_path):
                os.remove(fig2_path)
            plt.close('all')  # Fecha todas as figuras abertas
    
    def mostrar_dashboard(self):
        """Mostra um dashboard simples no console"""
        if self.dados.empty:
            print("\nNenhum dado disponível para mostrar dashboard.")
            return
            
        print("\n" + "="*50)
        print("DASHBOARD FINANCEIRO".center(50))
        print("="*50 + "\n")
        
        print("RESUMO MENSAL:")
        resumo = self.resumo_mensal()
        if resumo is not None:
            print(resumo)
        else:
            print("Não foi possível gerar o resumo mensal.")
        
        print("\nDISTRIBUIÇÃO POR CATEGORIA:")
        rel_cat = self.relatorio_por_categoria()
        if rel_cat is not None:
            print(rel_cat)
        else:
            print("Não foi possível gerar o relatório por categoria.")
        
        print("\nVISUALIZAÇÕES:")
        try:
            fig1 = self.plot_evolucao_mensal()
            if fig1 is not None:
                fig1.show(block=False)
            
            fig2 = self.plot_distribuicao_categorias()
            if fig2 is not None:
                fig2.show(block=False)
            
            plt.pause(2)  # Mostra os gráficos por 2 segundos
            plt.close('all')
        except Exception as e:
            print(f"\nErro ao exibir gráficos: {e}")
            print("Certifique-se de ter instalado PyQt5 ou PySide2")


# Exemplo de uso
if __name__ == "__main__":
    gerador = GeradorRelatoriosFinanceiros()
    
    while True:
        print("\nMENU PRINCIPAL")
        print("1. Visualizar Dashboard no Console")
        print("2. Exportar para Excel")
        print("3. Exportar para PDF")
        print("4. Mostrar Gráfico de Evolução Mensal")
        print("5. Mostrar Gráfico de Distribuição de Despesas")
        print("6. Carregar Novos Dados")
        print("7. Sair")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            gerador.mostrar_dashboard()
        elif opcao == '2':
            nome_arquivo = input("Nome do arquivo Excel (padrão: relatorio_financeiro.xlsx): ")
            if nome_arquivo:
                gerador.exportar_para_excel(nome_arquivo)
            else:
                gerador.exportar_para_excel()
        elif opcao == '3':
            nome_arquivo = input("Nome do arquivo PDF (padrão: relatorio_financeiro.pdf): ")
            if nome_arquivo:
                gerador.exportar_para_pdf(nome_arquivo)
            else:
                gerador.exportar_para_pdf()
        elif opcao == '4':
            plt.close('all')
            fig = gerador.plot_evolucao_mensal()
            if fig is not None:
                fig.show(block=False)
                plt.pause(0.1)
        elif opcao == '5':
            plt.close('all')
            fig = gerador.plot_distribuicao_categorias()
            if fig is not None:
                fig.show(block=False)
                plt.pause(0.1)
        elif opcao == '6':
            gerador.carregar_dados()
        elif opcao == '7':
            print("Saindo do sistema...")
            plt.close('all')
            break
        else:
            print("Opção inválida. Tente novamente.")