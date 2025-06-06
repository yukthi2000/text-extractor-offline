import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [file,setfile] = useState(null)
  const [loading,setloading] = useState(false)
  const[transcription, setTranscription] = useState('')
  const [alertMessage, setAlertMessage] = useState('')
  const [error, setError] = useState('')


const handleFile=(e)=>{
  setfile(e.target.files[0])
setAlertMessage('') 

}

const handleSubmit= async(e)=>{
e.preventDefault();
if (!file) {
  setAlertMessage('Please select a file to upload!') 
  return
}

setloading(true)
const formData = new FormData();
formData.append("file",file);
console.log(formData);


try {
  const response = await fetch('http://localhost:5000/vidtranscribe', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  // Handle file download
  // const blob = await response.blob();
  // const url = window.URL.createObjectURL(blob);
  // const link = document.createElement('a');
  // link.href = url;
  // link.setAttribute('download', 'transcript.txt');
  // document.body.appendChild(link);
  // link.click();
  // link.remove();

  // If you want to also display the content (optional)
 
  // Parse the JSON response
  const data = await response.json();
  
  // Now you can access the transcript and transcript_no_time
  const transcript = data.transcript;
  const transcript_no_time = data.transcript_no_time;
  
  console.log('====================================');
  console.log(data);
  console.log('====================================');
  
  // Set the transcription in your state
  setTranscription(transcript);
  
  // If you also want to store the transcript without timestamps
  // setTranscriptionNoTime(transcript_no_time);
  
} catch (error) {
  console.error('Error:', error);
  setError(error.message);
} finally {
  setloading(false);
}
}




  return (
     <div className="flex items-center justify-center w-full h-screen bg-amber-200 ">
      {/* <header className='grid gap-10 '>
        <div>

        <h1 className='text-2xl font-bold font-serif mb-4'>speech to text converter</h1>
        <form onSubmit={handleSubmit}> 
        <input type='file' className="file:mr-4 file:rounded-full file:border-0 file:bg-violet-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-violet-700 hover:file:bg-violet-100 dark:file:bg-violet-600 dark:file:text-violet-100 dark:hover:file:bg-violet-500" accept='.mp3,.wav,.m4a' onChange={handleFile}/>
        <button type='submit' disabled={loading} class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
          
        {loading ? 'Processing...' : 'Upload and Transcribe'}
        </button>
        </form>
        </div>
        {transcription && (
          <>
    <h2 className="text-red-500 font-mono text-3xl">Transcription</h2>

  <div className="w-full max-w-full h-100 overflow-y-auto">
    <p className="bg-blue-300 font-serif block whitespace-pre-wrap">{transcription}</p>
  </div>
          </>
)}

                {alertMessage && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 border-l-4 border-red-500">
            <span className="font-bold">Error:</span> {alertMessage}
          </div>
        )}
      </header> */}



      <header className='grid gap-10 '>
        <div>

        <h1 className='text-2xl font-bold font-serif mb-4'>video to text converter</h1>
        <form onSubmit={handleSubmit}> 
        <input type='file' className="file:mr-4 file:rounded-full file:border-0 file:bg-violet-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-violet-700 hover:file:bg-violet-100 dark:file:bg-violet-600 dark:file:text-violet-100 dark:hover:file:bg-violet-500" accept='.mp4,.mkv' onChange={handleFile}/>
        <button type='submit' disabled={loading} class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
          
        {loading ? 'Processing...' : 'Upload and Transcribe'}
        </button>
        </form>
        </div>
        {transcription && (
          <>
    <h2 className="text-red-500 font-mono text-3xl">Transcription</h2>

  <div className="w-full max-w-full h-100 overflow-y-auto">
    <p className="bg-blue-300 font-serif block whitespace-pre-wrap">{transcription}</p>
  </div>
          </>
)}

                {alertMessage && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 border-l-4 border-red-500">
            <span className="font-bold">Error:</span> {alertMessage}
          </div>
        )}
      </header>
     </div>
  )
}

export default App
