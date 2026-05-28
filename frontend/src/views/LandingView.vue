<template>
  <div class="landing-view">
    <a-skeleton v-if="loading" active :paragraph="{ rows: 8 }" />

    <template v-else-if="landingData">
      <!-- SEO Head -->
      <SeoHead :title="landingData.title" :description="landingData.description" />

      <!-- Hero 区 -->
      <section class="landing-hero">
        <h1>{{ landingData.title }}</h1>
        <p class="hero-desc">{{ landingData.description }}</p>
        <a-button type="primary" size="large" @click="scrollToGenerator">
          {{ $t('landing.cta') }}
        </a-button>
      </section>

      <!-- 邮箱生成器 -->
      <div ref="generatorRef">
        <MailboxGenerator />
      </div>

      <!-- 功能特点 -->
      <section class="features-section">
        <h2>{{ $t('landing.features') }}</h2>
        <a-row :gutter="[24, 24]">
          <a-col :xs="24" :sm="8" v-for="feature in features" :key="feature.icon">
            <a-card hoverable class="feature-card">
              <div class="feature-icon">{{ feature.icon }}</div>
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.desc }}</p>
            </a-card>
          </a-col>
        </a-row>
      </section>

      <!-- 使用步骤 -->
      <section class="steps-section">
        <h2>{{ $t('landing.steps') }}</h2>
        <a-steps :current="-1" direction="horizontal">
          <a-step :title="$t('landing.step1')" />
          <a-step :title="$t('landing.step2')" />
          <a-step :title="$t('landing.step3')" />
        </a-steps>
      </section>

      <!-- FAQ -->
      <section v-if="landingData.faq && landingData.faq.length" class="faq-section">
        <h2>{{ $t('landing.faq') }}</h2>
        <a-collapse>
          <a-collapse-panel v-for="(item, idx) in landingData.faq" :key="idx" :header="item.question">
            <p>{{ item.answer }}</p>
          </a-collapse-panel>
        </a-collapse>
      </section>
    </template>

    <a-result v-else status="404" title="Page Not Found">
      <template #extra>
        <a-button type="primary" @click="$router.push('/')">{{ $t('notFound.home') }}</a-button>
      </template>
    </a-result>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import MailboxGenerator from '../components/mailbox/MailboxGenerator.vue'
import SeoHead from '../components/seo/SeoHead.vue'

interface LandingData {
  title: string
  description: string
  faq: { question: string; answer: string }[]
}

export default defineComponent({
  name: 'LandingView',
  components: { MailboxGenerator, SeoHead },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const { t } = useI18n()
    const loading = ref(true)
    const landingData = ref<LandingData | null>(null)
    const generatorRef = ref<HTMLElement | null>(null)

    const features = computed(() => [
      { icon: '🔒', title: t('landing.privacy'), desc: t('landing.privacyDesc') },
      { icon: '⚡', title: t('landing.instant'), desc: t('landing.instantDesc') },
      { icon: '🗑️', title: t('landing.autoDelete'), desc: t('landing.autoDeleteDesc') },
    ])

    async function fetchLanding() {
      const slug = route.params.slug as string
      try {
        const res = await fetch(`/api/seo/landing/${slug}`)
        if (!res.ok) { landingData.value = null; return }
        landingData.value = await res.json()
      } catch {
        landingData.value = null
      } finally {
        loading.value = false
      }
    }

    function scrollToGenerator() {
      generatorRef.value?.scrollIntoView({ behavior: 'smooth' })
    }

    onMounted(fetchLanding)

    return { loading, landingData, features, generatorRef, scrollToGenerator }
  },
})
</script>

<style scoped>
.landing-view { max-width: 840px; margin: 0 auto; }
.landing-hero { text-align: center; padding: 48px 0 32px; }
.landing-hero h1 { font-size: 30px; font-weight: 600; margin-bottom: 16px; }
.hero-desc { font-size: 16px; color: rgba(0, 0, 0, 0.65); margin-bottom: 24px; }
.features-section, .steps-section, .faq-section { margin-top: 48px; }
.features-section h2, .steps-section h2, .faq-section h2 { text-align: center; margin-bottom: 24px; }
.feature-card { text-align: center; }
.feature-icon { font-size: 32px; margin-bottom: 12px; }
.feature-card h3 { margin-bottom: 8px; }
.feature-card p { color: rgba(0, 0, 0, 0.65); }

@media (max-width: 768px) {
  .landing-hero { padding: 24px 0 16px; }
  .landing-hero h1 { font-size: 24px; }
}
</style>
