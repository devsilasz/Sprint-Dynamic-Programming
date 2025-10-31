import sys
from typing import List, Dict, Tuple
import random

class ControleEstoque:
    def __init__(self, estoque_inicial: int, custo_armazenamento: float, 
                 custo_falta: float, custo_pedido: float, demanda_maxima: int):
        self.estoque_inicial = estoque_inicial
        self.custo_armazenamento = custo_armazenamento
        self.custo_falta = custo_falta
        self.custo_pedido = custo_pedido
        self.demanda_maxima = demanda_maxima
        
    def calcular_demanda_probabilistica(self, periodo: int) -> List[Tuple[int, float]]:
        """Simula demanda probabilística baseada no período"""
        if periodo <= 5:
            return [(10, 0.3), (15, 0.4), (20, 0.3)]
        elif periodo <= 10:
            return [(15, 0.2), (20, 0.5), (25, 0.3)]
        else:
            return [(20, 0.4), (25, 0.4), (30, 0.2)]
    
    def custo_total_periodo(self, estoque_atual: int, pedido: int, demanda_real: int) -> float:
        """Calcula custo total para um período específico"""
        estoque_final = estoque_atual + pedido - demanda_real
        
        custo_armazenamento_total = max(0, estoque_final) * self.custo_armazenamento
        custo_falta_total = max(0, -estoque_final) * self.custo_falta
        custo_pedido_total = pedido * self.custo_pedido if pedido > 0 else 0
        
        return custo_armazenamento_total + custo_falta_total + custo_pedido_total

def pd_recursiva_memorizada(controle: ControleEstoque, periodo: int, estoque_atual: int, 
                           memo: Dict[Tuple[int, int], float]) -> float:
    """Versão recursiva com memorização"""
    if periodo == 0:
        return 0
    
    chave = (periodo, estoque_atual)
    if chave in memo:
        return memo[chave]
    
    demanda_opcoes = controle.calcular_demanda_probabilistica(periodo)
    custo_minimo = float('inf')
    
    for pedido in range(0, 50, 5):
        custo_esperado = 0
        
        for demanda, probabilidade in demanda_opcoes:
            custo_periodo = controle.custo_total_periodo(estoque_atual, pedido, demanda)
            estoque_proximo = estoque_atual + pedido - demanda
            custo_futuro = pd_recursiva_memorizada(controle, periodo - 1, estoque_proximo, memo)
            custo_esperado += probabilidade * (custo_periodo + custo_futuro)
        
        custo_minimo = min(custo_minimo, custo_esperado)
    
    memo[chave] = custo_minimo
    return custo_minimo

def pd_iterativa_bottom_up(controle: ControleEstoque, total_periodos: int) -> float:
    """Versão iterativa bottom-up"""
    dp = {}
    
    for periodo in range(total_periodos + 1):
        for estoque in range(-50, 100):
            if periodo == 0:
                dp[(periodo, estoque)] = 0
            else:
                demanda_opcoes = controle.calcular_demanda_probabilistica(periodo)
                custo_minimo = float('inf')
                
                for pedido in range(0, 50, 5):
                    custo_esperado = 0
                    
                    for demanda, probabilidade in demanda_opcoes:
                        custo_periodo = controle.custo_total_periodo(estoque, pedido, demanda)
                        estoque_proximo = estoque + pedido - demanda
                        
                        if (periodo - 1, estoque_proximo) in dp:
                            custo_futuro = dp[(periodo - 1, estoque_proximo)]
                        else:
                            custo_futuro = 0
                            
                        custo_esperado += probabilidade * (custo_periodo + custo_futuro)
                    
                    custo_minimo = min(custo_minimo, custo_esperado)
                
                dp[(periodo, estoque)] = custo_minimo
    
    return dp[(total_periodos, controle.estoque_inicial)]

def executar_comparacao():
    """Executa ambas as versões e compara os resultados"""
    controle = ControleEstoque(
        estoque_inicial=20,
        custo_armazenamento=2.0,
        custo_falta=10.0,
        custo_pedido=5.0,
        demanda_maxima=30
    )
    
    total_periodos = 12
    memo = {}
    
    print("=== CONTROLE DE ESTOQUE - PROGRAMAÇÃO DINÂMICA ===\n")
    
    print("Parâmetros do problema:")
    print(f"Estoque inicial: {controle.estoque_inicial}")
    print(f"Custo armazenamento: R$ {controle.custo_armazenamento}")
    print(f"Custo falta: R$ {controle.custo_falta}")
    print(f"Custo pedido: R$ {controle.custo_pedido}")
    print(f"Períodos: {total_periodos}\n")
    
    print("Executando versão recursiva com memorização...")
    resultado_recursivo = pd_recursiva_memorizada(controle, total_periodos, 
                                                controle.estoque_inicial, memo)
    
    print("Executando versão iterativa bottom-up...")
    resultado_iterativo = pd_iterativa_bottom_up(controle, total_periodos)
    
    print(f"\nResultado recursivo: R$ {resultado_recursivo:.2f}")
    print(f"Resultado iterativo: R$ {resultado_iterativo:.2f}")
    
    diferenca = abs(resultado_recursivo - resultado_iterativo)
    print(f"Diferença: R$ {diferenca:.2f}")
    
    if diferenca < 0.01:
        print("✓ Ambas as versões produzem resultados idênticos!")
    else:
        print("⚠ Atenção: Há diferença significativa entre os resultados")
    
    print(f"\nEstados visitados na versão recursiva: {len(memo)}")

def simular_cenario_real():
    """Simula um cenário real de controle de estoque"""
    print("\n=== SIMULAÇÃO DE CENÁRIO REAL ===")
    
    controle = ControleEstoque(
        estoque_inicial=25,
        custo_armazenamento=1.5,
        custo_falta=15.0,
        custo_pedido=8.0,
        demanda_maxima=35
    )
    
    memo = {}
    resultado = pd_recursiva_memorizada(controle, 15, controle.estoque_inicial, memo)
    
    print(f"Custo mínimo esperado para 15 períodos: R$ {resultado:.2f}")
    print(f"Estados computados: {len(memo)}")
    
    economia_estimada = resultado * 0.15
    print(f"Economia estimada com otimização: R$ {economia_estimada:.2f}")

if __name__ == "__main__":
    executar_comparacao()
    simular_cenario_real()
