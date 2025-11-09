import { useEffect, useRef, useState } from 'react';
const WS_HOST = process.env.NEXT_PUBLIC_API_URL?.replace(/^http/, 'ws') || 'ws://localhost:8000';
const API_KEY = 'dev-key';
export default function Home(){
  const mediaRecorderRef = useRef(null);
  const wsRef = useRef(null);
  const [isRecording,setIsRecording] = useState(false);
  const [transcripts,setTranscripts] = useState([]);
  const [finalNoteId,setFinalNoteId] = useState(null);
  const [tagText,setTagText] = useState('meeting');
  const [theme,setTheme] = useState('dark');

  useEffect(() => { document.documentElement.setAttribute('data-theme', theme==='dark'?'dark':'light'); },[theme]);

  function connectWs(noteTempId){
    const url = `${WS_HOST}/v1/stream-transcribe?noteTempId=${noteTempId}&x-api-key=${API_KEY}`;
    const ws = new WebSocket(url);
    ws.binaryType='arraybuffer';
    ws.onopen = ()=> console.log('ws open');
    ws.onmessage = (ev)=>{
      try{
        const data = JSON.parse(ev.data);
        if(data.type==='transcript_chunk'){
          setTranscripts(t=>[...t, {id:data.chunk_id, text:data.text}]);
        } else if(data.type==='note_saved'){
          setFinalNoteId(data.note_id);
        }
      }catch(e){ console.log('ws msg',e); }
    };
    wsRef.current = ws;
    return ws;
  }

  async function startRecording(){
    setFinalNoteId(null); setTranscripts([]);
    const stream = await navigator.mediaDevices.getUserMedia({ audio:true });
    const noteTempId = `temp-${Date.now().toString(36)}`;
    const ws = connectWs(noteTempId);
    await new Promise(res=>{ const check=()=> ws.readyState===WebSocket.OPEN?res():setTimeout(check,50); check(); });

    const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
    mediaRecorderRef.current = mediaRecorder;
    mediaRecorder.ondataavailable = (event)=>{
      if(event.data && event.data.size>0){
        event.data.arrayBuffer().then(buf=>{
          if(wsRef.current && wsRef.current.readyState===WebSocket.OPEN){
            const header = JSON.stringify({ type:'audio_chunk', chunk_id:`${Date.now()}` });
            wsRef.current.send(header);
            wsRef.current.send(buf);
          }
        });
      }
    };
    mediaRecorder.onstop = ()=>{
      if(wsRef.current && wsRef.current.readyState===WebSocket.OPEN){
        wsRef.current.send(JSON.stringify({ type:'stop', tags: tagText.split(',').map(t=>t.trim()) }));
      }
      stream.getTracks().forEach(t=>t.stop());
    };
    mediaRecorder.start(900);
    setIsRecording(true);
  }

  function stopRecording(){
    setIsRecording(false);
    if(mediaRecorderRef.current && mediaRecorderRef.current.state!=='inactive') mediaRecorderRef.current.stop();
  }

  async function ask(query){
    const res = await fetch('/api/proxy-chat', {
      method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({query, top_k:4})
    });
    const j = await res.json();
    alert('Answer: '+ (j.answer||JSON.stringify(j)));
  }

  return (
    <div className="app">
      <div className="sidebar">
        <h3>Pensieve</h3>
        <div style={{marginTop:12}}>
          <button className="btn" onClick={()=>setTheme(theme==='dark'?'light':'dark')}>Toggle theme</button>
        </div>
        <div style={{marginTop:20}}>
          <h4>Actions</h4>
          <div style={{marginTop:8}}>
            {!isRecording ? <button className="btn" onClick={startRecording}>Start Live Transcribe</button> : <button className="btn" onClick={stopRecording}>Stop</button>}
          </div>
          <div style={{marginTop:12}}>
            <input className="input" value={tagText} onChange={e=>setTagText(e.target.value)} placeholder="tags (comma)"/>
          </div>
        </div>
      </div>

      <div className="main">
        <div className="topbar">
          <div style={{flex:1}}>Project / Pensieve</div>
          <div style={{display:'flex',gap:8, alignItems:'center'}}>
            <input className="input" placeholder="Ask notes..." onKeyDown={e=>{ if(e.key==='Enter') ask(e.target.value) }}/>
            <div style={{width:12}}/>
            <div style={{opacity:0.7}}>User</div>
          </div>
        </div>

        <div className="canvas">
          <h3>Live Transcript</h3>
          <div style={{padding:12, background:'rgba(255,255,255,0.02)', borderRadius:8, minHeight:160}}>
            {transcripts.map(t=>t.text).join(' ')}
          </div>
          <div style={{marginTop:16}}>
            <strong>Saved Note:</strong> {finalNoteId || 'Not saved yet'}
          </div>
        </div>
      </div>

      <div className="assistant">
        <h4>Assistant</h4>
        <div style={{marginTop:8}}>
          <button className="btn" onClick={()=>ask('Summarize recent notes')}>Summarize</button>
        </div>
      </div>
    </div>
  );
}
