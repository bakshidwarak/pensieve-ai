export default async function handler(req,res){
  if(req.method !== 'POST') return res.status(405).end();
  const body = req.body;
  const resp = await fetch((process.env.BACKEND_URL||'http://localhost:8000') + '/v1/chat', {
    method:'POST',
    headers:{ 'Content-Type':'application/json', 'x-api-key':'dev-key' },
    body: JSON.stringify(body)
  });
  const j = await resp.json();
  res.status(200).json(j);
}
