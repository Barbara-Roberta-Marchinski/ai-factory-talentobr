import os
import time

# Configurações da Política de Retenção (LGPD)
DIRETORIO_CVS = "data/cvs-exemplos"
TEMPO_RETENCAO_MESES = 6
SEGUNDOS_POR_MES = 30 * 24 * 60 * 60

def executar_limpeza_lgpd():
    """
    Varre o diretório de currículos e aplica a exclusão física irreversível 
    para arquivos que ultrapassaram o tempo de retenção estipulado.
    """
    print("Iniciando rotina de exclusão de dados (Compliance LGPD)...")
    agora = time.time()
    limite_tempo = agora - (TEMPO_RETENCAO_MESES * SEGUNDOS_POR_MES)

    if not os.path.exists(DIRETORIO_CVS):
        print(f"Diretório {DIRETORIO_CVS} não encontrado. Nenhuma ação necessária.")
        return

    arquivos_apagados = 0
    for filename in os.listdir(DIRETORIO_CVS):
        file_path = os.path.join(DIRETORIO_CVS, filename)
        
        # Ignora arquivos de sistema e documentação
        if filename in ["AVISO-DADOS-SINTETICOS.md", ".gitkeep"] or filename.startswith("."):
            continue
            
        if os.path.isfile(file_path):
            data_modificacao = os.path.getmtime(file_path)
            
            # Aplica a exclusão se o arquivo for mais velho que o limite de retenção
            if data_modificacao < limite_tempo:
                try:
                    os.remove(file_path)
                    print(f"[EXCLUÍDO] {filename} (Retenção de {TEMPO_RETENCAO_MESES} meses expirada)")
                    arquivos_apagados += 1
                except Exception as e:
                    print(f"Erro ao excluir {filename}: {e}")
                    
    print(f"Rotina concluída com sucesso. Total de registros apagados: {arquivos_apagados}")

if __name__ == "__main__":
    executar_limpeza_lgpd()