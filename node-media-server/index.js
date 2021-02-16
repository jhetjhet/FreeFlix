const express = require('express');
const cors = require('cors');
const Chunk = require('./database/models/Chunk');

const uploadRoutes = require('./routes/upload');

// Chunk.sync({force: true});
// console.log('YEYYYYY !!');

const app = express();

app.use(cors({origin: '*'}));

app.use('/upload', uploadRoutes(
    ({chunk, completed, canceled}, err) => {
        console.log(chunk.uploaded);
        if(completed){
            console.log(chunk.path);
            console.log(chunk.uploaded);
            console.log(chunk.totalSize);
        }
    }
));

app.listen(8080, () => {
    console.log('Server running...');
});
