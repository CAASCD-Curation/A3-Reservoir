import json,re,pathlib,shutil,csv
from PIL import Image,ImageOps
import argparse,openpyxl
parser=argparse.ArgumentParser(description="按用户确认的 a-b 分类与序号规则导入图片档案")
parser.add_argument('--excel',required=True)
parser.add_argument('--images',nargs='+',required=True)
parser.add_argument('--output',default=str(pathlib.Path(__file__).resolve().parent.parent))
args=parser.parse_args()
root=pathlib.Path(args.output);sheet=openpyxl.load_workbook(args.excel,read_only=True,data_only=True).active
rows=[{'row':i,'values':list(r)} for i,r in enumerate(sheet.values,1) if any(v is not None for v in r)]
positions=['FUNCTION PROTOTYPE','SPATIAL PROTOTYPE','MECHANISM PROTOTYPE','SPATIAL TRANSFORMATION','MEDIUM TRANSFORMATION','CONCEPTUAL TRANSFORMATION']
action_names=['COLLECT','HOLD','ACCUMULATE','FILTER','SETTLE','PRESSURIZE','REACH LIMIT','OVERFLOW','RELEASE','EMPTY','RECYCLE']
bykey={};group=None
headers=rows[0]['values']
assert headers[:9]==['分类1','一级分类','序号','来源','案例','精短标签','地点／年代','原型价值','出处/作者'], 'Unexpected Excel headers'
for row in rows[1:]:
 v=row['values'];r=row['row']
 category=re.match(r'\s*([1-6])',str(v[1] or ''))
 if category:group=int(category[1])
 if not v[4] or v[2] is None:continue
 assert group is not None, f'Missing category at row {r}'
 key=f'{group}-{int(v[2])}';normalized=[]
 for value in v[11:13]:
  for token in re.split(r'[→,，/|｜、;；]',str(value or '')):
   token=token.strip().upper();token=token
   if re.fullmatch(r'[A-Z]+(?: [A-Z]+)*',token) and token not in normalized:normalized.append(token)
 source=[a for a in ['INFRASTRUCTURE','ARCHITECTURE','ART','LITERATURE','EVERYDAY','BODY','LANGUAGE / CONCEPT','LANDSCAPE'] if a in str(v[3]).upper()]
 evidence=str(v[8] or '').strip();urls=re.findall(r'https?://[^\s<>]+',evidence)
 notes=[]

 obj={'id':f'R-{chr(64+group)}-{key.split(chr(45))[1]}','matchKey':key,'title':str(v[4]).strip(),'description':str(v[7] or '').strip(),'year':str(v[6]) if isinstance(v[6],(int,float)) else None,'placeAndPeriod':str(v[6]).strip() if v[6] is not None else None,'curatorialPosition':positions[group-1],'positionNumber':group,'sourceType':source,'actions':normalized,'keywords': [k.strip() for k in re.split(r'[｜|、,，;；\n]',str(v[5] or '')) if k.strip()],'weight':2 if len(str(v[7] or ''))<110 else 3,'depth':group*5,'relatedIds':[],'sourceTitle':evidence if not urls else None,'url':urls[0] if urls else None,'excelRow':r,'sheet':sheet.title,'dataNotes':notes}
 if key in bykey:raise ValueError('Duplicate Excel key '+key)
 bykey[key]=obj
images={}
for folder in args.images:
 for p in pathlib.Path(folder).rglob('*'):
  if p.suffix.lower() in ['.jpg','.png','.jpeg','.webp'] and re.fullmatch(r'[1-6]-\d+',p.stem):
   if p.stem in images:raise ValueError('Duplicate image key '+p.stem)
   images[p.stem]=p
(root/'src/data').mkdir(parents=True,exist_ok=True)
(root/'data-audit').mkdir(parents=True,exist_ok=True)
def year(s):
 s=str(s or '')
 if len(s)>100:return None
 if re.search(r'\d{3,}世纪',s):return None
 m=re.search(r'(公元前)?(\d{1,2})(?:[—–-]\d{1,2})?世纪',s)
 if m:return -(int(m[2])*100) if m[1] else (int(m[2])-1)*100
 m=re.search(r'(公元前)?\s*(\d{3,4})(?=\D|$)',s)
 return (-1 if m[1] else 1)*int(m[2]) if m else None
data=[];mapping=[]
for key,p in sorted(images.items(),key=lambda kv:tuple(map(int,kv[0].split('-')))):
 group,num=map(int,key.split('-'));o=bykey.get(key)
 if o:
  o=json.loads(json.dumps(o));v=next(r['values'] for r in rows if r['row']==o['excelRow']);o['rawRow']={str((headers[i] if i<len(headers) else None) or f'未命名列 {i+1}'):x for i,x in enumerate(v) if x is not None};o['title']=str(v[4]).strip();o['description']=str(v[7] or '').strip();o['dataNotes']=[n for n in o['dataNotes'] if '主动作列' in n];o['matchingStatus']='matched-by-user-key';o['imageOnly']=False

 else:
  o={'id':f'R-{chr(64+group)}-{key.split(chr(45))[1]}','matchKey':key,'title':'','description':'','year':None,'placeAndPeriod':None,'curatorialPosition':positions[group-1],'positionNumber':group,'sourceType':[],'actions':[],'keywords':[],'weight':2,'depth':group*5,'relatedIds':[],'sourceTitle':None,'url':None,'rawRow':{},'excelRow':None,'sheet':'工作表1','matchingStatus':'image-only','imageOnly':True,'dataNotes':['该编号有图片，Excel 中未找到对应文字记录；保留图片及编号，不推测标题和说明。']}
 o['imageFilename']=p.name;o['image']='images/'+p.name;o['encodedImage']=None;o['thumbnail']='thumbnails/'+key+'.webp';o['actionEligible']=group in [1,2];o['sortYear']=year(o.get('placeAndPeriod'));o['dateSortBasis']='年代起始值，仅用于排序；原文保留' if o['sortYear'] is not None else None;o['mapPosition']=None;o['mapEvidence']=[]
 # Semantic coordinates are derived only from explicit research metadata.
 # Classification is the Z-axis. Unknown flow/physical attributes remain unplaced.
 if not o['imageOnly']:
  incoming=sorted(set(o['keywords'])&{'集雨','引水','汇入','屋面','回灌','回补'})
  outgoing=sorted(set(o['keywords'])&{'供水','取水','泵排','灌溉','溢流','溢洪','自排','重力退水'})
  inflow=bool(incoming) or bool({'COLLECT','GATHER'}&set(o['actions']));outflow=bool(outgoing) or 'RELEASE' in o['actions']
  if group<=3 and (inflow or outflow):
   o['mapPosition']={'x':.85,'y':0 if inflow and outflow else .85 if inflow else -.85,'z':[1,.75,.5][group-1]}
   o['mapEvidence']=['物理储水设施：按原型分类','流向依据：'+(' / '.join(incoming+outgoing+o['actions'])),'Z 轴依据现有策展分类；坐标为展示规则，不是量化研究结论']
 original=root/'public'/o['image'];original.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,original)
 thumb=root/'public'/o['thumbnail'];thumb.parent.mkdir(parents=True,exist_ok=True);im=ImageOps.exif_transpose(Image.open(p)).convert('RGB');im.thumbnail((1000,800));im.save(thumb,quality=88)
 data.append(o);mapping.append({'id':o['id'],'classification':group,'sequence':num,'excelRow':o['excelRow'],'title':o['title'],'filename':p.name,'status':o['matchingStatus']})
for o in data:
 scores=[]
 for other in data:
  if o['id']==other['id']:continue
  score=4*len(set(o['actions'])&set(other['actions']))+2*len(set(o['keywords'])&set(other['keywords']))+(o['positionNumber']==other['positionNumber'])
  if score:scores.append((score,other['id']))
 o['relatedIds']=[i for _,i in sorted(scores,reverse=True)[:5]]
(root/'src/data/archive.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
(root/'data-audit/image-mapping.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
with (root/'data-audit/image-mapping.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(mapping[0]));w.writeheader();w.writerows(mapping)
report={'visibleImages':len(data),'matchedRows':sum(not o['imageOnly'] for o in data),'imageOnly':sum(o['imageOnly'] for o in data),'excludedNoImageRows':sum(k not in images for k in bykey),'categories':{p:sum(o['curatorialPosition']==p for o in data) for p in positions},'actionEligible':sum(o['actionEligible'] for o in data),'mapPositioned':sum(o['mapPosition'] is not None for o in data),'excludedRecords':[{'id':o['id'],'excelRow':o['excelRow'],'title':o['title']} for k,o in bykey.items() if k not in images],'sourceWorkbook':str(pathlib.Path(args.excel).resolve()),'mapping':'用户确认：文件名 a-b，a 为六类编号，b 对应 Excel 第三列序号。无文字图片仅建立编号图像档案。'}
(root/'data-audit/report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
