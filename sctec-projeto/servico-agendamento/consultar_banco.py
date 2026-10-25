# mostra o que tem na tabela de agendamentos (direto no sqlite)
import os
import sqlite3

banco = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agendamentos.db")
con = sqlite3.connect(banco)
linhas = con.execute("""
    select a.id, c.nome, t.nome, a.horario_inicio_utc, a.status, a.criado_em_utc
    from agendamentos a join cientistas c on c.id = a.cientista_id join telescopios t on t.id = a.telescopio_id
    order by a.id""").fetchall()
print(f"{'id':>3} | {'cientista':<12} | {'telescopio':<11} | {'horario':<20} | {'status':<9} | criado_em")
print("-" * 90)
for l in linhas:
    print(f"{l[0]:>3} | {l[1]:<12} | {l[2]:<11} | {l[3]:<20} | {l[4]:<9} | {l[5]}")
print(f"\ntotal: {len(linhas)} registros")
