import React, {react, useState} from 'react';
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
          <FileUploader file={file}>
            {({bytesUploaded, pause, setPause}) => (
              <React.Fragment>
                <h1>UPLOADED= {(bytesUploaded / file.size) * 100} %</h1>
                <button onClick={e => setPause(!pause)}>{pause ? '||' : '>>'}</button>
              </React.Fragment>
            )}
          </FileUploader>
        )}
    </div>
  );
}

export default App;
