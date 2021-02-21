import React, {react, useState} from 'react';
import axios from 'axios';
import FileUploader from './components/FileUploader';

const App = () => {
  const [file, setFile] = useState(null);

  const onFileSelect = (e) => {
    setFile(e.target.files[0]);
  }

  return (
    <div>
      <h1>HELLO WORLD</h1>
      <form>
        <label htmlFor="file-input">Select File: </label>
        <input onChange={onFileSelect} id="file-input" type="file"></input>
      </form>
      {file && (
          <FileUploader _file={file}>
            {({bytesUploaded, pause, setPause, cancelUpload}) => (
              <React.Fragment>
                <h1>UPLOADED= {Math.round((bytesUploaded / file.size) * 100)} %</h1>
                <button onClick={e => setPause(!pause)}>{pause ? '||' : '>>'}</button>
                <button onClick={e => cancelUpload()}>cancel</button>
              </React.Fragment>
            )}
          </FileUploader>
        )}
    </div>
  );
}

export default App;