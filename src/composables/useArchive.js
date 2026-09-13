import {ref,computed} from 'vue'
import records from '../data/archive.json'
export const archive=records.filter(o=>o.image)
export const position=ref(''),source=ref(''),action=ref('HOLD'),keywords=ref([]),view=ref('GRID'),level=ref(45)
export const filtered=computed(()=>archive.filter(o=>(!position.value||o.curatorialPosition===position.value)&&(!source.value||(source.value==='UNCLASSIFIED'?!o.sourceType.length:o.sourceType.includes(source.value)))&&keywords.value.every(k=>o.keywords.includes(k))))
export const keywordPool=[...new Set(archive.flatMap(o=>o.keywords))].sort((a,b)=>archive.filter(o=>o.keywords.includes(b)).length-archive.filter(o=>o.keywords.includes(a)).length)
export function reset(){position.value='';source.value='';keywords.value=[]}
export function toggleKeyword(k){keywords.value=keywords.value.includes(k)?keywords.value.filter(x=>x!==k):[...keywords.value,k]}
export function shared(a,b){const act=a.actions.filter(x=>b.actions.includes(x));const keys=a.keywords.filter(x=>b.keywords.includes(x));return act.length?`共同动作 / SHARED ACTION · ${act.join(' → ')}`:keys.length?`共同关键词 / SHARED KEYWORD · ${keys.join(' / ')}`:'同一策展位置 / SHARED POSITION'}
