const express = require('express');
const os = require('os');

const app = express();
const port = 8080;

app.get('/', (req, res) => {
  const message = `<h1>Ping Pod API</h1><br>
	/health<br>
	/hostname<br>
	/cpu-load<br>
	/memory-load`;
  res.status(200).send(message);
});

app.get('/health', (req, res) => {
  res.status(200).send('API está funcionando!');
});

app.get('/hostname', (req, res) => {
  res.status(200).send(`Nome do host: ${os.hostname()}`);
});

app.get('/cpu-load', (req, res) => {
  let result = 0;
  for (let i = 0; i < 1e7; i++) {
    result += Math.random * Math.random();
  }
  res.status(200).send(`Carga processada`);
});

app.get('/memory-load', (req, res) => {
  let memoryLoad = [];
  const size = 100000; 

  try {
    for (let i = 0; i < size; i++) {
      memoryLoad.push(new Array(1000).fill(0));
    }
    res.status(200).send(`Carga de memória criada com ${size} arrays.`);
  } catch (error) {
    res.status(500).send('Erro ao criar carga de memória: ' + error.message);
  }
});

app.listen(port, () => {
  console.log(`Servidor rodando na porta ${port}`);
});
