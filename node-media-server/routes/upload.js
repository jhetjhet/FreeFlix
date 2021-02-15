const router = require('express').Router();
const fs = require('fs');
const path = require('path');
const Chunk = require('../database/models/Chunk');

const DEFAULT_CHUNK_SIZE = 1024 * 1024;
const BASE_PATH = './media/';
const CONTENT_RANGE_RE = 'bytes\\s+(?<start>\\d+)-(?<end>\\d+)/(?<total>\\d+)';

router.post('*', (req, res, next) => {
    var contentRange = req.get('content-range');
    if(!contentRange) return res.status(400).send('Header must include content-range.');

    var m = contentRange.match(CONTENT_RANGE_RE);

    if(!m) return res.status(400).send('Invalid content-range format');

    var start = parseInt(m.groups.start);
    var end = parseInt(m.groups.end);
    var total = parseInt(m.groups.total);

    req.contentRange = {start, end, total};

    next();
});

router.get('/:chunkID/', async (req, res) => {
    var chunk = await Chunk.findByPk(req.params.chunkID);
    if(chunk){
        res.send({uploaded: chunk.uploaded});
    }else
        res.status(404).send('Chunk not found');
});

router.post('/:chunkID', async (req, res) => {
    try {
        var chunkID = req.params.chunkID;
        var [chunk, created] = await Chunk.findOrCreate({
            where: {id: chunkID},
            defaults: {
                id: chunkID,
                totalSize: req.contentRange.total,
                path: path.join(BASE_PATH, chunkID)
            }
        });

        if(chunk.uploaded !== req.contentRange.start || chunk.totalSize !== req.contentRange.total)
            return res.status(400).send('Headers dont match.');

        var fileStream = fs.createWriteStream(chunk.path, {flags: created ? 'w' : 'a'});
        var bytesSizeWriten = 0;
        req.on('data', (dataChunk) => {
            bytesSizeWriten += dataChunk.length;
        });

        req.pipe(fileStream);

        fileStream.on('close', async () => {
            await chunk.increment('uploaded', {by: bytesSizeWriten});
            res.json({uploaded: chunk.uploaded + bytesSizeWriten});
        });

        fileStream.on('error', async (err) => {
            console.log(err);
            res.status(500).end();
        });
    } catch (error) {
        console.log(error);
        res.status(500).end();
    }
});

router.post('/complete/:chunkID', async (req, res) => {
    try {
        var chunk = await Chunk.findByPk(req.params.chunkID);
        var fileStream = fs.createWriteStream(chunk.path, {flags: 'a'});
        req.pipe(fileStream);
        fileStream.on('close', async () => {
            await chunk.destroy();
            res.status(200).end();
        });
        fileStream.on('error', (err) => {
            res.status(500).end();
        });
    } catch (error) {
        res.status(404).send('Chunk not exist');
    }
});

router.delete('/cancel/:chunkID', async (req, res) => {
    try {
        var chunk = await Chunk.findByPk(req.params.chunkID);
        fs.unlink(chunk.path, async (err) => {
            if(err)
                res.status(500).end();
            else{
                await chunk.destroy();
                res.status(200).end();
            }
        });
    } catch (error) {
        res.status(404).end();
    }
});

module.exports = router;