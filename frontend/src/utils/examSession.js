// Keep the existing ExamSessionCreate payload used by the launch page.
export function buildSessionPayload(templateId, form, defaultTitle = '') {
    const payload = {
        template_id: Number(templateId),
        title: form.title || defaultTitle,
    }
    if (form.instructions) payload.instructions = form.instructions
    if (form.available_from) payload.available_from = new Date(form.available_from).toISOString()
    if (form.available_until) payload.available_until = new Date(form.available_until).toISOString()
    if (form.time_limit_minutes) payload.time_limit_minutes = form.time_limit_minutes
    payload.max_attempts = form.max_attempts ?? 1
    return payload
}
