const express = require('express');
const app = express();
const PORT = 3000;

app.use(express.json());

app.get('/api/data', (req, res) => {
  res.json({
    "mensagem": "Olá do Node.js!",
    "status": "sucesso",
    "tecnologia": "JavaScript"
  });
});

app.listen(PORT, () => {
  console.log(`Servidor Node rodando na porta ${PORT}`);
});
