const express = require('express');
const cors = require('cors');
const Chunk = require('./database/models/Chunk');
const uploadRouter = require('./routes/upload');

// Chunk.sync({force: true});
// console.log('YEYYYYY !!');

const app = express();

app.use(cors({origin: '*'}));

app.use('/upload', uploadRouter);

app.listen(8080, () => {
    console.log('Server running...');
});