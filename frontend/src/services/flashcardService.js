// covers all /flashcards endpoints for teacher and student

import api from './api'

const flashcardService = {

    /*
        teacher: flashcard sets
        - POST   /flashcards/sets                create a flashcard set for a course
        - GET    /flashcards/sets                list all sets for a course (teacher's own sets)
        - PATCH  /flashcards/sets/{set_id}       update set title or description
        - DELETE /flashcards/sets/{set_id}       delete set and all its cards
    */

    // create a flashcard set for a course
    createSet(data) {
        // data: { course_id, title, description }
        return api.post('/flashcards/sets', data)
    },

    // list all sets for a course (teacher's own sets)
    listSets(courseId) {
        return api.get('/flashcards/sets', { params: { course_id: courseId } })
    },

    // update set title or description
    updateSet(setId, data) {
        return api.patch(`/flashcards/sets/${setId}`, data)
    },

    // delete set and all its cards
    deleteSet(setId) {
        return api.delete(`/flashcards/sets/${setId}`)
    },

    /*
        teacher: flashcard cards
        - GET    /flashcards/sets/{set_id}/cards     get all cards in a set
        - POST   /flashcards/sets/{set_id}/cards     add a card to a set
        - PATCH  /flashcards/cards/{card_id}         edit a card
        - DELETE /flashcards/cards/{card_id}         delete a card
    */

    // get all cards in a set (teacher only)
    getCards(setId) {
        return api.get(`/flashcards/sets/${setId}/cards`)
    },

    // add a card to a set
    addCard(setId, data) {
        // data: { term, definition, hint, image_url, order_index }
        return api.post(`/flashcards/sets/${setId}/cards`, data)
    },

    // edit a card
    updateCard(cardId, data) {
        return api.patch(`/flashcards/cards/${cardId}`, data)
    },

    // delete a card
    deleteCard(cardId) {
        return api.delete(`/flashcards/cards/${cardId}`)
    },

    // upload image to supabase storage, returns { url: '...' }
    uploadImage(file) {
        const form = new FormData()
        form.append('file', file)
        return api.post('/flashcards/upload-image', form, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
    },

    /* 
        recycle bin
    */

    // get all deleted sets and cards for a course
    getRecycleBin(courseId) {
        return api.get('/flashcards/recycle-bin', { params: { course_id: courseId } })
    },

    // restore a soft-deleted set and all its cards
    restoreSet(setId) { return api.post(`/flashcards/sets/${setId}/restore`) },

    // restore a single soft-deleted card
    restoreCard(cardId) { return api.post(`/flashcards/cards/${cardId}/restore`) },

    // permanently delete set from db and supabase storage
    permanentDeleteSet(setId) { return api.delete(`/flashcards/sets/${setId}/permanent`) },

    /*
        student endpoints:
        - GET /flashcards/sets/{set_id}/study       get set with all cards and student's progress injected
        - POST /flashcards/progress                 mark a card as known or learning
        - GET  /flashcards/sets/{set_id}/progress   get progress summary for a set (known/learning/not started counts)
    */

    // get set with all cards and student's progress injected
    studySet(setId) {
        return api.get(`/flashcards/sets/${setId}/study`)
    },

    // mark a card as known or learning
    updateProgress(data) {
        // data: { flashcard_id, status: "known" | "learning" }
        return api.post('/flashcards/progress', data)
    },

    // get progress summary for a set (known/learning/not started counts)
    getSetProgress(setId) {
        return api.get(`/flashcards/sets/${setId}/progress`)
    },
}

export default flashcardService