import {useState, useEffect} from 'react';
import {v4 as uuidv4} from 'uuid';
import axios from 'axios';
import cookie from 'react-cookies';

const defaultChunkSize = (1024 * 1024);

const stringToHash = (str) => {
    var hash, chr;
    for(var i = 0; i < str.length; i++){
        chr = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + chr;
        hash |= 0;
    }
    return hash;
}

const FileUploader = ({children, _file, onFinish}) => {
    // upload
    const [bytesUploaded, setBytesUploaded] = useState(0);
    const [fileExt, setFileExt] = useState(undefined);
    const [chunkID, setChunkID] = useState(undefined);
    const [fileName, setFileName] = useState(undefined);
    const [file, setFile] = useState(null);

    // state
    const [pause, setPause] = useState(true);
    const [cancel, setCancel] = useState(false);

    useEffect(() => {
        if(file !== _file){
            setFile(_file);
            init(_file);
        }else{
            if(!pause){
                if(cancel) cancelUpload();
                else{
                    const remainSize = file.size - bytesUploaded;
                    if(remainSize > 0) prepareChunk();
                }
            }
        }
    }, [bytesUploaded, pause, file, _file]);

    const init = async (file) => {
        var _fileName = stringToHash(`${file.name}-${file.lastModified}-${file.size}`);
        var _chunkID = cookie.load(_fileName);
        if(!_chunkID){
            _chunkID = uuidv4();
            cookie.save(_fileName, _chunkID);
        }
        // var re = /(?:\.([^.]+))?$/;
        try {
            const resp = await axios.get(`http://localhost:8080/upload/${_chunkID}/`);
            setBytesUploaded(resp.data.uploaded);
        } catch (error) {
            console.error(error.message);
        }
        // console.log(re.exec(file.name)[1]);
        console.log(_chunkID);
        setChunkID(_chunkID);
        setFileName(_fileName);
    }

    const prepareChunk = () => {
        const totalFileSize = file.size;
        const remainSize = totalFileSize - bytesUploaded;
        const start = totalFileSize - remainSize;
        const end = start + Math.min(defaultChunkSize, remainSize);
        const chunk = file.slice(start, end);
        if(remainSize > 0 && remainSize > defaultChunkSize)
            uploadChunk(chunk, start, end, totalFileSize);
        else
            uploadComplete(chunk, start, end, totalFileSize);
    }

    const uploadChunk = async (chunk, start, end, total) => {
        console.log(`bytes ${start}-${end}/${total}`);
        if(chunkID)
            try {
                const resp = await axios.post(`http://localhost:8080/upload/${chunkID}/`, chunk, {
                    headers: {
                        'Content-Range': `bytes ${start}-${end}/${total}`
                    }
                });
                setBytesUploaded(resp.data.uploaded);
            } catch (error) {
                console.error(error.message);
                setPause(true);
            }
    }

    const uploadComplete = async (chunk, start, end, total) => {
        try {
            const resp = await axios.post(`http://localhost:8080/upload/complete/${chunkID}/`, chunk, {
                headers: {
                    'Content-Range': `bytes ${start}-${end}/${total}`
                }
            });
            finish();
        } catch (error) {
            console.error(error.message);
            setPause(true);
        }
    }

    const cancelUpload = async () => {
        if(chunkID)
            try {
                axios.delete(`http://localhost:8080/upload/cancel/${chunkID}/`);
                console.log('CANCELED');
                finish();
            } catch (error) {
                console.error(error.message);
            }
    }

    const finish = () => {
        cookie.remove(fileName);
        setPause(true);
        setCancel(false);
        setBytesUploaded(0);
    }

    return children({bytesUploaded, pause, setPause, setCancel});
}

export default FileUploader;