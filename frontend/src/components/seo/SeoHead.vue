<template>
  <!-- SeoHead 通过 JS 注入 head 标签，无可见 DOM -->
</template>

<script lang="ts">
import { defineComponent, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useLocaleStore } from '../../stores/locale'

export default defineComponent({
  name: 'SeoHead',
  props: {
    title: { type: String, default: '' },
    description: { type: String, default: '' },
    noindex: { type: Boolean, default: false },
  },
  setup(props) {
    const route = useRoute()
    const localeStore = useLocaleStore()
    const createdTags: HTMLElement[] = []

    function setMeta(name: string, content: string) {
      let el = document.querySelector(`meta[name="${name}"]`) as HTMLMetaElement
      if (!el) {
        el = document.createElement('meta')
        el.name = name
        document.head.appendChild(el)
        createdTags.push(el)
      }
      el.content = content
    }

    function setOg(property: string, content: string) {
      let el = document.querySelector(`meta[property="${property}"]`) as HTMLMetaElement
      if (!el) {
        el = document.createElement('meta')
        el.setAttribute('property', property)
        document.head.appendChild(el)
        createdTags.push(el)
      }
      el.content = content
    }

    function updateHead() {
      if (props.title) document.title = props.title
      if (props.description) setMeta('description', props.description)
      if (props.noindex) setMeta('robots', 'noindex, nofollow')

      // Open Graph
      if (props.title) setOg('og:title', props.title)
      if (props.description) setOg('og:description', props.description)
      setOg('og:url', window.location.href)
      setOg('og:type', 'website')

      // hreflang
      const base = window.location.origin + route.path
      setHreflang('zh', base)
      setHreflang('en', base)
    }

    function setHreflang(lang: string, href: string) {
      const selector = `link[hreflang="${lang}"]`
      let el = document.querySelector(selector) as HTMLLinkElement
      if (!el) {
        el = document.createElement('link')
        el.rel = 'alternate'
        el.hreflang = lang
        document.head.appendChild(el)
        createdTags.push(el)
      }
      el.href = href
    }

    onMounted(updateHead)
    watch(() => [props.title, props.description], updateHead)

    onUnmounted(() => {
      createdTags.forEach(el => el.remove())
    })

    return {}
  },
})
</script>
