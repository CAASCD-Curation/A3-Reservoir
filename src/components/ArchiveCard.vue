<script setup>
import MicroGridImage from './MicroGridImage.vue'
defineProps({object:Object});defineEmits(['release'])
</script>
<template><button class="archive-card" @click="$emit('release',object)" :aria-label="`展开 / RELEASE ${object.id} ${object.title}`"><div class="card-top mono"><span>{{object.id}}</span><span>{{'ABCDEF'[object.positionNumber-1]}} ↗</span></div><MicroGridImage :object="object"/><h3 v-if="object.title">{{object.title}}</h3><p v-if="object.placeAndPeriod" class="period">{{object.placeAndPeriod}}</p><span v-if="object.imageOnly" class="image-only-label">图像档案 / IMAGE ARCHIVE</span></button></template>
