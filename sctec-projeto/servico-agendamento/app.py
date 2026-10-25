# servico de agendamento (o "cerebro") - flask + sqlalchemy
import json
import logging
import os
import time
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy

SERVICO = "servico-agendamento"
COORDENADOR_URL = os.environ.get("COORDENADOR_URL", "http://localhost:3000")
USAR_LOCK = os.environ.get("USAR_LOCK", "true").lower() == "true"   # entrega 2 roda com false
DEMORA_BD = float(os.environ.get("DEMORA_BD", "0.3"))  # simula o tempo de processamento no banco

PASTA = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------ logging
AUDIT = 25  # nivel novo entre INFO e WARNING
logging.addLevelName(AUDIT, "AUDIT")


def agora_utc():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class FormatoUTC(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return iso(datetime.fromtimestamp(record.created, timezone.utc))


log = logging.getLogger(SERVICO)
log.setLevel(logging.INFO)
fmt = FormatoUTC("%(levelname)s:%(asctime)s:%(name)s:%(message)s")
for h in (logging.FileHandler(os.path.join(PASTA, "app.log"), encoding="utf-8"), logging.StreamHandler()):
    h.setFormatter(fmt)
    log.addHandler(h)
log.propagate = False


def auditoria(evento, detalhes):
    log.log(AUDIT, json.dumps({
        "timestamp_utc": iso(agora_utc()),
        "level": "AUDIT",
        "event_type": evento,
        "service": SERVICO,
        "details": detalhes,
    }, ensure_ascii=False))


# ------------------------------------------------------------ banco
app = Flask(__name__)
app.json.ensure_ascii = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(PASTA, "agendamentos.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"timeout": 15}}
db = SQLAlchemy(app)


class Cientista(db.Model):
    __tablename__ = "cientistas"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    instituicao = db.Column(db.String(120))


class Telescopio(db.Model):
    __tablename__ = "telescopios"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), unique=True, nullable=False)
    localizacao = db.Column(db.String(120))


class Agendamento(db.Model):
    __tablename__ = "agendamentos"
    id = db.Column(db.Integer, primary_key=True)
    cientista_id = db.Column(db.Integer, db.ForeignKey("cientistas.id"), nullable=False)
    telescopio_id = db.Column(db.Integer, db.ForeignKey("telescopios.id"), nullable=False)
    horario_inicio_utc = db.Column(db.String(30), nullable=False)
    horario_fim_utc = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="ATIVO")
    criado_em_utc = db.Column(db.String(30), nullable=False)

    telescopio = db.relationship("Telescopio")
    cientista = db.relationship("Cientista")


def links_agendamento(a):
    links = {
        "self": {"href": f"/agendamentos/{a.id}", "method": "GET"},
        "cientista": {"href": f"/cientistas/{a.cientista_id}", "method": "GET"},
        "telescopio": {"href": f"/telescopios/{a.telescopio_id}", "method": "GET"},
    }
    if a.status == "ATIVO":  # so da pra cancelar se ainda estiver ativo
        links["cancelar"] = {"href": f"/agendamentos/{a.id}", "method": "DELETE"}
    return links


def agendamento_json(a):
    return {
        "id": a.id,
        "cientista_id": a.cientista_id,
        "cientista": a.cientista.nome,
        "telescopio_id": a.telescopio_id,
        "telescopio": a.telescopio.nome,
        "horario_inicio_utc": a.horario_inicio_utc,
        "horario_fim_utc": a.horario_fim_utc,
        "status": a.status,
        "criado_em_utc": a.criado_em_utc,
        "_links": links_agendamento(a),
    }


def popular_banco():
    db.create_all()
    if not Telescopio.query.first():
        db.session.add_all([
            Telescopio(nome="Hubble-Acad", localizacao="Orbita baixa"),
            Telescopio(nome="Webb-Acad", localizacao="Ponto L2"),
        ])
        db.session.add_all([
            Cientista(nome="Marie Curie", email="marie@sctec.edu", instituicao="Sorbonne"),
            Cientista(nome="Carl Sagan", email="carl@sctec.edu", instituicao="Cornell"),
            Cientista(nome="Neil Tyson", email="neil@sctec.edu", instituicao="Hayden"),
        ])
        db.session.commit()


def erro(status, codigo, msg):
    return jsonify({"error": codigo, "message": msg}), status


# ------------------------------------------------------------ lock (coordenador)
def pedir_lock(recurso):
    log.info(f"Tentando adquirir lock para o recurso {recurso}")
    r = requests.post(f"{COORDENADOR_URL}/lock", json={"recurso": recurso}, timeout=5)
    if r.status_code == 200:
        log.info(f"Lock adquirido com sucesso para o recurso {recurso}")
        return True
    log.info(f"Falha ao adquirir lock para o recurso {recurso}, recurso ocupado")
    return False


def liberar_lock(recurso):
    log.info(f"Liberando lock para o recurso {recurso}")
    requests.post(f"{COORDENADOR_URL}/unlock", json={"recurso": recurso}, timeout=5)


# ------------------------------------------------------------ rotas
@app.route("/")
def pagina():
    return send_from_directory(PASTA, "index.html")


@app.route("/time", methods=["GET"])
def tempo():
    log.info(f"Requisição recebida em GET /time do IP {request.remote_addr}")
    return jsonify({"timestamp_utc": iso(agora_utc()), "epoch_ms": int(time.time() * 1000)})


@app.route("/cientistas", methods=["GET"])
def listar_cientistas():
    return jsonify([{"id": c.id, "nome": c.nome, "email": c.email, "instituicao": c.instituicao,
                     "_links": {"self": {"href": f"/cientistas/{c.id}", "method": "GET"}}}
                    for c in Cientista.query.all()])


@app.route("/cientistas/<int:cid>", methods=["GET"])
def ver_cientista(cid):
    c = db.session.get(Cientista, cid)
    if not c:
        return erro(404, "NOT_FOUND", "Cientista não encontrado")
    return jsonify({"id": c.id, "nome": c.nome, "email": c.email, "instituicao": c.instituicao,
                    "_links": {"self": {"href": f"/cientistas/{c.id}", "method": "GET"},
                               "agendamentos": {"href": f"/agendamentos?cientista_id={c.id}", "method": "GET"}}})


@app.route("/telescopios", methods=["GET"])
def listar_telescopios():
    return jsonify([{"id": t.id, "nome": t.nome, "localizacao": t.localizacao,
                     "_links": {"self": {"href": f"/telescopios/{t.id}", "method": "GET"}}}
                    for t in Telescopio.query.all()])


@app.route("/telescopios/<int:tid>", methods=["GET"])
def ver_telescopio(tid):
    t = db.session.get(Telescopio, tid)
    if not t:
        return erro(404, "NOT_FOUND", "Telescópio não encontrado")
    return jsonify({"id": t.id, "nome": t.nome, "localizacao": t.localizacao,
                    "_links": {"self": {"href": f"/telescopios/{t.id}", "method": "GET"}}})


@app.route("/agendamentos", methods=["GET"])
def listar_agendamentos():
    q = Agendamento.query
    if request.args.get("cientista_id"):
        q = q.filter_by(cientista_id=int(request.args["cientista_id"]))
    return jsonify([agendamento_json(a) for a in q.order_by(Agendamento.id).all()])


@app.route("/agendamentos/<int:aid>", methods=["GET"])
def ver_agendamento(aid):
    a = db.session.get(Agendamento, aid)
    if not a:
        return erro(404, "NOT_FOUND", "Agendamento não encontrado")
    return jsonify(agendamento_json(a))


@app.route("/agendamentos", methods=["POST"])
def criar_agendamento():
    dados = request.get_json(silent=True) or {}
    try:
        cientista_id = int(dados["cientista_id"])
        telescopio_id = int(dados["telescopio_id"])
        inicio = dados["horario_inicio_utc"]
        fim = dados.get("horario_fim_utc") or inicio
    except (KeyError, TypeError, ValueError):
        return erro(400, "INVALID_DATA", "Envie cientista_id, telescopio_id e horario_inicio_utc")

    tel = db.session.get(Telescopio, telescopio_id)
    if not tel or not db.session.get(Cientista, cientista_id):
        return erro(404, "NOT_FOUND", "Cientista ou telescópio não existe")

    recurso = f"{tel.nome}_{inicio}"
    log.info(f"Requisição recebida para POST /agendamentos (recurso {recurso})")

    tem_lock = False
    if USAR_LOCK:
        try:
            tem_lock = pedir_lock(recurso)
        except requests.RequestException:
            log.error("Coordenador fora do ar")
            return erro(503, "COORDINATOR_UNAVAILABLE", "Serviço coordenador indisponível")
        if not tem_lock:
            return erro(409, "CONFLICT", f"O recurso {recurso} está ocupado por outro pedido")

    try:
        log.info("Iniciando verificação de conflito no BD")
        conflito = Agendamento.query.filter_by(telescopio_id=telescopio_id, horario_inicio_utc=inicio,
                                               status="ATIVO").first()
        time.sleep(DEMORA_BD)  # pausa de proposito pra janela da condicao de corrida ficar visivel
        if conflito:
            log.info(f"Horário {inicio} já está agendado (agendamento {conflito.id})")
            return erro(409, "CONFLICT", "Já existe agendamento para esse telescópio nesse horário")

        log.info("Salvando novo agendamento no BD")
        a = Agendamento(cientista_id=cientista_id, telescopio_id=telescopio_id, horario_inicio_utc=inicio,
                        horario_fim_utc=fim, status="ATIVO", criado_em_utc=iso(agora_utc()))
        db.session.add(a)
        db.session.commit()

        auditoria("AGENDAMENTO_CRIADO", {"agendamento_id": a.id, "cientista_id": cientista_id,
                                         "telescopio": tel.nome, "horario_inicio_utc": inicio,
                                         "timestamp_cliente_utc": dados.get("timestamp_cliente_utc")})
        return jsonify(agendamento_json(a)), 201
    finally:
        if tem_lock:
            liberar_lock(recurso)


@app.route("/agendamentos/<int:aid>", methods=["DELETE"])
def cancelar_agendamento(aid):
    log.info(f"Requisição recebida para DELETE /agendamentos/{aid}")
    a = db.session.get(Agendamento, aid)
    if not a:
        return erro(404, "NOT_FOUND", "Agendamento não encontrado")
    if a.status == "CANCELADO":
        return erro(409, "ALREADY_CANCELLED", "Esse agendamento já foi cancelado")

    a.status = "CANCELADO"
    db.session.commit()
    auditoria("AGENDAMENTO_CANCELADO", {"agendamento_id": a.id, "cientista_id": a.cientista_id,
                                        "telescopio": a.telescopio.nome, "horario_inicio_utc": a.horario_inicio_utc})
    return jsonify(agendamento_json(a))


with app.app_context():
    popular_banco()

if __name__ == "__main__":
    log.info(f"Subindo {SERVICO} (USAR_LOCK={USAR_LOCK}, coordenador={COORDENADOR_URL})")
    app.run(host="0.0.0.0", port=5000, threaded=True)
