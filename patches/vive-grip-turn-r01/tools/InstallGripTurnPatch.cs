using System;
using System.IO;
using System.Diagnostics;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using System.Security.Cryptography;
[DataContract] public class PatchFile{[DataMember] public string path;[DataMember] public string sha256;[DataMember] public long bytes;}
[DataContract] public class PatchChunk:PatchFile{[DataMember] public long source_offset;[DataMember] public int source_bytes;[DataMember] public int target_bytes;}
[DataContract] public class BaseVariant{[DataMember] public string name;[DataMember] public PatchFile[] files;}
[DataContract] public class GripManifest{[DataMember] public string base_exe_sha256;[DataMember] public string target_exe_sha256;[DataMember] public long target_bytes;[DataMember] public PatchChunk[] chunks;[DataMember] public PatchFile[] overlay_files;[DataMember] public BaseVariant[] variants;}
public class InstallGripTurnPatch {
 [StructLayout(LayoutKind.Sequential)] struct DeltaInput{public IntPtr start;public UIntPtr size;[MarshalAs(UnmanagedType.Bool)]public bool editable;}
 [StructLayout(LayoutKind.Sequential)] struct DeltaOutput{public IntPtr start;public UIntPtr size;}
 [DllImport("msdelta.dll",SetLastError=true)] [return:MarshalAs(UnmanagedType.Bool)] static extern bool ApplyDeltaB(long flags,DeltaInput source,DeltaInput delta,out DeltaOutput output);
 [DllImport("msdelta.dll")] [return:MarshalAs(UnmanagedType.Bool)] static extern bool DeltaFree(IntPtr p);
 static string Sha(string f){using(var h=SHA256.Create())using(var s=File.OpenRead(f)){return BitConverter.ToString(h.ComputeHash(s)).Replace("-","").ToLowerInvariant();}}
 static void Need(bool b,string msg){if(!b)throw new InvalidOperationException(msg);}
 static string Under(string root,string relative){Need(!Path.IsPathRooted(relative)&&!relative.Contains(".."),"Unsafe relative path");string x=Path.GetFullPath(Path.Combine(root,relative.Replace('/',Path.DirectorySeparatorChar)));Need(x.StartsWith(root.TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase),"Path escapes chosen folder");return x;}
 static void Check(string root,PatchFile f){string p=Under(root,f.path);Need(File.Exists(p)&&new FileInfo(p).Length==f.bytes&&Sha(p)==f.sha256,"Version/hash mismatch: "+f.path);}
 static byte[] Apply(byte[] source,byte[] delta){var a=GCHandle.Alloc(source,GCHandleType.Pinned);var b=GCHandle.Alloc(delta,GCHandleType.Pinned);DeltaOutput result;
  try {Need(ApplyDeltaB(0,new DeltaInput{start=a.AddrOfPinnedObject(),size=(UIntPtr)source.Length},new DeltaInput{start=b.AddrOfPinnedObject(),size=(UIntPtr)delta.Length},out result),"Windows delta reconstruction failed: "+Marshal.GetLastWin32Error());try{Need(result.size.ToUInt64()<=16777216,"Oversize delta output");var bytes=new byte[(int)result.size.ToUInt64()];Marshal.Copy(result.start,bytes,0,bytes.Length);return bytes;}finally{DeltaFree(result.start);}}
  finally{a.Free();b.Free();}
 }
 static void NoRunningGame(){Need(Process.GetProcessesByName("CampusCenter").Length==0,"Close CampusCenter before installing or rolling back. No process will be terminated.");}
 public static int Main(string[] args){try{
  Need(args.Length==2&&(args[0]=="install"||args[0]=="rollback"),"Usage: InstallGripTurnPatch.exe install|rollback \"existing Windows build folder\"");
  string root=Path.GetFullPath(args[1]).TrimEnd(Path.DirectorySeparatorChar),payload=Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location);
  Need(Directory.Exists(root),"Chosen Windows build folder does not exist");NoRunningGame();
  GripManifest m;using(var s=File.OpenRead(Path.Combine(payload,"grip-patch-manifest.json")))m=(GripManifest)new DataContractJsonSerializer(typeof(GripManifest)).ReadObject(s);
  Need(m.base_exe_sha256=="1b503e2e77c5c6063c89d571b8347cdaf7e5ece66545cd83116a3a83145a9624","Unsupported manifest baseline");
  string exe=Under(root,"CampusCenter/Binaries/Win64/CampusCenter.exe"),backup=Under(root,"_GripTurnR01_Rollback"),old=Path.Combine(backup,"CampusCenter.original.exe");Need(File.Exists(exe),"Use the Windows folder containing the CampusCenter and Engine folders");
  if(args[0]=="rollback"){
   Need(File.Exists(old)&&Sha(old)==m.base_exe_sha256,"Original backup missing or altered");Need(Sha(exe)==m.target_exe_sha256,"Current executable differs; refusing to overwrite a later update");
   foreach(var f in m.overlay_files)Check(root,new PatchFile{path="CampusCenter/Content/Paks/"+f.path,bytes=f.bytes,sha256=f.sha256});
   foreach(var f in m.overlay_files)Need(!File.Exists(Path.Combine(backup,f.path)),"Rollback destination already exists");
   foreach(var f in m.overlay_files)File.Move(Under(root,"CampusCenter/Content/Paks/"+f.path),Path.Combine(backup,f.path));
   File.Replace(old,exe,Path.Combine(backup,"CampusCenter.retired-grip.exe"));Need(Sha(exe)==m.base_exe_sha256,"Rollback verification failed");Console.WriteLine("Original executable restored; grip overlay removed. Standard settings and launchers unchanged.");return 0;
  }
  if(Sha(exe)==m.target_exe_sha256){foreach(var f in m.overlay_files)Check(root,new PatchFile{path="CampusCenter/Content/Paks/"+f.path,bytes=f.bytes,sha256=f.sha256});Console.WriteLine("Exact grip patch already installed.");return 0;}
  Need(Sha(exe)==m.base_exe_sha256,"Unsupported executable; only exact verified R28/R29 builds are accepted");
  string variant=null;foreach(var v in m.variants){bool good=true;foreach(var f in v.files){string x=Under(root,f.path);if(!File.Exists(x)||new FileInfo(x).Length!=f.bytes||Sha(x)!=f.sha256){good=false;break;}}if(good){variant=v.name;break;}}
  Need(variant!=null,"Build dependencies differ from both verified R28 and R29; no files changed");
  Need(!Directory.Exists(backup),"Rollback folder already exists; preserve it and review before applying again");
  foreach(var f in m.overlay_files){Need(f.path=="CampusCenter-GripTurnR01_1_P.pak"||f.path=="CampusCenter-GripTurnR01_1_P.utoc"||f.path=="CampusCenter-GripTurnR01_1_P.ucas","Unexpected overlay file");Check(Path.Combine(payload,"Overlay"),f);Need(!File.Exists(Under(root,"CampusCenter/Content/Paks/"+f.path)),"An overlay already exists; no overwrite allowed");}
  Need(m.chunks.Length>0&&m.chunks.Length<=64&&m.target_bytes>0&&m.target_bytes<2147483647,"Invalid chunk manifest");long offset=0,targetTotal=0;foreach(var c in m.chunks){Need(c.source_offset==offset&&c.source_bytes>=0&&c.source_bytes<=16777216&&c.target_bytes>0&&c.target_bytes<=16777216,"Invalid chunk range");Check(payload,c);offset+=c.source_bytes;targetTotal+=c.target_bytes;}Need(offset==new FileInfo(exe).Length&&targetTotal==m.target_bytes,"Chunk lengths differ from executable");
  string stage=Under(root,"_GripTurnR01_Staging");Need(!Directory.Exists(stage),"A staging folder exists; preserve and inspect it before retrying");Directory.CreateDirectory(stage);string next=Path.Combine(stage,"CampusCenter.exe");
  using(var source=File.OpenRead(exe))using(var dest=new FileStream(next,FileMode.CreateNew))foreach(var c in m.chunks){source.Position=c.source_offset;byte[] bytes=new byte[c.source_bytes];int got=0;while(got<bytes.Length){int n=source.Read(bytes,got,bytes.Length-got);Need(n>0,"Truncated source");got+=n;}byte[] decoded=Apply(bytes,File.ReadAllBytes(Under(payload,c.path)));Need(decoded.Length==c.target_bytes,"Chunk output size mismatch");dest.Write(decoded,0,decoded.Length);}
  Need(Sha(next)==m.target_exe_sha256,"Reconstructed executable hash differs; installed files remain untouched");
  Directory.CreateDirectory(backup);File.WriteAllText(Path.Combine(backup,"variant.txt"),variant);
  Need(Sha(exe)==m.base_exe_sha256,"Executable changed during reconstruction; no installed files replaced");
  File.Replace(next,exe,old);
  try{foreach(var f in m.overlay_files)File.Copy(Under(Path.Combine(payload,"Overlay"),f.path),Under(root,"CampusCenter/Content/Paks/"+f.path),false);}
  catch{
   foreach(var f in m.overlay_files){string x=Under(root,"CampusCenter/Content/Paks/"+f.path);if(File.Exists(x)&&Sha(x)==f.sha256)File.Move(x,Path.Combine(backup,f.path));}
   if(File.Exists(old)&&Sha(old)==m.base_exe_sha256&&Sha(exe)==m.target_exe_sha256)File.Replace(old,exe,Path.Combine(backup,"CampusCenter.failed-install.exe"));
   throw;
  }
  Need(Sha(exe)==m.target_exe_sha256&&Sha(old)==m.base_exe_sha256,"Installed/backup executable verification failed");foreach(var f in m.overlay_files)Check(root,new PatchFile{path="CampusCenter/Content/Paks/"+f.path,bytes=f.bytes,sha256=f.sha256});
  Console.WriteLine("Grip patch installed for "+variant+". Left/right side grip snaps 30 degrees once per press; index-trigger forward retained. No initial-yaw, runtime or saved-setting change. Hardware testing remains pending.");return 0;
 }catch(Exception e){Console.Error.WriteLine("Stopped: "+e.Message+". No processes or system settings were changed. Preserve any staging/rollback folder for recovery.");return 1;}}
}
