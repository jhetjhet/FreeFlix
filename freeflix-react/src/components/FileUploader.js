import {useState, useEffect} from 'react';
import {v4 as uuidv4} from 'uuid';
import axios from 'axios';
import cookie from 'react-cookies';

const stringToHash = (str) => {
    var hash, chr;
    for(var i = 0; i < str.length; i++){
        chr = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + chr;
        hash |= 0;
    }
    return hash;
}

const FileUploader = ({children, _file, onFinish, chunkSize=(1048576 * 3)}) => {
    // upload
    const [bytesUploaded, setBytesUploaded] = useState(null);
    const [chunkID, setChunkID] = useState(undefined);
    const [cookieName, setCookieName] = useState(undefined);
    const [file, setFile] = useState(null);
    const [cancelTokenSource, setCancelTokenSource] = useState(null);

    // state
    const [pause, setPause] = useState(true);
    const [newUpload, setNewUpload] = useState(true);

    useEffect(() => {
        console.log(`[uploaded]: ${bytesUploaded}`);
        if(file !== _file){
            setFile(_file);
            init(_file);
        }else{
            if(!pause){
                const remainSize = file.size - bytesUploaded;
                if(remainSize > 0) prepareChunk();
            }
        }
    }, [bytesUploaded, pause, file, _file]);

    const init = (file) => {
        var cookieName = stringToHash(`${file.name}-${file.lastModified}-${file.size}`);
        var chunkid = cookie.load(cookieName);
        console.log(`[cookie]: ${cookieName}`);
        if(!chunkid){
            chunkid = uuidv4();
            cookie.save(cookieName, chunkid);
        }

        axios.get(`http://localhost:8080/upload/${chunkid}/`).then((resp) => {
            setBytesUploaded(resp.data.uploaded);
            console.log(resp.data);
        }).catch((err) => {
            console.error(err);
        });

        setChunkID(chunkid);
        setCookieName(cookieName);
    }

    const prepareChunk = () => {
        const totalFileSize = file.size;
        const remainSize = totalFileSize - bytesUploaded;
        const start = totalFileSize - remainSize;
        const end = start + Math.min(chunkSize, remainSize);
        const chunk = file.slice(start, end);
        uploadChunk(chunk, start, end, remainSize, totalFileSize);
    }

    const uploadChunk = (chunk, start, end, remainSize, total) => {
        var form = new FormData();
        form.append("filename", file.name);
        form.append("chunk", chunk);

        var url;
        if(remainSize > 0 && remainSize > chunkSize)
            url = `http://localhost:8080/upload/${chunkID}/`;
        else
            url = `http://localhost:8080/upload/complete/${chunkID}/`;

        const source = axios.CancelToken.source();
        setCancelTokenSource(source);

        if(chunkID){
            axios.post(url, form, {
                cancelToken: source.token,
                headers: {
                    'Content-Range': `bytes ${start}-${end}/${total}`,
                    'content-type': 'multipart/form-data',
                }
            }).then((resp) => {
                setBytesUploaded(resp.data.uploaded);
                if(resp.data.uploaded === file.size)
                    finish();
            }).catch((err) => {
                console.error(err);
                setPause(true);
            });
        }
    }

    const cancelUpload = () => {
        if(chunkID && bytesUploaded > 0){
            if(cancelTokenSource)
                cancelTokenSource.cancel(`${chunkID} file upload canceled.`);
            finish();
            axios.delete(`http://localhost:8080/upload/cancel/${chunkID}/`).then((resp) => {
                // finish();
            }).catch(err => {
                console.error(err);
            });
        }
    }

    const finish = () => {
        cookie.remove(cookieName);
        setFile(null);
        setPause(true);
        setBytesUploaded(null);
    }

    return children({bytesUploaded, pause, setPause, cancelUpload});
}

export default FileUploader;