using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using System.Security.Cryptography;
[DataContract] class Chunk { [DataMember] public string path; [DataMember] public string sha256; [DataMember] public long source_offset; [DataMember] public int source_bytes; [DataMember] public int target_bytes; }
[DataContract] class Manifest { [DataMember] public string base_exe_sha256; [DataMember] public string target_exe_sha256; [DataMember] public long target_bytes; [DataMember] public Chunk[] chunks; }
class ApplySenderDelta {
 [StructLayout(LayoutKind.Sequential)] struct In { public IntPtr start; public UIntPtr size; public int editable; }
 [StructLayout(LayoutKind.Sequential)] struct Out { public IntPtr start; public UIntPtr size; }
 [DllImport("msdelta.dll",SetLastError=true)] static extern bool ApplyDeltaB(ulong flags, In source, In delta, out Out target);
 [DllImport("msdelta.dll")] static extern bool DeltaFree(IntPtr memory);
 static void Need(bool good,string message){if(!good)throw new InvalidDataException(message);}
 static string Sha(string path){using(var f=File.OpenRead(path))using(var s=SHA256.Create())return BitConverter.ToString(s.ComputeHash(f)).Replace("-","").ToLowerInvariant();}
 static byte[] Apply(byte[] source,byte[] delta){
  var a=GCHandle.Alloc(source,GCHandleType.Pinned);var b=GCHandle.Alloc(delta,GCHandleType.Pinned);
  try{Out output;Need(ApplyDeltaB(0,new In{start=a.AddrOfPinnedObject(),size=(UIntPtr)source.Length},new In{start=b.AddrOfPinnedObject(),size=(UIntPtr)delta.Length},out output),"MSDelta failed: "+Marshal.GetLastWin32Error());
   try{ulong n=output.size.ToUInt64();Need(n<=16777216,"Decoded chunk exceeds limit");var data=new byte[(int)n];Marshal.Copy(output.start,data,0,data.Length);return data;}finally{DeltaFree(output.start);}
  }finally{a.Free();b.Free();}
 }
 static int Main(string[] args){try{
  Need(args.Length==3,"Usage: ApplySenderDelta payload source-exe NEW-target-exe");string root=Path.GetFullPath(args[0]),source=Path.GetFullPath(args[1]),target=Path.GetFullPath(args[2]);
  Need(!File.Exists(target),"Target exists; no overwrite permitted");Manifest m;using(var f=File.OpenRead(Path.Combine(root,"sender-manifest.json")))m=(Manifest)new DataContractJsonSerializer(typeof(Manifest)).ReadObject(f);
  Need(m.base_exe_sha256=="20adab2cd975e19d325adbe607b907cfffa2bd3e775b01c51a68f695bfdf915a"&&Sha(source)==m.base_exe_sha256,"Source is not the exact approved grip-enabled native executable");
  Need(m.chunks!=null&&m.chunks.Length>0&&m.chunks.Length<=64,"Invalid chunk count");long offset=0,total=0;
  foreach(var c in m.chunks){Need(c.source_offset==offset&&c.source_bytes>0&&c.source_bytes<=16777216&&c.target_bytes>0&&c.target_bytes<=16777216,"Invalid chunk ranges");offset+=c.source_bytes;total+=c.target_bytes;
   string path=Path.GetFullPath(Path.Combine(root,c.path));Need(path.StartsWith(root.TrimEnd('\\')+"\\",StringComparison.OrdinalIgnoreCase),"Unsafe chunk path");Need(Sha(path)==c.sha256,"Chunk hash differs");}
  Need(offset==new FileInfo(source).Length&&total==m.target_bytes,"Size closure mismatch");
  using(var input=File.OpenRead(source))using(var output=new FileStream(target,FileMode.CreateNew))foreach(var c in m.chunks){input.Position=c.source_offset;var data=new byte[c.source_bytes];int got=0;while(got<data.Length){int n=input.Read(data,got,data.Length-got);Need(n>0,"Truncated source");got+=n;}
   var decoded=Apply(data,File.ReadAllBytes(Path.Combine(root,c.path)));Need(decoded.Length==c.target_bytes,"Decoded chunk length differs");output.Write(decoded,0,decoded.Length);}
  Need(Sha(source)==m.base_exe_sha256&&Sha(target)==m.target_exe_sha256,"Final SHA256 mismatch; preserve output for review");Console.WriteLine("Native sender reconstructed and SHA256 verified.");return 0;
 }catch(Exception e){Console.Error.WriteLine(e.Message);return 1;}}
}
