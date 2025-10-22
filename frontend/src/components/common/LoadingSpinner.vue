<template>
  <div 
    class="animate-spin rounded-full border-2 border-gray-300 border-t-primary-600"
    :class="sizeClasses"
  ></div>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  props: {
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
    }
  },
  computed: {
    sizeClasses() {
      const sizes = {
        sm: 'w-4 h-4',
        md: 'w-6 h-6',
        lg: 'w-8 h-8',
        xl: 'w-12 h-12'
      }
      return sizes[this.size]
    }
  }
}
</script>