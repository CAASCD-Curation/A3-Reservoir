<script setup>
import {ref,computed} from 'vue'
import {archive,keywordPool} from '../composables/useArchive'
import ArchiveCard from './ArchiveCard.vue'
defineEmits(['release']);const first=ref(''),second=ref('')
const matches=computed(()=>first.value&&second.value?archive.filter(o=>o.keywords.includes(first.value)&&o.keywords.includes(second.value)):[])
</script>
<template><section id="relations" class="relations-panel"><header><p class="mono">TWO WORDS / ONE SHARED SPACE</p><h2>RELATIONS <span>交叉关系</span></h2><p>两个关键词，共同指向哪些案例？</p></header><div class="relation-pickers"><label>关键词 A / KEYWORD A<select v-model="first"><option value="">选择 / SELECT</option><option v-for="k in keywordPool" :value="k" :key="k" :disabled="k===second">{{k}}</option></select></label><span>∩</span><label>关键词 B / KEYWORD B<select v-model="second"><option value="">选择 / SELECT</option><option v-for="k in keywordPool" :value="k" :key="k" :disabled="k===first">{{k}}</option></select></label><button @click="first='';second=''">重置 / RESET ↺</button></div><p class="relation-count mono" aria-live="polite">{{first&&second?`${first} ∩ ${second} — ${matches.length} OBJECTS / 共同案例`:'选择两个不同关键词 / SELECT TWO KEYWORDS'}}</p><div class="relation-results" v-if="matches.length"><ArchiveCard v-for="o in matches" :key="o.id" :object="o" @release="$emit('release',$event)"/></div><p v-else-if="first&&second" class="relation-empty">这两个关键词暂无共同案例。<small>NO SHARED OBJECTS IN THIS ARCHIVE.</small></p></section></template>
