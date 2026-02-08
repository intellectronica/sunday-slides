import { defineConfig } from 'unocss'

export default defineConfig({
  shortcuts: {
    'bg-main': 'bg-[var(--slide-bg)] text-black',
  },
  theme: {
    colors: {
      primary: '#000000',
      background: '#2BD3EC',
    },
  },
})
