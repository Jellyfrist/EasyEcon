// Keep only the formatting supported by the question editor. Question HTML can
// come from pasted content or the API, so never pass it straight to v-html.
const allowedTags = new Set(['B', 'STRONG', 'I', 'EM', 'U', 'BR', 'P', 'DIV', 'SPAN', 'IMG'])

function safeImageSource(src) {
  if (!src.trim()) return null
  if (/^data:image\/(png|jpeg|webp|gif);base64,[a-z0-9+/=]+$/i.test(src)) return src
  try {
    const url = new URL(src, window.location.origin)
    if (url.protocol === 'https:' || url.protocol === 'http:') return src
  } catch {
    // Invalid URLs are dropped.
  }
  return null
}

export function sanitizeQuestionHtml(html) {
  if (!html) return ''

  const source = new DOMParser().parseFromString(html, 'text/html')
  const output = document.createElement('div')

  function copyChildren(from, to) {
    for (const node of from.childNodes) {
      if (node.nodeType === Node.TEXT_NODE) {
        to.append(document.createTextNode(node.textContent))
      } else if (node.nodeType === Node.ELEMENT_NODE) {
        if (!allowedTags.has(node.tagName)) {
          copyChildren(node, to)
          continue
        }
        if (node.tagName === 'IMG') {
          const src = safeImageSource(node.getAttribute('src') || '')
          if (!src) continue
          const image = document.createElement('img')
          image.src = src
          image.alt = node.getAttribute('alt') || 'Question image'
          to.append(image)
          continue
        }
        const element = document.createElement(node.tagName.toLowerCase())
        if (node.tagName === 'SPAN') {
          const weight = node.style.fontWeight
          if (/^(normal|bold|[1-9]00)$/.test(weight)) element.style.fontWeight = weight
          const decoration = node.style.textDecorationLine
          if (decoration === 'underline') element.style.textDecorationLine = decoration
          const style = node.style.fontStyle
          if (style === 'italic') element.style.fontStyle = style
        }
        copyChildren(node, element)
        to.append(element)
      }
    }
  }

  copyChildren(source.body, output)
  return output.innerHTML
}

export function questionHtml(question) {
  if (question.text_html) return sanitizeQuestionHtml(question.text_html)
  const fallback = document.createElement('div')
  fallback.textContent = question.text || ''
  return fallback.innerHTML
}
