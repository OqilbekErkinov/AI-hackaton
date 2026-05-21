import { useColorMode } from '@vueuse/core'

export const useColorTheme = () => {
  const mode = useColorMode({
    attribute: 'data-theme',
    modes: {
      light: 'light',
      dark: 'dark',
    },
    storageKey: 'nexora-theme',
  })

  return {
    mode, // auto, light, dark
    setTheme: (theme: 'light' | 'dark' | 'auto') => {
      mode.value = theme
    }
  }
}

export default useColorTheme
