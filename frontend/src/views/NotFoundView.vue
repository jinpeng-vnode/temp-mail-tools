<template>
  <div class="not-found-view">
    <a-result status="404" :title="$t('notFound.title')" :sub-title="$t('notFound.desc')">
      <template #extra>
        <a-button type="primary" @click="$router.push('/')">{{ $t('notFound.home') }}</a-button>
      </template>
    </a-result>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({ name: 'NotFoundView' })
</script>

<style scoped>
.not-found-view { display: flex; align-items: center; justify-content: center; min-height: 60vh; }
</style>
