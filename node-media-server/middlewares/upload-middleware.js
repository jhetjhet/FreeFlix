const Busboy = require('busboy');
const Chunk = require('../database/models/Chunk');
const Path = require('path');
const fs = require('fs');

const CONTENT_RANGE_RE = 'bytes\\s+(?<start>\\d+)-(?<end>\\d+)/(?<total>\\d+)';

function ChunkUpload(saveto, chunkSize){
    this.saveto = saveto;
    this.chunkSize = chunkSize;

    this.contentRangeMiddleWare = function(req, res, next){
        const contentRange = req.get('content-range');
        if(!contentRange) 
            return res.status(400).send("No content-range found in the header.");
        const m = contentRange.match(CONTENT_RANGE_RE);

        if(!m)
            return res.status(400).send("Invalid content-range header.");

        const start = parseInt(m.groups.start);
        const end = parseInt(m.groups.end);
        const total = parseInt(m.groups.total);

        if((end - start) != chunkSize && (total - end) > chunkSize)
            return res.status(400).send("content-range dont match the chunk size.");
        
        req.contentRange = {start, end, total};
        
        next();
    }

    this.busboyMiddleWare = function(req, res, next){
        const busboy = new Busboy({
            headers: req.headers,
            limits: {
                files: 1,
                fileSize: this.chunkSize,
            }
        });
        const chunkid = req.params.chunkid;

        Chunk.findOrCreate({
            where: {id: chunkid},
            defaults: {
                id: chunkid,
                totalSize: req.contentRange.total,
            }
        }).then(([chunk, created]) => {
            var fields = {};
        
            busboy.on('field', (fieldname, val, fieldnameTruncated, valTruncated, encoding, mimetype) => {
                fields[fieldname] = val;
            });
        
            if(!created && chunk.path){
                busboy.on('file', (fieldname, file, filename, encoding, mimetype) => {
                    if(fieldname != "chunk")
                        return res.status(404).end();
                    
                    let fileStream = fs.createWriteStream(chunk.path, {flags: chunk.stats ? 'a' : 'w'});
                    file.pipe(fileStream);

                    file.on('end', () => {fileStream.close()});
                    file.on('error', (err) => {fileStream.close()});
                    // fileStream.on('error', () => {fileStream.close()});
                });
            }
        
            busboy.on('finish', () => {
                if(!fields.filename)
                    return res.status(404).json({filename: "This field is required."});

                req.fields = fields;

                if(!chunk.path){
                    chunk.path = Path.join(saveto, `${chunk.id}-${fields.filename}`);
                    chunk.save().then((chunk) => {
                        req.chunk = chunk;
                        return next();
                    }).catch((err) => {
                        return res.status(500).end();
                    });
                }else{
                    chunk.updateStats();
                    req.chunk = chunk;
                    return next();
                }
            });
        
            req.pipe(busboy);

        }).catch((err) => {
            return res.status(404).end("File does not exists.");
        });
    }

    this.middlewares = [this.contentRangeMiddleWare, this.busboyMiddleWare]
}

ChunkUpload.prototype.continue = function(){
    return [function(req, res, next){
        Chunk.findByPk(req.params.chunkid).then((chunk) => {
            return res.json({uploaded: chunk.uploaded});
        }).catch((err) => {
            return res.status(404).end();
        });
    }];
}

ChunkUpload.prototype.upload = function(){
    return [...this.middlewares];
}

ChunkUpload.prototype.complete = function(){
    return [...this.middlewares, function(req, res, next){
        req.chunk.destroy().then(() => {
            return next();
        }).catch((err) => {
            return res.status(500).end();
        });
}];
}

ChunkUpload.prototype.cancel = function(){
    return [function(req, res){
        Chunk.findByPk(req.params.chunkid).then((chunk) => {
            fs.unlink(chunk.path, (err) => {
                if(err)
                    return res.status(404).end();
                chunk.destroy().then(() => {
                    res.status(200).end();
                }).catch((err) => {
                    res.status(500).end();
                })
            });
        }).catch((err) => {
            return res.status(404).end();
        });
}];
}

module.exports = ChunkUpload;