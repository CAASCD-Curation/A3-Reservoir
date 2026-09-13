<script setup>
import {ref,computed,onMounted,onBeforeUnmount,watch} from 'vue'
import * as THREE from 'three'
import {OrbitControls} from 'three/addons/controls/OrbitControls.js'
import ArchiveCard from './ArchiveCard.vue'
const props=defineProps({objects:Array,mode:String,action:String,paused:Boolean})
const emit=defineEmits(['release','fallback'])
const host=ref(null),error=ref(false),loading=ref(true),hovered=ref(null),wheel=ref(false)
const positioned=computed(()=>props.mode==='MAP'?props.objects.filter(o=>o.mapPosition):props.objects)
const unplaced=computed(()=>props.mode==='MAP'?props.objects.filter(o=>!o.mapPosition):[])
let renderer,scene,camera,controls,group,frame,resizeObserver,visibilityObserver,visible=false,disposed=false,down=null,raycaster,pointer
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches
const cleanup=[]
const axisLabels=ref([]);let mapAnchors=[]
function label(text,position,size=4.3){
 const canvas=document.createElement('canvas');canvas.width=640;canvas.height=140
 const ctx=canvas.getContext('2d');ctx.fillStyle='#f3f3ed';ctx.fillRect(0,0,640,140);ctx.fillStyle='#123deb';ctx.textAlign='center'
 text.split('\n').forEach((s,i)=>{ctx.font=i?'26px sans-serif':'30px monospace';ctx.fillText(s,320,50+i*45)})
 const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace
 const sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,depthTest:false,transparent:true}));sprite.position.copy(position);sprite.scale.set(size,size*140/640,1);scene.add(sprite)
}
function zoom(f){if(!camera)return;camera.position.multiplyScalar(f);camera.position.setLength(THREE.MathUtils.clamp(camera.position.length(),12,48));controls.update();render()}
function render(){
 if(renderer&&scene&&camera){renderer.render(scene,camera)
  if(mapAnchors.length&&host.value){const w=host.value.clientWidth,h=host.value.clientHeight
   const next=mapAnchors.map(a=>{const p=a.p.clone().project(camera);return {title:a.title,cn:a.cn,x:Math.max(62,Math.min(w-62,(p.x+1)/2*w)),y:Math.max(27,Math.min(h-27,(-p.y+1)/2*h))}})
   if(next.some((a,i)=>!axisLabels.value[i]||Math.abs(a.x-axisLabels.value[i].x)>.2||Math.abs(a.y-axisLabels.value[i].y)>.2))axisLabels.value=next
  }
 }
}
function disposeCards(){if(!group)return;for(const mesh of [...group.children]){group.remove(mesh);mesh.geometry.dispose();mesh.material.map?.dispose();mesh.material.dispose()}}
function populate(){
 if(!group)return;disposeCards();hovered.value=null
 const records=positioned.value
 records.forEach((o,i)=>{
  const c=document.createElement('canvas');c.width=512;c.height=390;const ctx=c.getContext('2d');ctx.fillStyle='#f3f3ed';ctx.fillRect(0,0,512,390);ctx.strokeStyle='#123deb';ctx.strokeRect(1,1,510,388);ctx.fillStyle='#123deb';ctx.font='22px monospace';ctx.fillText(o.id,14,30);ctx.font='20px sans-serif';ctx.fillText((o.title||'图像档案 / IMAGE ARCHIVE').slice(0,35),14,374)
  const texture=new THREE.CanvasTexture(c);texture.colorSpace=THREE.SRGBColorSpace
  const material=new THREE.MeshBasicMaterial({map:texture,side:THREE.DoubleSide,transparent:true})
  const mesh=new THREE.Mesh(new THREE.PlaneGeometry(props.mode==='MAP'?2.5:2.25,props.mode==='MAP'?1.9:1.71),material)
  let base
  if(props.mode==='MAP'){
   const p=o.mapPosition
   // A small, deterministic label spread separates coincident records, without changing semantic coordinates.
   const same=records.filter(x=>JSON.stringify(x.mapPosition)===JSON.stringify(p));const j=same.findIndex(x=>x.id===o.id);const spread=(j-(same.length-1)/2)*.52
   base=new THREE.Vector3(p.x*8+(j%4-Math.min(same.length-1,3)/2)*2.4,p.y*8+(Math.floor(j/4)-Math.floor((same.length-1)/4)/2)*2.1,p.z*8)
  }else{const y=records.length===1?0:1-2*(i+.5)/records.length;const r=Math.sqrt(1-y*y);const phi=i*2.399963;const radius=8.8;base=new THREE.Vector3(Math.cos(phi)*r*radius,y*radius,Math.sin(phi)*r*radius)}
  mesh.position.copy(base);mesh.userData={object:o,base};mesh.lookAt(camera.position);group.add(mesh)
  const img=new Image();img.onload=()=>{if(disposed||!group.children.includes(mesh))return;const scale=Math.min(484/img.width,310/img.height);const w=img.width*scale,h=img.height*scale;ctx.drawImage(img,(512-w)/2,42+(310-h)/2,w,h);texture.needsUpdate=true;render()};img.src=o.thumbnail||o.image
 })
 render()
}
function tick(){
 if(!visible||disposed)return
 if(!props.paused){
  const factor=hovered.value ? .025 : .055
  for(const mesh of group.children){
   const {object,base}=mesh.userData;const target=base.clone();let opacity=1,scale=1
   if(object.actionEligible){
    if(props.mode==='DEPTH'){
     const multipliers={COLLECT:.62,HOLD:1,ACCUMULATE:.79,FILTER:1,SETTLE:1,PRESSURIZE:.70,'REACH LIMIT':1.13,OVERFLOW:1.35,RELEASE:1.22,EMPTY:1.55,RECYCLE:1}
     target.multiplyScalar(multipliers[props.action]??1)
     if(props.action==='SETTLE')target.y-=3
     if(props.action==='RELEASE')target.z+=2
    }
    if(props.action==='FILTER')opacity=.40
    if(props.action==='EMPTY')opacity=.07
    if(props.action==='PRESSURIZE')scale=.83
    if(props.action==='REACH LIMIT')scale=1.08
   }
   if(hovered.value?.id===object.id)scale*=1.1
   mesh.position.lerp(target,reduced?1:factor);mesh.scale.lerp(new THREE.Vector3(scale,scale,scale),reduced?1:factor);mesh.material.opacity=THREE.MathUtils.lerp(mesh.material.opacity,opacity,reduced?1:factor);mesh.lookAt(camera.position)
  }
  controls.update();render()
 }
 frame=requestAnimationFrame(tick)
}
function pick(e){
 const rect=renderer.domElement.getBoundingClientRect();pointer.set((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);raycaster.setFromCamera(pointer,camera)
 const hit=raycaster.intersectObjects(group.children).find(h=>h.object.material.opacity>.15);return hit?.object.userData.object||null
}
onMounted(()=>{
 try{
  scene=new THREE.Scene();scene.background=new THREE.Color('#f3f3ed');camera=new THREE.PerspectiveCamera(43,1,.1,150);camera.position.set(...(props.mode==='MAP'?[22,16,28]:[0,2,28]))
  renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));host.value.appendChild(renderer.domElement);renderer.domElement.setAttribute('aria-label',props.mode==='MAP'?'三维坐标图，拖动旋转':'球形图像档案，拖动旋转')
  controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.07;controls.enableZoom=false;controls.enablePan=false;controls.minDistance=12;controls.maxDistance=48
  group=new THREE.Group();scene.add(group);raycaster=new THREE.Raycaster();pointer=new THREE.Vector2()
  if(props.mode==='MAP'){
   const specs=[[[1,0,0],'X+ PHYSICAL\n物理存在'],[[-1,0,0],'X− NON-PHYSICAL\n非物理存在'],[[0,1,0],'Y+ INFLOW\n流入'],[[0,-1,0],'Y− OUTFLOW\n流出'],[[0,0,1],'Z+ PROTOTYPE\n原型'],[[0,0,-1],'Z− TRANSFORMATION\n变型']]
   specs.forEach(([v,title])=>{const dir=new THREE.Vector3(...v);scene.add(new THREE.ArrowHelper(dir,new THREE.Vector3(),11,0x123deb,.42,.18));mapAnchors.push({title:title.split('\n')[0],cn:title.split('\n')[1],p:dir.clone().multiplyScalar(12.5)})})
  }else{label('RESERVOIR / 蓄水池\nSPHERICAL ARCHIVE / 球形档案',new THREE.Vector3(0,0,0),4.5)}
  populate()
  const move=e=>{hovered.value=pick(e);renderer.domElement.style.cursor=hovered.value?'pointer':'grab'}
  const pd=e=>{down=[e.clientX,e.clientY]};const pu=e=>{const o=pick(e);if(down&&Math.hypot(e.clientX-down[0],e.clientY-down[1])<5&&o)emit('release',o);down=null};const leave=()=>hovered.value=null
  for(const [event,fn] of [['pointermove',move],['pointerdown',pd],['pointerup',pu],['pointerleave',leave]]){renderer.domElement.addEventListener(event,fn);cleanup.push(()=>renderer.domElement.removeEventListener(event,fn))}
  resizeObserver=new ResizeObserver(()=>{const w=host.value.clientWidth,h=host.value.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();render()});resizeObserver.observe(host.value)
  visibilityObserver=new IntersectionObserver(([e])=>{visible=e.isIntersecting;cancelAnimationFrame(frame);if(visible)tick()});visibilityObserver.observe(host.value);loading.value=false
 }catch(e){loading.value=false;error.value=true;console.warn('WebGL unavailable',e)}
})
watch(()=>props.objects,populate);watch(wheel,v=>{if(controls)controls.enableZoom=v})
onBeforeUnmount(()=>{disposed=true;cancelAnimationFrame(frame);resizeObserver?.disconnect();visibilityObserver?.disconnect();cleanup.forEach(f=>f());controls?.dispose();scene?.traverse(o=>{o.geometry?.dispose();if(o.material){o.material.map?.dispose();o.material.dispose()}});renderer?.dispose();renderer?.domElement.remove()})
</script>
<template><section class="spatial-archive"><div class="spatial-heading mono"><span>{{mode==='MAP'?'SPATIAL COORDINATES / 空间坐标':'SPHERICAL ARCHIVE / 球形档案'}}</span><span>{{positioned.length}} / {{objects.length}} OBJECTS 图像</span></div><div class="spatial-stage"><div ref="host" class="orbital-canvas" tabindex="0" @keydown.up.prevent="zoom(.93)" @keydown.down.prevent="zoom(1.07)"><p v-if="loading" class="scene-status">载入空间档案 / LOADING SPACE</p><div v-if="error" class="scene-status">三维暂不可用 / 3D UNAVAILABLE<button @click="$emit('fallback')">返回二维 / OPEN GRID ↗</button></div></div><div v-for="a in axisLabels" :key="a.title" class="axis-label" :style="{left:a.x+'px',top:a.y+'px'}"><strong>{{a.cn}}</strong><small>{{a.title}}</small></div><div v-if="hovered" class="orbital-hover"><span class="mono">{{hovered.id}} / RELEASE 展开 ↗</span><strong>{{hovered.title||'图像档案 / IMAGE ARCHIVE'}}</strong><small v-if="hovered.placeAndPeriod">{{hovered.placeAndPeriod}}</small><small v-if="mode==='MAP'">{{hovered.mapEvidence.slice(0,2).join(' · ')}}</small></div></div><div class="orbital-controls"><span>拖动旋转 / DRAG TO ORBIT</span><button @click="zoom(.85)" aria-label="放大 / Zoom in">＋</button><button @click="zoom(1.15)" aria-label="缩小 / Zoom out">−</button><button @click="wheel=!wheel" :aria-pressed="wheel">滚轮 / WHEEL {{wheel?'ON':'OFF'}}</button><button @click="$emit('fallback')">二维 / 2D ↗</button></div><p v-if="mode==='MAP'" class="map-note">坐标依据已标注的分类、动作与流向关键词；同坐标图片微错开以便点击。未提供完整属性的图像列在下方，不猜测坐标。</p><details v-if="unplaced.length" class="unplaced"><summary>待定位图像 / UNPOSITIONED ARCHIVES <span>{{unplaced.length}} +</span></summary><p>原表未提供完整的物理属性或流入／流出依据。</p><div class="unplaced-grid"><ArchiveCard v-for="o in unplaced" :key="o.id" :object="o" @release="$emit('release',$event)"/></div></details></section></template>
