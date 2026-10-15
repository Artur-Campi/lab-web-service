"""Exercício 3: monitoramento genérico (sem lógica específica por linguagem)."""
import requests


def verificar_status(urls):
    for url in urls:
        try:
            dados = requests.get(url, timeout=5).json()
            print(f"[{dados['status'].upper()}] {dados['service']:<14} | {dados['timestamp']} | {url}")
        except requests.exceptions.RequestException:
            print(f"[OFFLINE] {'?':<14} | {'-':<24} | {url}")


if __name__ == "__main__":
    verificar_status(["http://localhost:5000/status", "http://localhost:3000/status"])
