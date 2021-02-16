const router = require('express').Router();
const fs = require('fs');
const path = require('path');
const Chunk = require('../database/models/Chunk');

const BASE_PATH = './media/';
const CONTENT_RANGE_RE = 'bytes\\s+(?<start>\\d+)-(?<end>\\d+)/(?<total>\\d+)';

module.exports = function (onUpload, chunkSize=(1048576 * 3)){
    router.post('*', (req, res, next) => {
        var contentRange = req.get('content-range');
        if(!contentRange) return res.status(400).send('Header must include content-range.');
    
        const m = contentRange.match(CONTENT_RANGE_RE);
    
        if(!m) return res.status(400).send('Invalid content-range format');
    
        const start = parseInt(m.groups.start);
        const end = parseInt(m.groups.end);
        const total = parseInt(m.groups.total);

        if((end - start) != chunkSize && (total - end) > chunkSize) return res.status(400).send('Chunk size dont match');

        req.contentRange = {start, end, total};
    
        next();
    });
    
    router.get('/:chunkID/:fileName/', async (req, res) => {
        var chunk = await Chunk.findByPk(req.params.chunkID);
        if(chunk)
            return res.send({uploaded: chunk.uploaded});
        res.status(404).send('Chunk not found');
    });
    
    router.post('/:chunkID/:fileName/', async (req, res) => {
        var chunkID = req.params.chunkID;
        var [chunk, created] = await Chunk.findOrCreate({
            where: {id: chunkID},
            defaults: {
                id: chunkID,
                totalSize: req.contentRange.total,
                path: path.join(BASE_PATH, chunkID+path.extname(req.params.fileName))
            }
        });
    
        if(chunk.uploaded !== req.contentRange.start || chunk.totalSize !== req.contentRange.total)
            return res.status(400).send('Header dont match.');
    
        var fileStream = fs.createWriteStream(chunk.path, {flags: created ? 'w' : 'a'});
        var bytesSizeWriten = 0;
        req.on('data', (dataChunk) => {
            bytesSizeWriten += dataChunk.length;
        });
    
        req.pipe(fileStream);
    
        fileStream.on('close', async () => {
            await chunk.increment('uploaded', {by: bytesSizeWriten});
            onUpload({chunk, completed: false, canceled: false}, null); // cb
            res.json({uploaded: chunk.uploaded + bytesSizeWriten});
        });
    
        fileStream.on('error', async (err) => {
            console.log(err);
            res.status(500).end();
            onUpload({chunk, completed: false, canceled: false}, err);
        });
    });
    
    router.post('/complete/:chunkID/:fileName/', async (req, res) => {
        try {
            var chunk = await Chunk.findByPk(req.params.chunkID);
            var fileStream = fs.createWriteStream(chunk.path, {flags: 'a'});
            req.pipe(fileStream);
            fileStream.on('close', async () => {
                await chunk.destroy();
                res.status(200).end();
                onUpload({chunk, completed: true, canceled: false}, null);
            });
            fileStream.on('error', (err) => {
                res.status(500).end();
                onUpload({chunk, completed: false, canceled: false}, err);
            });
        } catch (error) {
            res.status(404).send('Chunk not exist');
        }
    });
    
    router.delete('/cancel/:chunkID/:fileName/', async (req, res) => {
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

    return router
};