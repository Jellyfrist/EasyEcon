/**
 * useFlashcardEditor.js
 * Composable for the teacher's flashcard editor.
 * Manages local card list with add / edit / remove before save.
 */

import { ref, computed } from 'vue'
import {
  createSet,
  updateSet,
  addCard,
  updateCard,
  deleteCard,
  fetchSetByPage,
} from '@/services/flashcardService'

let _localIdCounter = 0
function localId() { return `local_${++_localIdCounter}` }

export function useFlashcardEditor(pageId) {
  // State
  const setId = ref(null)         // null = not yet saved to server
  const title = ref('')
  const description = ref('')

  /** Each card: { _lid, id?, term, definition, hint, image_url, order_index, _dirty, _isNew } */
  const localCards = ref([])

  const isSaving = ref(false)
  const isLoading = ref(false)
  const error = ref(null)
  const lastSaved = ref(null)

  // Computed
  const totalCards = computed(() => localCards.value.length)

  const incompleteCount = computed(() =>
    localCards.value.filter(c => !c.term.trim() || !c.definition.trim()).length
  )

  const completionPct = computed(() => {
    if (!totalCards.value) return 0
    const complete = totalCards.value - incompleteCount.value
    return Math.round((complete / totalCards.value) * 100)
  })

  // Load existing
  async function load() {
    if (!pageId) return
    isLoading.value = true
    error.value = null
    try {
      const data = await fetchSetByPage(pageId)
      setId.value = data.id
      title.value = data.title
      description.value = data.description ?? ''
      localCards.value = data.cards.map((c, i) => ({
        _lid: localId(),
        id: c.id,
        term: c.term,
        definition: c.definition,
        hint: c.hint ?? '',
        image_url: c.image_url ?? '',
        order_index: i,
        _dirty: false,
        _isNew: false,
      }))
    } catch (e) {
      // 404 → new set, ignore error
      if (e?.response?.status !== 404) {
        error.value = e?.response?.data?.detail ?? 'Failed to load'
      }
    } finally {
      isLoading.value = false
    }
  }

  // Card manipulation

  function addEmptyCard() {
    localCards.value.push({
      _lid: localId(),
      id: null,
      term: '',
      definition: '',
      hint: '',
      image_url: '',
      order_index: localCards.value.length,
      _dirty: true,
      _isNew: true,
    })
  }

  function updateLocalCard(lid, field, value) {
    const card = localCards.value.find(c => c._lid === lid)
    if (!card) return
    card[field] = value
    card._dirty = true
  }

  function removeLocalCard(lid) {
    localCards.value = localCards.value.filter(c => c._lid !== lid)
  }

  function setImageUrl(lid, url) {
    updateLocalCard(lid, 'image_url', url)
  }

  // Persistence

  /**
   * Full save: creates set if new, then syncs all dirty/new cards.
   */
  async function save() {
    isSaving.value = true
    error.value = null
    try {
      // 1. Create or update the set header
      if (!setId.value) {
        const newSet = await createSet({
          learning_page_id: pageId,
          title: title.value,
          description: description.value,
          cards: localCards.value
            .filter(c => c.term.trim() && c.definition.trim())
            .map((c, i) => ({
              term: c.term,
              definition: c.definition,
              hint: c.hint || null,
              image_url: c.image_url || null,
              order_index: i,
            })),
        })
        setId.value = newSet.id
        // Map server ids back to local cards
        newSet.cards.forEach((sc, i) => {
          if (localCards.value[i]) {
            localCards.value[i].id = sc.id
            localCards.value[i]._isNew = false
            localCards.value[i]._dirty = false
          }
        })
      } else {
        // Update set header
        await updateSet(setId.value, {
          title: title.value,
          description: description.value,
        })

        // Sync individual dirty/new cards
        for (const card of localCards.value) {
          if (!card.term.trim() || !card.definition.trim()) continue
          if (!card._dirty) continue

          const payload = {
            term: card.term,
            definition: card.definition,
            hint: card.hint || null,
            image_url: card.image_url || null,
            order_index: card.order_index,
          }

          if (card._isNew) {
            const saved = await addCard(setId.value, payload)
            card.id = saved.id
            card._isNew = false
          } else if (card.id) {
            await updateCard(card.id, payload)
          }
          card._dirty = false
        }
      }

      lastSaved.value = new Date()
    } catch (e) {
      error.value = e?.response?.data?.detail ?? 'Save failed'
    } finally {
      isSaving.value = false
    }
  }

  async function removeCardFromServer(lid) {
    const card = localCards.value.find(c => c._lid === lid)
    if (card?.id) {
      try {
        await deleteCard(card.id)
      } catch {
        // soft fail
      }
    }
    removeLocalCard(lid)
  }

  return {
    // state
    setId,
    title,
    description,
    localCards,
    isSaving,
    isLoading,
    error,
    lastSaved,
    // computed
    totalCards,
    incompleteCount,
    completionPct,
    // actions
    load,
    addEmptyCard,
    updateLocalCard,
    removeLocalCard,
    setImageUrl,
    removeCardFromServer,
    save,
  }
}