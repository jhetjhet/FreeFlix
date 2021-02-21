const router = require('express').Router();
const UploadMiddleWare = require('../middlewares/upload-middleware');
const Path = require('path');

var uploadMiddleWare = new UploadMiddleWare(Path.join(__dirname, '../media'), 3145728);

router.get('/:chunkid/', uploadMiddleWare.continue());
router.post('/:chunkid/', uploadMiddleWare.upload(), function(req, res){
    return res.json({uploaded: req.chunk.uploaded});
});
router.post('/complete/:chunkid/', uploadMiddleWare.complete(), function(req, res){
    return res.json({uploaded: req.chunk.uploaded});
});
router.delete('/cancel/:chunkid/', uploadMiddleWare.cancel());

module.exports = router;