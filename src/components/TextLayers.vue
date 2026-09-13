<script setup>
import {computed} from 'vue'
import {positions,positionCN} from '../data/system'
const props=defineProps({objects:Array});defineEmits(['release'])
const groups=computed(()=>positions.map((p,i)=>({p,cn:positionCN[i],i,objects:props.objects.filter(o=>o.curatorialPosition===p).sort((a,b)=>(b.sortYear??-Infinity)-(a.sortYear??-Infinity))})).filter(g=>g.objects.length))
</script>
<template><section class="text-layers"><h3 class="chronology-title">时间蓄水池 / CHRONOLOGICAL BASINS</h3><p class="layer-note">各分类独立按年代由新到旧排列，越老越深；年代不明的图像单列在底部。<small>NEWER ABOVE · OLDER BELOW</small></p><div class="time-basins"><section v-for="g in groups" :key="g.p" class="text-basin" :data-position="g.i+1"><header><span class="mono">{{'ABCDEF'[g.i]}} / {{g.p}}</span><h3>{{g.cn}}</h3></header><template v-for="(o,j) in g.objects" :key="o.id"><p v-if="o.sortYear===null&&(j===0||g.objects[j-1].sortYear!==null)" class="unknown-date">年代未标注 / UNDATED</p><button class="layer-row" @click="$emit('release',o)" :data-year="o.sortYear"><span class="mono">{{o.id}}</span><strong>{{o.title||'图像档案 / IMAGE ARCHIVE'}}</strong><span v-if="o.placeAndPeriod" class="layer-period">{{o.placeAndPeriod}}</span><span>↗</span></button></template></section></div></section></template>
