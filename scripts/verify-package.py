"""Verify archive contents and start its bundled MCP server without dependencies."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

root = Path(__file__).resolve().parent.parent
version = json.loads((root / 'package.json').read_text())['version']
archive = root / 'release' / f'noesis-grok-bot-{version}.zip'
expected_digest = (archive.with_name(archive.name + '.sha256')).read_text().split()[0]
if hashlib.sha256(archive.read_bytes()).hexdigest() != expected_digest:
    raise RuntimeError('Archive SHA-256 mismatch')
node = shutil.which('node')
if not node:
    raise RuntimeError('Node.js 22+ is required')
han = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')
with tempfile.TemporaryDirectory(prefix='noesis grok bot ') as temp:
    destination = Path(temp)
    with zipfile.ZipFile(archive) as package:
        names = package.namelist()
        if package.testzip() is not None:
            raise RuntimeError('Archive integrity failed')
        for name in names:
            path = Path(name)
            if not name.startswith('noesis-grok-bot/') or '..' in path.parts or any(part in ('node_modules', '.git', 'release') for part in path.parts):
                raise RuntimeError(f'Unexpected archive entry: {name}')
            if path.suffix in ('.json', '.md', '.mjs', '.py', '.cjs'):
                content = package.read(name).decode('utf-8')
                if path.suffix == '.json':
                    content = json.dumps(json.loads(content), ensure_ascii=False)
                if han.search(content):
                    raise RuntimeError(f'Non-English CJK content: {name}')
        package.extractall(destination)
    plugin = destination / 'noesis-grok-bot'
    checksums = json.loads((plugin / 'SHA256SUMS.json').read_text())
    if len(names) != len(checksums) + 1:
        raise RuntimeError('Unexpected file count')
    for name, digest in checksums.items():
        if hashlib.sha256((plugin / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError(f'File hash mismatch: {name}')
    probe = r'''
      const {spawn}=require('node:child_process');
      const {createInterface}=require('node:readline');
      const child=spawn(process.execPath,['./dist/server.cjs'],{cwd:process.argv[1],stdio:['pipe','pipe','pipe']});
      const waiting=new Map();let next=1,stderr='';
      child.stderr.on('data',b=>stderr+=b.toString());
      createInterface({input:child.stdout}).on('line',line=>{const v=JSON.parse(line);if(v.id)waiting.get(v.id)?.(v);});
      const rpc=(method,params)=>new Promise((resolve,reject)=>{
        const id=next++;const timer=setTimeout(()=>reject(Error('MCP timeout')),5000);
        waiting.set(id,v=>{clearTimeout(timer);waiting.delete(id);v.error?reject(Error(JSON.stringify(v.error))):resolve(v.result);});
        child.stdin.write(JSON.stringify({jsonrpc:'2.0',id,method,params})+'\n');
      });
      (async()=>{
        await rpc('initialize',{protocolVersion:'2025-03-26',capabilities:{},clientInfo:{name:'grok-bot-package-check',version:'1.0.0'}});
        child.stdin.write(JSON.stringify({jsonrpc:'2.0',method:'notifications/initialized'})+'\n');
        const tools=await rpc('tools/list',{});if(tools.tools.length!==11)throw Error('Wrong tool count');
        const r=await rpc('tools/call',{name:'noesis_read',arguments:{endpoint:'macro_latest'}});
        if(!r.isError||JSON.parse(r.content[0].text).error.code!=='AUTH_REQUIRED')throw Error('Unauthenticated read was not denied');
        if(stderr)throw Error('Unexpected stderr');
        console.log(JSON.stringify({tools:tools.tools.length,unauthenticatedRead:'denied',dependencyFree:true}));
      })().catch(e=>{console.error(e.message);process.exitCode=1;}).finally(()=>child.stdin.end());
    '''
    result = subprocess.run([node, '-e', probe, str(plugin)], capture_output=True, text=True, timeout=20, check=True, cwd=destination)
    print(json.dumps({'archiveChecksums': 'passed', 'archiveFiles': len(checksums), 'portableMcp': json.loads(result.stdout)}))
