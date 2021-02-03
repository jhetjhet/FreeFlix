import {useState, useEffect} from 'react';
import axios from 'axios';
// import cookie from 'react-'

const defaultChunkSize = 1024 * 1024;

const stringToHash = (str) => {
    var hash, chr;
    for(var i = 0; i < str.length; i++){
        chr = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + chr;
        hash |= 0;
    }
    return hash;
}

const FileUploader = ({children, file, onFinish}) => {
    // upload
    const [fileChunk, setFileChunk] = useState(null);
    const [startChunkByte, setStartChunkByte] = useState(undefined);
    const [endChunkByte, setEndChunkByte] = useState(undefined);
    const [bytesUploaded, setBytesUploaded] = useState(0);
    const [totalFileSize, setTotalFileSize] = useState(undefined);

    // state
    const [pause, setPause] = useState(true);
    const [cancel, setCancel] = useState(false);

    useEffect(() => {
        if(!totalFileSize){
            setTotalFileSize(file.size);
            setStartChunkByte(0);
            setEndChunkByte(defaultChunkSize);
            // console.log(`${file.name}-${file.lastModified}-${file.size}`);
        }else{
            if(!pause && !cancel){
                const remainSize = totalFileSize - bytesUploaded;
                console.log(remainSize);
                if(remainSize > 0){
                    prepareChunk();
                }
            }
        }
    }, [bytesUploaded, pause, cancel, totalFileSize, file]);

    const prepareChunk = () => {
        const remainSize = totalFileSize - bytesUploaded;
        const start = totalFileSize - remainSize;
        const end = start + Math.min(defaultChunkSize, remainSize);
        const chunk = file.slice(start, end);
        uploadChunk(chunk);
    }

    const uploadChunk = (chunk) => {
        setTimeout(() => {
            setBytesUploaded(bytesUploaded + chunk.size);
        }, 1000);
    }

    return children({bytesUploaded, pause, setPause});
}

export default FileUploader;