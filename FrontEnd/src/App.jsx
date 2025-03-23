import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [file,setfile] = useState(null)
  const [loading,setloading] = useState(false)
  const[transcription, setTranscription] = useState('dsadas')
  const [alertMessage, setAlertMessage] = useState('')
const handleFile=(e)=>{
  setfile(e.target.value)
}

const handleSubmit= async(e)=>{
e.preventDefault();
if(!file) alert("Empty") ;

setloading(true)
const formData = new FormData();
formData.append("file",file);

try{
  const response = await fetch('http://localhost:5000/transcribe',{
    method:'POST',
    body:formData,
  })
  const data = await response.json();
  setTranscription(data.text);
}catch(error){
  console.log(error);
  
}finally{
  setloading(false);
}


}

  return (
     <div className="flex items-center justify-center w-full h-screen bg-amber-200 ">
      <header className='grid gap-10 '>
        <div>

        <h1 className='text-2xl font-bold font-serif mb-4'>speech to text converter</h1>
        <form onSubmit={handleSubmit}> 
        <input type='file' className="file:mr-4 file:rounded-full file:border-0 file:bg-violet-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-violet-700 hover:file:bg-violet-100 dark:file:bg-violet-600 dark:file:text-violet-100 dark:hover:file:bg-violet-500" accept='.mp3,.wav' onChange={handleFile}/>
        <button type='submit' disabled={loading} class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
          
        {loading ? 'Processing...' : 'Upload and Transcribe'}
        </button>
        </form>
        </div>
        {transcription && (
          <div className="">
            <h2 className='text-red-500 font-mono text-3xl' >Transcription</h2>
            <p className='bg-blue-300 font-serif inline'>{transcription}</p>
          </div>
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
