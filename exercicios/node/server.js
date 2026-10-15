/*
 * Servidor Node.js/Express (porta 3000) - base de dados de ESTOQUE.
 *
 * Exercícios atendidos:
 *   Ex. 2 -> GET  /api/full-info/:id  (proxy: Node consulta o Flask)
 *   Ex. 3 -> GET  /status             (contrato padronizado)
 *   Ex. 4 -> POST /cadastrar          (distribui o cadastro para o Flask)
 *   Ex. 5 -> validação de ID (400 INVALID_ID)
 */
const express = require('express');

const app = express();
const PORT = 3000;
const FLASK_URL = process.env.FLASK_URL || 'http://localhost:5000';

app.use(express.json());

// Base de estoque (preparação dos servidores)
const produtos_estoque = {
  '1': { nome: 'Dell XPS 13', estoque: 10 },
  '2': { nome: 'Monitor LG 29', estoque: 5 },
};

// Ex. 4: produtos cadastrados pelo fluxo distribuído
const produtos_comerciais = {};

// ------------------------------------------------------------- utilitários
function idValido(valor) {
  // Ex. 5: apenas dígitos e maior que zero
  return /^\d+$/.test(String(valor)) && Number(valor) > 0;
}

function erroIdInvalido(res) {
  return res.status(400).json({
    error: 'INVALID_ID',
    message: 'O ID deve ser um inteiro positivo',
  });
}

function buscarProduto(id) {
  return produtos_estoque[id] || produtos_comerciais[id];
}

// Middleware: valida qualquer parâmetro :id antes de processar a rota
app.param('id', (req, res, next, id) => {
  if (!idValido(id)) return erroIdInvalido(res);
  req.params.id = String(Number(id)); // normaliza "01" -> "1"
  next();
});

// ------------------------------------------------------------------- rotas
app.get('/api/data', (req, res) => {
  res.json({ mensagem: 'Olá do Node.js!', status: 'sucesso', tecnologia: 'JavaScript' });
});

app.get('/estoque/:id', (req, res) => {
  const produto = buscarProduto(req.params.id);
  if (!produto) {
    return res.status(404).json({ error: 'NOT_FOUND', message: `Produto ${req.params.id} não encontrado` });
  }
  res.json({ id: req.params.id, ...produto });
});

// Ex. 2: o Node atua como CLIENTE do Flask
app.get('/api/full-info/:id', async (req, res) => {
  const { id } = req.params;
  const estoque = buscarProduto(id);
  if (!estoque) {
    return res.status(404).json({ error: 'NOT_FOUND', message: `Produto ${id} não encontrado no estoque` });
  }

  try {
    console.log(`[PROXY] Consultando Flask: ${FLASK_URL}/detalhes/${id}`);
    const resposta = await fetch(`${FLASK_URL}/detalhes/${id}`);
    const fiscal = await resposta.json();

    if (!resposta.ok) return res.status(resposta.status).json(fiscal);

    res.json({ id, nome: estoque.nome, estoque: estoque.estoque, preco: fiscal.preco, categoria: fiscal.categoria });
  } catch (erro) {
    console.error('[PROXY] Falha ao contatar o Flask:', erro.message);
    res.status(502).json({ error: 'BAD_GATEWAY', message: 'Serviço fiscal (Flask) indisponível' });
  }
});

// Ex. 3: mesmo contrato do Flask
app.get('/status', (req, res) => {
  res.json({ service: 'node-estoque', status: 'online', timestamp: new Date().toISOString() });
});

// Ex. 4: cadastro com persistência distribuída
app.post('/cadastrar', async (req, res) => {
  const { id, nome, estoque, preco_base, categoria } = req.body || {};

  if (!idValido(id)) return erroIdInvalido(res);
  if (typeof nome !== 'string' || !Number.isInteger(estoque) || typeof preco_base !== 'number' || typeof categoria !== 'string') {
    return res.status(400).json({
      error: 'INVALID_DATA',
      message: 'Campos obrigatórios: nome (texto), estoque (inteiro), preco_base (número), categoria (texto)',
    });
  }

  // 1. Tratamento: nome em CAIXA ALTA
  const nomeTratado = nome.toUpperCase();
  const produtoId = String(Number(id));

  try {
    // 2. Sincronização: envia apenas a parte fiscal para o Flask
    const resposta = await fetch(`${FLASK_URL}/fiscal/cadastrar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: produtoId, preco_base, categoria }),
    });
    const fiscal = await resposta.json();

    if (resposta.status !== 201) {
      console.log(`[CADASTRO] Flask recusou o produto ${produtoId} (HTTP ${resposta.status})`);
      return res.status(resposta.status).json(fiscal);
    }

    // 3. Persistência comercial (somente após o 201 do Flask)
    produtos_comerciais[produtoId] = { nome: nomeTratado, estoque };
    console.log(`[CADASTRO] Produto ${produtoId} salvo em produtos_comerciais:`, produtos_comerciais[produtoId]);

    res.status(201).json({
      mensagem: 'Produto cadastrado com sucesso',
      comercial: { id: produtoId, ...produtos_comerciais[produtoId] },
      fiscal,
    });
  } catch (erro) {
    console.error('[CADASTRO] Falha ao contatar o Flask:', erro.message);
    res.status(502).json({ error: 'BAD_GATEWAY', message: 'Serviço fiscal (Flask) indisponível' });
  }
});

// Rota auxiliar para conferir o dicionário produtos_comerciais
app.get('/comerciais', (req, res) => res.json(produtos_comerciais));

app.listen(PORT, () => {
  console.log(`Servidor Node (estoque) rodando na porta ${PORT}`);
});
