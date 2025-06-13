import pandas as pd
import sqlite3
import numpy as np
import re
from pathlib import Path

class ANACDataProcessor:
    """
    Classe para processar e tratar dados da ANAC antes de inserir no SQLite
    """
    
    def __init__(self, csv_file_path, db_path=None):
        self.csv_file_path = csv_file_path
        self.db_path = db_path or 'dados_voo.db'
        self.df = None
        
        # Mapeamento para correção de encoding
        self.encoding_fixes = {
            'M�S': 'MES',
            'AEROPORTO DE ORIGEM (REGI�O)': 'AEROPORTO DE ORIGEM (REGIAO)',
            'AEROPORTO DE ORIGEM (PA�S)': 'AEROPORTO DE ORIGEM (PAIS)',
            'AEROPORTO DE DESTINO (REGI�O)': 'AEROPORTO DE DESTINO (REGIAO)',
            'AEROPORTO DE DESTINO (PA�S)': 'AEROPORTO DE DESTINO (PAIS)',
            'PASSAGEIROS GR�TIS': 'PASSAGEIROS GRATIS',
            'CARGA GR�TIS (KG)': 'CARGA GRATIS (KG)',
            'COMBUST�VEL (LITROS)': 'COMBUSTIVEL (LITROS)',
            'DIST�NCIA VOADA (KM)': 'DISTANCIA VOADA (KM)'
        }
        
        # Colunas que devem ser numéricas
        self.numeric_columns = [
            'ANO', 'MES', 'PASSAGEIROS PAGOS', 'PASSAGEIROS GRATIS', 
            'CARGA PAGA (KG)', 'CARGA GRATIS (KG)', 'CORREIO (KG)',
            'ASK', 'RPK', 'ATK', 'RTK', 'COMBUSTIVEL (LITROS)',
            'DISTANCIA VOADA (KM)', 'DECOLAGENS', 'CARGA PAGA KM',
            'CARGA GRATIS KM', 'CORREIO KM', 'ASSENTOS', 'PAYLOAD',
            'HORAS VOADAS', 'BAGAGEM (KG)'
        ]
        
        # Colunas categóricas para validação
        self.categorical_columns = {
            'EMPRESA (NACIONALIDADE)': ['BRASILEIRA', 'ESTRANGEIRA'],
            'NATUREZA': ['DOMESTICA', 'INTERNACIONAL'],
            'GRUPO DE VOO': ['REGULAR', 'NAO REGULAR', 'IMPRODUTIVO']
        }

    def load_data(self):
        """Carrega os dados do CSV com tratamento de encoding"""
        print("📁 Carregando dados do CSV...")
        
        try:
            # Tenta diferentes encodings
            encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    self.df = pd.read_csv(
                        self.csv_file_path, 
                        sep=';', 
                        encoding=encoding,
                        low_memory=False
                    )
                    print(f"✅ Arquivo carregado com encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if self.df is None:
                raise Exception("Não foi possível carregar o arquivo com nenhum encoding testado")
                
            print(f"📊 Dados carregados: {len(self.df)} registros, {len(self.df.columns)} colunas")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False

    def remove_low_quality_records(self, min_completeness=50):
        """Remove registros com muitos dados faltantes"""
        print(f"🔍 Removendo registros com menos de {min_completeness}% de dados...")
        
        initial_count = len(self.df)
        
        # Calcular completude por linha de forma mais robusta
        total_columns = len(self.df.columns)
        print(f"   📊 Total de colunas: {total_columns}")
        
        # Contar campos preenchidos por linha (método mais preciso)
        completeness_list = []
        rows_to_remove = []
        
        for index, row in self.df.iterrows():
            filled_count = 0
            for value in row:
                # Verificar se o valor está preenchido
                if pd.notna(value) and str(value).strip() != '' and str(value).strip() != 'nan':
                    filled_count += 1
            
            completeness = (filled_count / total_columns) * 100
            completeness_list.append(completeness)
            
            # Marcar para remoção se abaixo do limite
            if completeness < min_completeness:
                rows_to_remove.append(index)
                print(f"   🗑️  Linha {index + 1}: {completeness:.1f}% completa ({filled_count}/{total_columns}) - SERÁ REMOVIDA")
        
        # Mostrar estatísticas de completude
        avg_completeness = sum(completeness_list) / len(completeness_list)
        print(f"   📊 Completude média: {avg_completeness:.1f}%")
        print(f"   📊 Encontrados {len(rows_to_remove)} registros com <{min_completeness}% de dados")
        
        # Remover registros problemáticos
        if rows_to_remove:
            self.df = self.df.drop(rows_to_remove).reset_index(drop=True)
            print(f"   ✅ Removidos {len(rows_to_remove)} registros problemáticos")
        else:
            print(f"   ✅ Nenhum registro encontrado abaixo de {min_completeness}%")
        
        final_count = len(self.df)
        removed_count = initial_count - final_count
        
        print(f"   📊 Registros iniciais: {initial_count}")
        print(f"   📊 Registros finais: {final_count}")
        print(f"   📊 Total removido: {removed_count}")
        
        return removed_count

    def fix_column_names(self):
        """Corrige os nomes das colunas com problemas de encoding"""
        print("🔧 Corrigindo nomes das colunas...")
        
        # Aplicar correções de encoding
        new_columns = []
        fixes_applied = 0
        
        for col in self.df.columns:
            if col in self.encoding_fixes:
                new_columns.append(self.encoding_fixes[col])
                fixes_applied += 1
                print(f"   ✓ {col} → {self.encoding_fixes[col]}")
            else:
                new_columns.append(col)
        
        self.df.columns = new_columns
        print(f"✅ {fixes_applied} correções de encoding aplicadas")

    def clean_numeric_data(self):
        """Limpa e converte dados numéricos"""
        print("🔢 Tratando dados numéricos...")
        
        conversion_count = 0
        
        for col in self.numeric_columns:
            if col in self.df.columns:
                # Substituir vírgulas por pontos e converter para numérico
                self.df[col] = self.df[col].astype(str).str.replace(',', '.', regex=False)
                
                # Tratar valores vazios e não numéricos
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                
                # Preencher NaN com 0 para colunas que faz sentido
                if col in ['PASSAGEIROS PAGOS', 'PASSAGEIROS GRATIS', 'CARGA PAGA (KG)', 
                          'CARGA GRATIS (KG)', 'CORREIO (KG)', 'BAGAGEM (KG)']:
                    self.df[col] = self.df[col].fillna(0)
                
                conversion_count += 1
                
        print(f"✅ {conversion_count} colunas numéricas processadas")

    def clean_categorical_data(self):
        """Limpa e padroniza dados categóricos"""
        print("📝 Tratando dados categóricos...")
        
        # Limpar espaços e padronizar maiúsculas
        categorical_cols = [
            'EMPRESA (SIGLA)', 'EMPRESA (NOME)', 'EMPRESA (NACIONALIDADE)',
            'AEROPORTO DE ORIGEM (SIGLA)', 'AEROPORTO DE ORIGEM (NOME)',
            'AEROPORTO DE DESTINO (SIGLA)', 'AEROPORTO DE DESTINO (NOME)',
            'NATUREZA', 'GRUPO DE VOO'
        ]
        
        for col in categorical_cols:
            if col in self.df.columns:
                # Remover espaços extras e converter para maiúscula
                self.df[col] = self.df[col].astype(str).str.strip().str.upper()
                
                # Tratar valores nulos
                self.df[col] = self.df[col].replace('NAN', pd.NA)
        
        # Correções específicas de encoding em dados
        self.df = self.df.replace({
            'DOM�STICA': 'DOMESTICA',
            'N�O REGULAR': 'NAO REGULAR',
            'GR�TIS': 'GRATIS',
            'BRASILEIRA': 'BRASILEIRA',
            'ESTRANGEIRA': 'ESTRANGEIRA'
        }, regex=True)
        
        print("✅ Dados categóricos limpos e padronizados")

    def validate_data(self):
        """Valida consistência dos dados"""
        print("🔍 Validando consistência dos dados...")
        
        issues = []
        
        # Validar anos (devem ser 2025 baseado na análise)
        if 'ANO' in self.df.columns:
            unique_years = self.df['ANO'].dropna().unique()
            if len(unique_years) > 1 or (len(unique_years) == 1 and unique_years[0] != 2025):
                issues.append(f"Anos inconsistentes encontrados: {unique_years}")
        
        # Validar meses (1-12)
        if 'MES' in self.df.columns:
            invalid_months = self.df[(self.df['MES'] < 1) | (self.df['MES'] > 12)]['MES'].dropna()
            if len(invalid_months) > 0:
                issues.append(f"Meses inválidos encontrados: {invalid_months.unique()}")
        
        # Validar códigos de aeroporto (devem ter 4 caracteres)
        airport_cols = ['AEROPORTO DE ORIGEM (SIGLA)', 'AEROPORTO DE DESTINO (SIGLA)']
        for col in airport_cols:
            if col in self.df.columns:
                invalid_codes = self.df[
                    (self.df[col].notna()) & 
                    (self.df[col].str.len() != 4)
                ][col].unique()
                if len(invalid_codes) > 0:
                    issues.append(f"Códigos de aeroporto inválidos em {col}: {invalid_codes[:5]}")
        
        # Validar valores negativos em colunas que não deveriam ter
        positive_only_cols = ['PASSAGEIROS PAGOS', 'PASSAGEIROS GRATIS', 'DECOLAGENS']
        for col in positive_only_cols:
            if col in self.df.columns:
                negative_count = len(self.df[self.df[col] < 0])
                if negative_count > 0:
                    issues.append(f"Valores negativos em {col}: {negative_count} registros")
        
        if issues:
            print("⚠️  Problemas encontrados:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ Validação concluída sem problemas críticos")
        
        return len(issues) == 0

    def create_summary_report(self):
        """Cria relatório resumido dos dados após tratamento"""
        print("\n📋 RELATÓRIO DE TRATAMENTO DOS DADOS")
        print("=" * 50)
        
        print(f"📊 Registros totais: {len(self.df):,}")
        print(f"📊 Colunas totais: {len(self.df.columns)}")
        
        print(f"\n📅 Período dos dados:")
        if 'ANO' in self.df.columns and 'MES' in self.df.columns:
            anos = self.df['ANO'].dropna().unique()
            meses = self.df['MES'].dropna().unique()
            print(f"   Anos: {sorted(anos)}")
            print(f"   Meses: {sorted(meses)}")
        
        print(f"\n✈️  Empresas únicas: {self.df['EMPRESA (SIGLA)'].nunique()}")
        print(f"🛫 Aeroportos origem únicos: {self.df['AEROPORTO DE ORIGEM (SIGLA)'].nunique()}")
        print(f"🛬 Aeroportos destino únicos: {self.df['AEROPORTO DE DESTINO (SIGLA)'].nunique()}")
        
        print(f"\n📈 Distribuição por natureza:")
        if 'NATUREZA' in self.df.columns:
            natureza_counts = self.df['NATUREZA'].value_counts()
            for nat, count in natureza_counts.items():
                pct = (count / len(self.df)) * 100
                print(f"   {nat}: {count:,} ({pct:.1f}%)")
        
        print(f"\n📊 Valores ausentes por coluna (top 10):")
        missing_data = self.df.isnull().sum().sort_values(ascending=False)
        for col, missing_count in missing_data.head(10).items():
            if missing_count > 0:
                pct = (missing_count / len(self.df)) * 100
                print(f"   {col}: {missing_count:,} ({pct:.1f}%)")

    def save_to_csv(self, output_path=None):
        """Salva o CSV tratado"""
        if output_path is None:
            # Criar nome baseado no arquivo original
            original_path = Path(self.csv_file_path)
            output_path = original_path.parent / f"{original_path.stem}_tratado{original_path.suffix}"
        
        print(f"\n💾 Salvando CSV tratado: {output_path}")
        
        try:
            self.df.to_csv(
                output_path, 
                sep=';', 
                index=False, 
                encoding='utf-8',
                decimal='.'  # Garantir que decimais usem ponto
            )
            
            print(f"✅ CSV tratado salvo: {output_path}")
            print(f"✅ {len(self.df)} registros exportados")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar CSV: {e}")
            return False

    def process_all(self, save_to_db=True, save_to_csv=True, table_name='voos_anac', csv_output_path=None, min_completeness=70):
        """Executa todo o pipeline de tratamento de dados"""
        print("🚀 INICIANDO PROCESSAMENTO DOS DADOS ANAC")
        print("=" * 50)
        
        # 1. Carregar dados
        if not self.load_data():
            return False
        
        # 2. Remover registros com muitos dados faltantes
        self.remove_low_quality_records(min_completeness)
        
        # 3. Corrigir nomes das colunas
        self.fix_column_names()
        
        # 4. Tratar dados numéricos
        self.clean_numeric_data()
        
        # 5. Tratar dados categóricos
        self.clean_categorical_data()
        
        # 6. Validar dados
        self.validate_data()
        
        # 7. Gerar relatório
        self.create_summary_report()
        
        # 8. Salvar CSV tratado (opcional)
        if save_to_csv:
            csv_success = self.save_to_csv(csv_output_path)
            if not csv_success:
                print("⚠️  Falha ao salvar CSV, mas continuando...")
        
        print(f"\n🎉 PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        return True

    def get_processed_dataframe(self):
        """Retorna o DataFrame processado"""
        return self.df.copy() if self.df is not None else None


# EXEMPLO DE USO
if __name__ == "__main__":
    # Inicializar o processador
    processor = ANACDataProcessor(
        csv_file_path='resumo_anual_2025.csv',
    )
 
    success = processor.process_all(
        save_to_csv=True, 
        save_to_db=False,
        min_completeness=70  # Remove linhas com menos de 70% de dados
    )
