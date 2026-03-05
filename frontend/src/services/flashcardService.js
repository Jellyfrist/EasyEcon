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
        - POST   /flashcards/sets/{set_id}/cards     add a card to a set
        - PATCH  /flashcards/cards/{card_id}         edit a card
        - DELETE /flashcards/cards/{card_id}         delete a card
    */

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

    // get all cards in a set (teacher only)
    // GET /flashcards/sets/{set_id}/cards
    getCards(setId) {
        return api.get(`/flashcards/sets/${setId}/cards`)
    },


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