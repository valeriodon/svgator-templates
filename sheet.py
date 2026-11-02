"""usage: sheet.py video.mp4 out.png start_ms end_ms step_ms [cols] [width]"""
import sys,subprocess,io,os
from PIL import Image, ImageDraw
v,out,a,b,st=sys.argv[1:6]; cols=int(sys.argv[6]) if len(sys.argv)>6 else 6; tw=int(sys.argv[7]) if len(sys.argv)>7 else 260
ff=os.path.expanduser('~/.local/bin/ffmpeg')
if not os.path.exists(ff): ff='ffmpeg'   # fall back to ffmpeg on PATH
ims=[]
for t in range(int(a),int(b)+1,int(st)):
    r=subprocess.run([ff,'-v','error','-ss',str(t/1000),'-i',v,'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True)
    im=Image.open(io.BytesIO(r.stdout)).convert('RGB'); im=im.resize((tw,int(im.height*tw/im.width)))
    d=ImageDraw.Draw(im); d.rectangle([0,0,52,16],fill=(0,0,0)); d.text((3,2),str(t),fill=(255,255,0)); ims.append(im)
w,h=ims[0].size; rows=(len(ims)+cols-1)//cols
S=Image.new('RGB',(cols*(w+6)+6,rows*(h+6)+6),(90,90,90))
for i,im in enumerate(ims): S.paste(im,(6+(i%cols)*(w+6),6+(i//cols)*(h+6)))
S.save(out); print(S.size)
