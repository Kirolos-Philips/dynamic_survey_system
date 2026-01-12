class SurveyRenderer {
    constructor(containerId, surveyId, language) {
        this.container = document.getElementById(containerId);
        this.surveyId = surveyId;
        this.language = language;
        this.surveyData = null;
        this.formValues = {};
        this.currentStep = 0;
        this.sections = [];
        this.submissionId = null;
        this.isSaving = false;
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async init() {
        try {
            const response = await fetch(`/api/surveys/${this.surveyId}/data/`, {
                headers: { 'Accept-Language': this.language }
            });
            this.surveyData = await response.json();
            this.prepareSections();
            this.render();
            this.applyInitialLogic();
            this.updateStepVisibility();

            // Initialize submission
            await this.ensureSubmission();
        } catch (error) {
            console.error('Error loading survey:', error);
            this.container.innerHTML = '<div class="error-msg">Failed to load survey.</div>';
        }
    }

    async ensureSubmission() {
        if (this.submissionId) return;
        try {
            const response = await fetch('/api/submissions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ survey: this.surveyId })
            });
            const data = await response.json();
            this.submissionId = data.id;
        } catch (error) {
            console.error('Error creating submission:', error);
        }
    }

    async saveProgress(isCompleted = false) {
        if (!this.submissionId || this.isSaving) return;

        this.isSaving = true;
        const currentSection = this.sections[this.currentStep];
        const answers = currentSection.questions.map(q => ({
            question: q.id,
            value: this.formValues[q.id]
        })).filter(a => a.value !== undefined && a.value !== null && a.value !== '');

        try {
            const url = this.submissionId ? `/api/submissions/${this.submissionId}/` : '/api/submissions/';
            const method = this.submissionId ? 'PATCH' : 'POST';
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    survey: this.surveyId,
                    answers: answers,
                    is_completed: isCompleted
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(Object.values(errorData).flat().join(', '));
            }

            if (isCompleted) {
                this.renderSuccess();
            }
        } catch (error) {
            console.error('Error saving answers:', error);
            alert(`Error: ${error.message}`);
        } finally {
            this.isSaving = false;
        }
    }

    renderSuccess() {
        this.container.innerHTML = `
            <div class="survey-card" style="text-align: center; padding: 4rem 2rem;">
                <div style="font-size: 4rem; margin-bottom: 1.5rem;">🎉</div>
                <h2 style="color: var(--accent-color); margin-bottom: 1rem;">Submission Successful!</h2>
                <p style="color: var(--text-dim);">Thank you for taking the time to complete this survey.</p>
                <button onclick="location.reload()" class="nav-btn next" style="max-width: 200px; margin: 2rem auto 0;">Back to Start</button>
            </div>
        `;
    }

    prepareSections() {
        const { questions_map } = this.surveyData;
        const sectionMap = {};
        Object.values(questions_map).forEach(q => {
            if (!sectionMap[q.section]) {
                sectionMap[q.section] = [];
            }
            sectionMap[q.section].push(q);
        });
        this.sections = Object.keys(sectionMap).map(title => ({
            title,
            questions: sectionMap[title]
        }));
    }

    render() {
        const { title, description } = this.surveyData;

        // Render Sidebar Steps
        this.renderSidebar();

        let html = `
            <div class="survey-header">
                <h1>${title}</h1>
                <p class="description">${description}</p>
            </div>
            
            <div class="progress-bar-container">
                <div class="progress-bar-fill" id="progress-fill"></div>
            </div>

            <form id="survey-form">
                <div id="steps-container">
        `;

        this.sections.forEach((section, index) => {
            html += `
                <div class="survey-section" data-step="${index}" style="display: ${index === 0 ? 'block' : 'none'}">
                    <h2 class="section-title">${section.title}</h2>
                    <div class="questions-container">
                        ${section.questions.map(q => this.renderQuestion(q)).join('')}
                    </div>
                </div>
            `;
        });

        html += `
                </div>
                <div class="form-footer">
                    <button type="button" id="prev-btn" class="nav-btn prev" style="display: none">Back</button>
                    <button type="button" id="next-btn" class="nav-btn next">Next</button>
                    <button type="submit" id="submit-btn" class="submit-btn" style="display: none">Submit Survey</button>
                </div>
            </form>
        `;

        this.container.innerHTML = html;
        this.attachEventListeners();
        this.updateProgress();
    }

    renderQuestion(q) {
        let inputHtml = '';
        const name = `question_${q.id}`;

        if (q.type === 'radio') {
            inputHtml = q.choices.map(choice => `
                <label class="radio-label" data-choice-id="${choice.id}">
                    <input type="radio" name="${name}" value="${choice.value}" data-question-id="${q.id}" data-choice-id="${choice.id}">
                    <span class="radio-custom"></span>
                    <span class="choice-text">${choice.label}</span>
                </label>
            `).join('');
        } else if (q.type === 'dropdown') {
            inputHtml = `
                <div class="select-wrapper">
                    <select name="${name}" data-question-id="${q.id}" class="survey-select">
                        <option value="" disabled selected>Select an option</option>
                        ${q.choices.map(choice => `
                            <option value="${choice.value}" data-choice-id="${choice.id}">${choice.label}</option>
                        `).join('')}
                    </select>
                </div>
            `;
        } else if (q.type === 'number') {
            inputHtml = `
                <input type="number" name="${name}" data-question-id="${q.id}" class="survey-input" placeholder="Enter a number">
            `;
        } else if (q.type === 'date') {
            inputHtml = `
                <input type="date" name="${name}" data-question-id="${q.id}" class="survey-input">
            `;
        } else if (q.type === 'checkbox') {
            inputHtml = q.choices.map(choice => `
                <label class="radio-label" data-choice-id="${choice.id}">
                    <input type="checkbox" name="${name}" value="${choice.value}" data-question-id="${q.id}" data-choice-id="${choice.id}">
                    <span class="checkbox-custom"></span>
                    <span class="choice-text">${choice.label}</span>
                </label>
            `).join('');
        } else {
            inputHtml = `
                <input type="text" name="${name}" data-question-id="${q.id}" class="survey-input" placeholder="Your answer">
            `;
        }

        return `
            <div class="question-wrapper" id="q-wrapper-${q.id}" data-question-id="${q.id}">
                <label class="question-text">${q.text}</label>
                <div class="input-container">
                    ${inputHtml}
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        const form = document.getElementById('survey-form');
        form.addEventListener('change', (e) => {
            const target = e.target;
            const qId = target.dataset.questionId;
            if (qId) {
                let value = target.value;
                if (target.type === 'checkbox') {
                    const checked = form.querySelectorAll(`input[name="${target.name}"]:checked`);
                    value = Array.from(checked).map(cb => cb.value);
                }
                this.updateValue(qId, value);
                this.handleTriggers(qId);
            }
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = document.getElementById('submit-btn');
            const originalText = submitBtn.innerText;
            submitBtn.disabled = true;
            submitBtn.innerText = 'Submitting...';
            try {
                await this.saveProgress(true);
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerText = originalText;
            }
        });

        document.getElementById('next-btn').addEventListener('click', async () => {
            const nextBtn = document.getElementById('next-btn');
            const originalText = nextBtn.innerText;
            nextBtn.disabled = true;
            nextBtn.innerText = 'Saving...';
            try {
                await this.saveProgress();
                this.nextStep();
            } finally {
                nextBtn.disabled = false;
                nextBtn.innerText = originalText;
            }
        });

        document.getElementById('prev-btn').addEventListener('click', () => {
            this.prevStep();
        });

        const stepsList = document.getElementById('steps-list');
        if (stepsList) {
            stepsList.addEventListener('click', (e) => {
                const stepItem = e.target.closest('.step-item');
                if (stepItem) {
                    const stepIndex = parseInt(stepItem.dataset.step);
                    this.goToStep(stepIndex);
                }
            });
        }
    }

    goToStep(index) {
        if (index >= 0 && index < this.sections.length) {
            this.currentStep = index;
            this.updateStepVisibility();
        }
    }

    nextStep() {
        if (this.currentStep < this.sections.length - 1) {
            this.currentStep++;
            this.updateStepVisibility();
        }
    }

    prevStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.updateStepVisibility();
        }
    }

    updateStepVisibility() {
        const steps = document.querySelectorAll('.survey-section');
        steps.forEach((step, index) => {
            step.style.display = index === this.currentStep ? 'block' : 'none';
        });

        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const submitBtn = document.getElementById('submit-btn');

        if (prevBtn) prevBtn.style.display = this.currentStep === 0 ? 'none' : 'block';

        if (this.currentStep === this.sections.length - 1) {
            if (nextBtn) nextBtn.style.display = 'none';
            if (submitBtn) submitBtn.style.display = 'block';
        } else {
            if (nextBtn) nextBtn.style.display = 'block';
            if (submitBtn) submitBtn.style.display = 'none';
        }

        this.updateProgress();
        this.updateSidebarState();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    updateProgress() {
        const progressFill = document.getElementById('progress-fill');
        if (progressFill) {
            const progress = ((this.currentStep + 1) / this.sections.length) * 100;
            progressFill.style.width = `${progress}%`;
        }
    }

    updateValue(qId, value) {
        this.formValues[qId] = value;
        this.updateSidebarState();
    }

    handleTriggers(triggerId) {
        const targets = this.surveyData.trigger_map[triggerId];
        if (!targets) return;

        targets.forEach(targetId => {
            this.evaluateLogic(targetId);
        });
    }

    evaluateLogic(targetId) {
        const targetIdStr = String(targetId);
        const rules = this.surveyData.logic_map[targetIdStr];
        if (!rules) return;

        const question = this.surveyData.questions_map[targetIdStr];
        const wrapper = document.getElementById(`q-wrapper-${targetIdStr}`);
        if (!question || !wrapper) return;

        const hasShowRules = rules.some(r => r.action === 'show');
        let showMatched = false;
        let hideMatched = false;
        let allowedChoiceIds = null;

        rules.forEach(rule => {
            const triggerValue = this.formValues[String(rule.trigger_question)];
            const isMatch = this.checkCondition(triggerValue, rule.operator, rule.value);

            if (isMatch) {
                switch (rule.action) {
                    case 'show':
                        showMatched = true;
                        break;
                    case 'hide':
                        hideMatched = true;
                        break;
                    case 'limit_choices':
                    case 'include_choices':
                        if (allowedChoiceIds === null) allowedChoiceIds = new Set();
                        (rule.target_choices || []).forEach(id => allowedChoiceIds.add(Number(id)));
                        break;
                    case 'exclude_choices':
                        if (allowedChoiceIds === null) {
                            allowedChoiceIds = new Set(question.choices.map(c => Number(c.id)));
                        }
                        (rule.target_choices || []).forEach(id => allowedChoiceIds.delete(Number(id)));
                        break;
                }
            }
        });

        const shouldShow = hasShowRules ? (showMatched && !hideMatched) : !hideMatched;
        wrapper.style.display = shouldShow ? 'block' : 'none';
        wrapper.classList.toggle('hidden', !shouldShow);

        if (['radio', 'dropdown', 'checkbox'].includes(question.type)) {
            if (allowedChoiceIds !== null) {
                const choiceList = Array.from(allowedChoiceIds);
                this.filterChoices(targetIdStr, choiceList);
            } else {
                this.resetChoices(targetIdStr);
            }
        }
        this.updateSidebarState();
    }

    checkCondition(val1, operator, val2) {
        if (val1 === undefined || val1 === null) return false;
        const v1 = String(val1).toLowerCase().trim();
        const v2 = String(val2).toLowerCase().trim();

        switch (operator) {
            case 'eq': return v1 == v2;
            case 'neq': return v1 != v2;
            case 'gt': return parseFloat(v1) > parseFloat(v2);
            case 'lt': return parseFloat(v1) < parseFloat(v2);
            case 'contains': return v1.includes(v2);
            default: return false;
        }
    }

    filterChoices(qId, allowedChoiceIds) {
        const wrapper = document.getElementById(`q-wrapper-${qId}`);
        const allowed = allowedChoiceIds.map(id => Number(id));

        const radioLabels = wrapper.querySelectorAll('.radio-label');
        radioLabels.forEach(label => {
            const choiceId = Number(label.dataset.choiceId);
            const isAllowed = allowed.includes(choiceId);
            label.style.display = isAllowed ? 'flex' : 'none';
            label.classList.toggle('hidden', !isAllowed);

            const input = label.querySelector('input');
            if (!isAllowed && input && input.checked) {
                input.checked = false;
                this.updateValue(qId, null);
            }
        });

        const select = wrapper.querySelector('select');
        if (select) {
            Array.from(select.options).forEach(option => {
                if (option.value === "") return;
                const choiceId = Number(option.dataset.choiceId);
                const isAllowed = allowed.includes(choiceId);

                option.hidden = !isAllowed;
                option.disabled = !isAllowed;
                option.style.display = isAllowed ? 'block' : 'none';

                if (!isAllowed && select.value === option.value) {
                    select.value = "";
                    this.updateValue(qId, null);
                }
            });
        }
    }

    resetChoices(qId) {
        const wrapper = document.getElementById(`q-wrapper-${qId}`);
        if (!wrapper) return;
        const radioLabels = wrapper.querySelectorAll('.radio-label');
        radioLabels.forEach(label => label.classList.remove('hidden'));

        const select = wrapper.querySelector('select');
        if (select) {
            Array.from(select.options).forEach(option => {
                option.hidden = false;
                option.disabled = false;
            });
        }
    }

    applyInitialLogic() {
        Object.keys(this.surveyData.logic_map).forEach(targetId => {
            this.evaluateLogic(targetId);
        });
    }

    renderSidebar() {
        const stepsList = document.getElementById('steps-list');
        if (!stepsList) return;

        stepsList.innerHTML = this.sections.map((section, index) => `
            <div class="step-item" id="sidebar-step-${index}" data-step="${index}">
                <div class="step-number">
                    <span class="step-label-num">${index + 1}</span>
                </div>
                <div class="step-label">${section.title}</div>
            </div>
        `).join('');
        this.updateSidebarState();
    }

    updateSidebarState() {
        if (!this.sections.length) return;

        const sidebarTitle = document.querySelector('.sidebar-title');
        if (sidebarTitle) {
            const label = this.language === 'ar' ? 'الأقسام' : 'Sections';
            sidebarTitle.innerHTML = `${label} <span style="float: right; opacity: 0.6;">${this.currentStep + 1} / ${this.sections.length}</span>`;
        }

        this.sections.forEach((section, index) => {
            const sidebarItem = document.getElementById(`sidebar-step-${index}`);
            if (sidebarItem) {
                sidebarItem.classList.toggle('active', index === this.currentStep);

                const isCompleted = section.questions.every(q => {
                    const wrapper = document.getElementById(`q-wrapper-${q.id}`);
                    const isHidden = wrapper && (wrapper.style.display === 'none' || wrapper.classList.contains('hidden'));
                    if (isHidden) return true;

                    const val = this.formValues[q.id];
                    return val !== undefined && val !== null && val !== '';
                });

                sidebarItem.classList.toggle('completed', isCompleted);
            }
        });
    }
}
