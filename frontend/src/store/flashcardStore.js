// manages flashcard sets, cards, and student progress

import { defineStore } from 'pinia'
import { ref } from 'vue'
import flashcardService from '../services/flashcardService'

export const useFlashcardStore = defineStore('flashcard', () => {

    // list of flashcard sets for current course
    const sets = ref([])

    // currently opened set with cards (teacher editor or student study view)
    const currentSet = ref(null)

    // student progress summary for current set
    const progress = ref(null)

    const loading = ref(false)
    const error = ref(null)

    function _setError(err) {
        error.value = err?.response?.data?.detail || err.message || 'something went wrong'
    }

    /**
     * teacher
     */


    // list all flashcard sets for a course (teacher's own sets)
    async function fetchSets(courseId) {
        loading.value = true
        error.value = null
        try {
            const res = await flashcardService.listSets(courseId)
            sets.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    // create a flashcard set for a course
    async function createSet(data) {
        loading.value = true
        error.value = null
        // if creation is successful, add the new set to the list and return it
        try {
            const res = await flashcardService.createSet(data)
            sets.value.push(res.data)
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    // only title and description can be updated, no content update here
    async function updateSet(setId, data) {
        loading.value = true
        error.value = null
        // after successful update, update the set in the list and currentSet if it is open
        try {
            // update it on server
            const res = await flashcardService.updateSet(setId, data)
            // update set in sets list
            const idx = sets.value.findIndex(s => s.id === setId)

            // if set is open in currentSet, update it there as well to keep in sync
            if (idx !== -1) sets.value[idx] = res.data
            // if currentSet is the one being updated, update it as well
            if (currentSet.value?.id === setId) currentSet.value = { ...currentSet.value, ...res.data }
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    // delete set and all its cards
    async function deleteSet(setId) {
        loading.value = true
        error.value = null
        try {
            await flashcardService.deleteSet(setId)
            sets.value = sets.value.filter(s => s.id !== setId)
            if (currentSet.value?.id === setId) currentSet.value = null
            return true
        } catch (err) {
            _setError(err)
            return false
        } finally {
            loading.value = false
        }
    }

    // add a card to a set
    async function addCard(setId, data) {
        loading.value = true
        error.value = null
        try {
            const res = await flashcardService.addCard(setId, data)
            // add card to currentSet if it is open
            if (currentSet.value?.id === setId) {
                currentSet.value.cards = [...(currentSet.value.cards || []), res.data]
                currentSet.value.card_count = (currentSet.value.card_count || 0) + 1
            }
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    // edit a card
    async function updateCard(cardId, data) {
        loading.value = true
        error.value = null
        // after successful update, update the card in currentSet to keep in sync
        try {
            const res = await flashcardService.updateCard(cardId, data)
            // update card inside currentSet
            if (currentSet.value?.cards) {
                const idx = currentSet.value.cards.findIndex(c => c.id === cardId)
                if (idx !== -1) currentSet.value.cards[idx] = res.data
            }
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    // delete a card
    async function deleteCard(cardId) {
        loading.value = true
        error.value = null
        try {
            await flashcardService.deleteCard(cardId)
            if (currentSet.value?.cards) {
                currentSet.value.cards = currentSet.value.cards.filter(c => c.id !== cardId)
                currentSet.value.card_count = Math.max(0, (currentSet.value.card_count || 1) - 1)
            }
            return true
        } catch (err) {
            _setError(err)
            return false
        } finally {
            loading.value = false
        }
    }

    
    /**
     * student
     */

    // start studying a set: fetch the set with cards and student progress for each card
    async function studySet(setId) {
        loading.value = true
        error.value = null
        try {
            const res = await flashcardService.studySet(setId)
            currentSet.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    // mark a card as known or learning
    async function markCard(flashcardId, status) {
        // optimistically update the card status in currentSet
        if (currentSet.value?.cards) {
            const card = currentSet.value.cards.find(c => c.id === flashcardId)
            if (card) card.status = status
        }
        try {
            await flashcardService.updateProgress({ flashcard_id: flashcardId, status })
        } catch (err) {
            _setError(err)
        }
    }

    // fetch progress summary for a set (known/learning/not started counts)
    async function fetchProgress(setId) {
        loading.value = true
        error.value = null
        try {
            const res = await flashcardService.getSetProgress(setId)
            progress.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    // clear current set and progress (e.g. when navigating away from study view)
    function clearCurrent() {
        currentSet.value = null
        progress.value = null
    }

    return {
        sets,
        currentSet,
        progress,
        loading,
        error,
        fetchSets,
        createSet,
        updateSet,
        deleteSet,
        addCard,
        updateCard,
        deleteCard,
        studySet,
        markCard,
        fetchProgress,
        clearCurrent,
    }
})