// servico coordenador (o "porteiro") - controla os locks
const express = require('express');

const app = express();
const PORT = 3000;
app.use(express.json());

// recurso -> momento em que foi travado
const locks = new Map();

function log(msg) {
  console.log(`[${new Date().toISOString()}] servico-coordenador: ${msg}`);
}

app.post('/lock', (req, res) => {
  const recurso = req.body && req.body.recurso;
  if (!recurso) return res.status(400).json({ error: 'INVALID_DATA', message: 'Informe o recurso' });

  log(`Recebido pedido de lock para recurso ${recurso}`);
  if (locks.has(recurso)) {
    log(`Recurso ${recurso} já em uso, negando lock.`);
    return res.status(409).json({ status: 'negado', recurso });
  }
  // node roda o js numa thread so, entao o has + set acima nao intercala com outro pedido
  locks.set(recurso, new Date().toISOString());
  log(`Lock concedido para recurso ${recurso}`);
  res.status(200).json({ status: 'concedido', recurso });
});

app.post('/unlock', (req, res) => {
  const recurso = req.body && req.body.recurso;
  log(`Recebido pedido de unlock para recurso ${recurso}`);
  if (!locks.delete(recurso)) {
    return res.status(404).json({ status: 'nao_estava_travado', recurso });
  }
  log(`Lock para o recurso ${recurso} liberado.`);
  res.json({ status: 'liberado', recurso });
});

// so pra ver o que esta travado
app.get('/locks', (req, res) => res.json(Object.fromEntries(locks)));

app.listen(PORT, () => log(`rodando na porta ${PORT}`));
