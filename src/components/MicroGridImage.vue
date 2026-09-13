<script setup>
import {ref,watch} from 'vue'
const props=defineProps({object:Object,original:Boolean,eager:Boolean})
const failed=ref(false)
watch(()=>props.object.id,()=>failed.value=false)
</script>
<template><div class="micro-image" :class="{original,blank:failed}"><img v-if="object.image&&!failed" :src="original?object.image:(object.thumbnail||object.image)" :alt="object.title||object.id" :loading="eager?'eager':'lazy'" @error="failed=true"/></div></template>
