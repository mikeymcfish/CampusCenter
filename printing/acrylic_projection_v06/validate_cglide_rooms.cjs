const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path'),crypto=require('crypto');
const sourcePath='T:/AI/Comfy2601/ComfyUI/ComfyUI_windows_portable/ComfyUI/custom_nodes/ComfyUI-CGlide/web/csglide_cast.js';
const code=fs.readFileSync(sourcePath,'utf8');
function fn(name){const start=code.indexOf('function '+name+'(');assert(start>=0);let brace=code.indexOf('{',start),depth=1,i=brace+1;for(;depth;i++){if(code[i]==='{')depth++;if(code[i]==='}')depth--;}return (name==='zipRead'?'async ':'')+code.slice(start,i);}
const constants=code.split('\n').filter(s=>s.startsWith('const MAX_IMAGES')||s.startsWith('const alignFrames')).join('\n');
const ctx={TextDecoder,DataView,Uint8Array,Map,Blob,Response,DecompressionStream};
vm.runInNewContext(constants+'\n'+['blankState','parseInitial','presentation','zipRead'].map(fn).join('\n')+'\nthis.api={parseInitial,presentation,zipRead};',ctx);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const root=__dirname,folder=path.join(root,'cglide'),manifest=JSON.parse(fs.readFileSync(path.join(folder,'package_manifest.json'),'utf8'));
 const files=[...manifest.packages.map(r=>({file:r.package,count:1})),{file:manifest.combined_package,count:31}];let states=0,assignments=0;
 for(const {file,count} of files){
  const bytes=fs.readFileSync(path.join(folder,file));
  const entries=await ctx.api.zipRead(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength));
  const p=JSON.parse(new TextDecoder().decode(entries.get('project.json')));assert.equal(p.shots.length,count);assert(p.meta.packed);assert.equal(p.meta.shots,count);
  const refs=JSON.parse(new TextDecoder().decode(entries.get('REFERENCE_ORDER.json')));
  for(const shot of p.shots){
   const n=shot.id.split('-').pop(),r=refs.find(r=>r.room===n);assert(r);
   const s=ctx.api.parseInitial(JSON.stringify(shot.state));assert.deepStrictEqual(JSON.parse(JSON.stringify(s)),shot.state);
   assert.equal(s.mode,'fl2va');assert.equal(s.length,294);assert.equal(s.width,768);assert.equal(s.height,768);
   assert(s.prompt.includes('12.25 seconds'));assert(/^[\x00-\x7f]*$/.test(s.prompt));assert(!s.prompt.includes('<Picture'));
   assert(s.prompt.includes('Static Shot for the entire 12.25 seconds'));
   assert(s.prompt.includes('Every stationary landmark occupies the SAME screen coordinates in EVERY frame'));
   assert(s.prompt.includes('Only people animate inside this stationary background'));
   assert(s.slots.videos.every(x=>!x.file)&&s.slots.audios.every(x=>!x.file));assert(s.slots.first.file&&!s.slots.last.file&&!s.cont.file);assert(s.slots.images.every(x=>!x.file));
   const tags=ctx.api.presentation(s).tags;assert.equal(Object.keys(tags).length,r.refs.length);
   for(const ref of r.refs){
    assert.equal(tags['@first'],'<Picture 1>');assert.equal(ref.slot,'first');
    assert.equal(s.slots.first.file,ref.asset);assert(entries.has('assets/'+ref.asset));
    assert.equal(sha(entries.get('assets/'+ref.asset)),ref.sha256);assert.equal(sha(fs.readFileSync(path.join(root,ref.source))),ref.sha256);
    assert(s.prompt.includes('@first'));assignments++;
   }
   let compiled=s.prompt;for(const [token,label] of Object.entries(tags))compiled=compiled.replaceAll(token,label);
   assert(!/@image\d+/.test(compiled));assert(!compiled.includes('<Subject'));assert(compiled.includes('integrated_multimodal_description:'));assert(compiled.length<7000);
   assert(entries.has(`masks/${n}_Room_Mask_1024.png`));assert.equal(r.refs.length,1);
   if(n==='GYM')assert(compiled.includes('No bleachers'));
   states++;
  }
 }
 const report={installed_parser:sourcePath,parser_sha256:sha(Buffer.from(code)),package_count:files.length,states_round_tripped:states,image_assignments_verified:assignments,all_assets_byte_identical:true,zip_read_by_installed_CGlide_code:true,reference_tag_compilation_verified:true,output_frames:294,output_seconds:12.25,output_resolution:[768,768],encoding:'ASCII prompt text in UTF-8 JSON',live_UI_import_performed:false,generation_submitted:false};
 fs.writeFileSync(path.join(folder,'validation.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
