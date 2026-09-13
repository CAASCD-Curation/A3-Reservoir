<script setup>
import {computed,ref,onMounted,onBeforeUnmount,defineAsyncComponent} from 'vue'
import ArchiveCard from './ArchiveCard.vue'
import TextLayers from './TextLayers.vue'
import KeywordFlow from './KeywordFlow.vue'
import {view,level,action} from '../composables/useArchive'
const SpatialArchive=defineAsyncComponent(()=>import('./SpatialArchive.vue'))
const props=defineProps({objects:Array,paused:Boolean});defineEmits(['release'])
const container=ref(null),width=ref(900);let observer
onMounted(()=>{observer=new ResizeObserver(([e])=>width.value=e.contentRect.width);observer.observe(container.value)})
onBeforeUnmount(()=>observer?.disconnect())
const columns=computed(()=>{const max=width.value<500?3:Math.min(7,Math.max(3,Math.floor(width.value/135)));return 1+Math.round(level.value/100*(max-1))})
</script>
<template><div ref="container" class="archive-views" :class="{'high-density':level>70}"><SpatialArchive v-if="['MAP','DEPTH'].includes(view)" :key="view" :objects="objects" :mode="view" :action="action" :paused="paused" @release="$emit('release',$event)" @fallback="view='GRID'"/><KeywordFlow v-else-if="view==='FLOW'" :objects="objects" @release="$emit('release',$event)"/><TextLayers v-else-if="view==='LAYER'" :objects="objects" @release="$emit('release',$event)"/><div v-else class="hydraulic-grid" :style="{'--columns':columns,'--gap':`${26-level*.16}px`}" :data-columns="columns"><ArchiveCard v-for="(o,i) in objects" :key="o.id" :object="o" :style="{'--delay':`${-(i%7)*2}s`}" @release="$emit('release',$event)"/></div></div></template>
